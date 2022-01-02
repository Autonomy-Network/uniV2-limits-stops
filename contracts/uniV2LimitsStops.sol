pragma solidity 0.8.6;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/IUniswapV2Router02.sol";


// Comments referenced throughout
// *1:
// Reduce amountOutMin proportionally so that the price of execution is the same
// as what was intended by the user. This is done so that the trade executes at
// the price intended by the user, even though they'll receive less than if
// that'd market bought/sold at that price (because they pay for the execution
// in regular ETH tx fees with normal Uniswap market orders). The naive way is
// to do the trade, then take the output token, and trade some of that for
// whatever the fee is paid in - this will execute at the intended price, but
// is gas inefficient because it then requires sending the output tokens here
// (and then requiring an additional transfer to the user), rather than inputing
// the recipient into the Uniswap trade. Instead, we can have 2 Uniswap trades
// (in the worst case scenario where the fee token isn't one of the traded tokens)
// that sends the fee in the 1st, and reduce amountOutMin in the 2nd proportional
// to the fees spent, such that the total execution price is the same as what was
// intended by the user, even though there are fewer input tokens to spend on the
// trade
// *2:
// Can't do `tradeInput = (inputAmount - inputSpentOnFee)` because of stack too deep


/**
* @title    UniV2LimitsStops
* @notice   Wraps around an arbitrary UniV2 router contract and adds conditions
*           of price to create limit orders and stop losses. Ensures that
*           only a specific user can call a trade because the Autonomy Registry
*           forces that the first argument of the calldata is the user's address
*           and this contract knows that condition is true when the call is coming
*           from an appropriate proxy
* @author   Quantaf1re (James Key)
*/
contract UniV2LimitsStops is Ownable {

    using SafeERC20 for IERC20;

    address payable public immutable registry;
    address public immutable userVeriForwarder;
    address public immutable userFeeVeriForwarder;
    address public immutable CELO;
    FeeInfo private _defaultFeeInfo;
    uint256 private constant MAX_UINT = type(uint256).max;


    constructor(
        address payable registry_,
        address userVeriForwarder_,
        address userFeeVeriForwarder_,
        address CELO_,
        FeeInfo memory defaultFeeInfo
    ) Ownable() {
        registry = registry_;
        userVeriForwarder = userVeriForwarder_;
        userFeeVeriForwarder = userFeeVeriForwarder_;
        CELO = CELO_;
        _defaultFeeInfo = defaultFeeInfo;
    }


    struct FeeInfo {
        // Need a known instance of UniV2 that is guaranteed to have the token
        // that the default fee is paid in, along with enough liquidity, since
        // an arbitrary instance of UniV2 is passed to fcns in this contract
        IUniswapV2Router02 uni;
        address[] path;
        // Whether or not the fee token is AUTO, because that needs to
        // get sent to the user, since `transferFrom` is used from them directly
        // in the Registry to charge the fee
        bool isAUTO;
    }

    // Hold arguments for calling Uniswap to avoid stack to deep errors
    struct UniArgs{
        uint inputAmount;
        uint amountOutMin;
        uint amountOutMax;
        address[] path;
        uint deadline;
    }


    //////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////
    ////                                                          ////
    ////----------------------Token to token----------------------////
    ////                                                          ////
    //////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////

    /**
     * @notice  Only calls swapExactTokensForTokens if the output is above
     *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
     *          is the 'stop price' when used as a stop loss, and
     *          `amountOutMin` is the 'limit price' when used as a limit
     *          order. When using this as a classic limit order, `amountOutMax`
     *          would be sent to the max uint value. When using this
     *          as a classic stop loss, `amountOutMin` would be set to 0.
     *          The min/max can also be used to limit downside during flash
     *          crashes, e.g. `amountOutMin` could be set to 10% lower then
     *          `amountOutMax` for a stop loss, if desired.
     */
    function tokenToTokenRange(
        address user,
        uint maxGasPrice,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        uint amountOutMax,
        address[] calldata path,
        address to,
        uint deadline
    ) external gasPriceCheck(maxGasPrice) userVerified {
        transferApproveUnapproved(uni, path[0], inputAmount, user);
        uint[] memory amounts = uni.swapExactTokensForTokens(inputAmount, amountOutMin, path, to, deadline);
        require(amounts[amounts.length-1] <= amountOutMax, "LimitsStops: price too high");
    }

    function _tokenToTokenPayDefault(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        UniArgs memory uniArgs
    ) private {
        FeeInfo memory feeInfo = _defaultFeeInfo;
        // Assuming there's no AUTO token for now
        if (!feeInfo.isAUTO) {
            feeInfo.path[0] = uniArgs.path[0];
        }

        _tokenToTokenPaySpecific(user, feeAmount, uni, feeInfo, uniArgs);
    }

    function _tokenToTokenPaySpecific(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        UniArgs memory uniArgs
    ) private {
        // Pay the execution fee
        uint tradeInput = uniArgs.inputAmount;
        address receiver = user;
        if (feeInfo.isAUTO) {
            // If the src token is AUTO
            if (uniArgs.path[0] == feeInfo.path[feeInfo.path.length-1]) {
                tradeInput -= feeAmount;
                transferApproveUnapproved(uni, uniArgs.path[0], tradeInput, user);
            // If the dest token is AUTO
            } else if (uniArgs.path[uniArgs.path.length-1] == feeInfo.path[feeInfo.path.length-1]) {
                // Do nothing because it'll all get sent to the user, and the
                // fee will be taken from them after that
                transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
            } else {
                transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
                approveUnapproved(feeInfo.uni, uniArgs.path[0], uniArgs.inputAmount);
                tradeInput -= feeInfo.uni.swapTokensForExactTokens(feeAmount, uniArgs.inputAmount, feeInfo.path, user, uniArgs.deadline)[0];
            }
        } else {
            // If the src token is CELO
            if (uniArgs.path[0] == feeInfo.path[feeInfo.path.length-1]) {
                tradeInput -= feeAmount;
                transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
                // If the fee is in CELO, it needs to be sent to the Registry
                registry.transfer(feeAmount);
            // If the dest token is CELO
            } else if (uniArgs.path[uniArgs.path.length-1] == feeInfo.path[feeInfo.path.length-1]) {
                // Do nothing because it'll all get sent to the Registry, and the excess sent back to the user
                transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
                receiver = registry;
            } else {
                transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
                approveUnapproved(feeInfo.uni, uniArgs.path[0], uniArgs.inputAmount);
                tradeInput -= feeInfo.uni.swapTokensForExactTokens(feeAmount, uniArgs.inputAmount, feeInfo.path, user, uniArgs.deadline)[0];
            }
        }

        // *1, *2
        uint[] memory amounts = uni.swapExactTokensForTokens(
            tradeInput,
            uniArgs.amountOutMin * tradeInput / uniArgs.inputAmount,
            uniArgs.path,
            receiver,
            uniArgs.deadline
        );
        require(amounts[amounts.length-1] <= uniArgs.amountOutMax * tradeInput / uniArgs.inputAmount, "LimitsStops: price too high");
    }

    /**
     * @notice  Only calls swapExactTokensForTokens if the output is above
     *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
     *          is the 'stop price' when used as a stop loss, and
     *          `amountOutMin` is the 'limit price' when used as a limit
     *          order. When using this as a classic limit order, `amountOutMax`
     *          would be sent to the max uint value. When using this
     *          as a classic stop loss, `amountOutMin` would be set to 0.
     *          The min/max can also be used to limit downside during flash
     *          crashes, e.g. `amountOutMin` could be set to 10% lower then
     *          `amountOutMax` for a stop loss, if desired. Additionally, 
     *          takes part of the trade and uses it to pay `feeAmount`,
     *          in the default fee token, to the registry
     */
    function tokenToTokenRangePayDefault(
        address user,
        uint feeAmount,
        uint maxGasPrice,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        uint amountOutMax,
        address[] calldata path,
        uint deadline
    ) external gasPriceCheck(maxGasPrice) userFeeVerified {
        _tokenToTokenPayDefault(
            user,
            feeAmount,
            uni,
            UniArgs(inputAmount, amountOutMin, amountOutMax, path, deadline)
        );
    }

    /**
     * @notice  Only calls swapExactTokensForTokens if the output is above
     *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
     *          is the 'stop price' when used as a stop loss, and
     *          `amountOutMin` is the 'limit price' when used as a limit
     *          order. When using this as a classic limit order, `amountOutMax`
     *          would be sent to the max uint value. When using this
     *          as a classic stop loss, `amountOutMin` would be set to 0.
     *          The min/max can also be used to limit downside during flash
     *          crashes, e.g. `amountOutMin` could be set to 10% lower then
     *          `amountOutMax` for a stop loss, if desired. Additionally, 
     *          takes part of the trade and uses it to pay `feeAmount`,
     *          in the specified fee token, to the registry.
     *          WARNING: only use this if you want to do things non-standard
     */
    function tokenToTokenRangePaySpecific(
        address user,
        uint feeAmount,
        uint maxGasPrice,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        uint inputAmount,
        uint amountOutMin,
        uint amountOutMax,
        address[] calldata path,
        uint deadline
    ) external gasPriceCheck(maxGasPrice) userFeeVerified {
        _tokenToTokenPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            UniArgs(inputAmount, amountOutMin, amountOutMax, path, deadline)
        );
    }


    //////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////
    ////                                                          ////
    ////-------------------------Helpers--------------------------////
    ////                                                          ////
    //////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////

    function approveUnapproved(IUniswapV2Router02 uni, address tokenAddr, uint amount) private returns (IERC20 token) {
        token = IERC20(tokenAddr);
        if (token.allowance(address(this), address(uni)) < amount) {
            token.approve(address(uni), MAX_UINT);
        }
    }

    function transferApproveUnapproved(IUniswapV2Router02 uni, address tokenAddr, uint amount, address user) private {
        IERC20 token = approveUnapproved(uni, tokenAddr, amount);
        token.safeTransferFrom(user, address(this), amount);
    }

    function setDefaultFeeInfo(FeeInfo calldata newDefaultFee) external onlyOwner {
        _defaultFeeInfo = newDefaultFee;
    }

    function getDefaultFeeInfo() external view returns (FeeInfo memory) {
        return _defaultFeeInfo;
    }

    modifier userVerified() {
        require(msg.sender == userVeriForwarder, "LimitsStops: not userForw");
        _;
    }

    modifier userFeeVerified() {
        require(msg.sender == userFeeVeriForwarder, "LimitsStops: not userFeeForw");
        _;
    }

    modifier gasPriceCheck(uint maxGasPrice) {
        require(tx.gasprice <= maxGasPrice, "LimitsStops: gasPrice too high");
        _;
    }

    // Needed to receive excess ETH when calling swapETHForExactTokens
    receive() external payable {}
}