pragma solidity ^0.8;


import "../interfaces/IUniswapV2Router02.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


// TODO: get returned data from calls, so if they revert, can pass on the reason
// TODO: add safeTransfer
// TODO: add withdraw for ERC20s for fools who send tokens to this contract

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


contract UniV2LimitsStops is Ownable {

    address payable public immutable registry;
    address public immutable userVeriForwarder;
    address public immutable userFeeVeriForwarder;
    address public immutable WETH;
    FeeInfo private _defaultFeeInfo;
    uint256 private constant MAX_UINT = type(uint256).max;


    constructor(
        address payable registry_,
        address userVeriForwarder_,
        address userFeeVeriForwarder_,
        address WETH_,
        FeeInfo memory defaultFeeInfo
    ) Ownable() {
        registry = registry_;
        userVeriForwarder = userVeriForwarder_;
        userFeeVeriForwarder = userFeeVeriForwarder_;
        WETH = WETH_;
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
        bool isAUTO;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                 ETH to token limit orders                //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function ethToTokenLimitOrder(
        IUniswapV2Router02 uni,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable {
        uni.swapExactETHForTokens{value: msg.value}(amountOutMin, path, to, deadline);
    }

    function ethToTokenLimitOrderPayDefault(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) external payable userFeeVerified {
        FeeInfo memory feeInfo = _defaultFeeInfo;
        if (feeInfo.isAUTO) {
            feeInfo.path[0] = WETH;
        }

        _ethToTokenLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            amountOutMin,
            path,
            deadline
        );
    }

    function ethToTokenLimitOrderPaySpecific(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) external payable userFeeVerified {
        _ethToTokenLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            amountOutMin,
            path,
            deadline
        );
    }

    function _ethToTokenLimitOrderPaySpecific(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) private {
        // Pay the execution fee
        uint inputSpentOnFee;
        if (feeInfo.isAUTO) {
            inputSpentOnFee = feeInfo.uni.swapETHForExactTokens{value: msg.value}(feeAmount, feeInfo.path, user, deadline)[0];
        } else {
            registry.transfer(feeAmount);
            inputSpentOnFee = feeAmount;
        }

        // *1, *2
        uni.swapExactETHForTokens{value: (msg.value - inputSpentOnFee)}(
            amountOutMin * (msg.value - inputSpentOnFee) / msg.value,
            path,
            user,
            deadline
        );
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                 Token to ETH limit orders                //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function tokenToEthLimitOrder(
        address payable user,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external userVerified {
        // IERC20 token = approveUnapproved(uni, path[0], inputAmount);
        // token.transferFrom(user, address(this), inputAmount);
        transferApproveUnapproved(uni, path[0], inputAmount, user);
        uni.swapExactTokensForETH(inputAmount, amountOutMin, path, to, deadline);
    }

    function tokenToEthLimitOrderPayDefault(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) external userFeeVerified {
        FeeInfo memory feeInfo = _defaultFeeInfo;
        // The fee path only needs to be modified when not paying in ETH (since
        // the output of the trade is ETH and that can be used) and when the input
        // token isn't AUTO anyway (since that can be used without a 2nd trade)
        if (feeInfo.isAUTO && path[0] != feeInfo.path[feeInfo.path.length-1]) {
            address[] memory newFeePath = new address[](3);
            newFeePath[0] = path[0];               // src token
            newFeePath[1] = WETH;   // WETH_ since path in tokenToETH ends in WETH_
            newFeePath[2] = feeInfo.path[feeInfo.path.length-1];   // AUTO since feePath here ends in AUTO
            feeInfo.path = newFeePath;
        }
        
        _tokenToEthLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            inputAmount,
            amountOutMin,
            path,
            deadline
        );
    }

    function tokenToEthLimitOrderPaySpecific(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) external userFeeVerified {
        _tokenToEthLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            inputAmount,
            amountOutMin,
            path,
            deadline
        );
    }

    function _tokenToEthLimitOrderPaySpecific(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) private {
        // Pay the execution fee
        uint inputSpentOnFee;
        if (feeInfo.isAUTO) {
            // If the src token is AUTO
            if (path[0] == feeInfo.path[feeInfo.path.length-1]) {
                // The user already holds inputAmount of AUTO, so don't move them
                inputSpentOnFee = feeAmount;
                transferApproveUnapproved(uni, path[0], (inputAmount - inputSpentOnFee), user);
            } else {
                transferApproveUnapproved(uni, path[0], inputAmount, user);
                approveUnapproved(feeInfo.uni, path[0], inputAmount);
                inputSpentOnFee = feeInfo.uni.swapTokensForExactTokens(feeAmount, inputAmount, feeInfo.path, user, deadline)[0];
            }
        } else {
            transferApproveUnapproved(uni, path[0], inputAmount, user);
        }

        // *1, *2
        uni.swapExactTokensForETH(
            (inputAmount - inputSpentOnFee),
            amountOutMin * (inputAmount - inputSpentOnFee) / inputAmount,
            path,
            // Sending it all to the registry means that the fee will be kept
            // (if it's in ETH) and the excess sent to the user
            feeInfo.isAUTO ? user : registry,
            deadline
        );
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                 Token to token limit orders              //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function tokenToTokenLimitOrder(
        address payable user,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external userVerified {
        IERC20 token = approveUnapproved(uni, path[0], inputAmount);
        token.transferFrom(user, address(this), inputAmount);
        uni.swapExactTokensForTokens(inputAmount, amountOutMin, path, to, deadline);
    }

    function tokenToTokenLimitOrderPayDefault(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) external userFeeVerified {
        FeeInfo memory feeInfo = _defaultFeeInfo;
        // The fee path only needs to be modified when the src/dest tokens aren't
        // AUTO (if paying in AUTO), and when paying in ETH
        if (feeInfo.isAUTO && path[0] != feeInfo.path[feeInfo.path.length-1]) {
            address[] memory newFeePath = new address[](3);
            newFeePath[0] = path[0];                // src token
            newFeePath[1] = WETH;                  // WETH_ since path in tokenToETH ends in WETH_
            newFeePath[2] = feeInfo.path[feeInfo.path.length-1];   // AUTO since feePath here ends in AUTO
            feeInfo.path = newFeePath;
        } else if (!feeInfo.isAUTO) {
            feeInfo.path[0] = path[0];
        }

        _tokenToTokenLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            inputAmount,
            amountOutMin,
            path,
            deadline
        );
    }

    function tokenToTokenLimitOrderPaySpecific(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) external userFeeVerified {
        _tokenToTokenLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            inputAmount,
            amountOutMin,
            path,
            deadline
        );
    }

    function _tokenToTokenLimitOrderPaySpecific(
        address user,
        uint feeAmount,
        IUniswapV2Router02 uni,
        FeeInfo memory feeInfo,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        uint deadline
    ) private {
        // Pay the execution fee
        uint inputSpentOnFee;
        if (feeInfo.isAUTO) {
            // If the src token is AUTO
            if (path[0] == feeInfo.path[feeInfo.path.length-1]) {
                // The user already holds inputAmount of AUTO
                inputSpentOnFee = feeAmount;
                transferApproveUnapproved(uni, path[0], (inputAmount - inputSpentOnFee), user);
            // If the dest token is AUTO
            } else if (path[path.length-1] == feeInfo.path[feeInfo.path.length-1]) {
                // Do nothing because it'll all get sent to the user, and the
                // fee will be taken from them after that
                transferApproveUnapproved(uni, path[0], inputAmount, user);
            } else {
                transferApproveUnapproved(uni, path[0], inputAmount, user);
                approveUnapproved(feeInfo.uni, path[0], inputAmount);
                inputSpentOnFee = feeInfo.uni.swapTokensForExactTokens(feeAmount, inputAmount, feeInfo.path, user, deadline)[0];
            }
        } else {
            transferApproveUnapproved(uni, path[0], inputAmount, user);
            approveUnapproved(feeInfo.uni, path[0], inputAmount);
            inputSpentOnFee = feeInfo.uni.swapTokensForExactETH(feeAmount, inputAmount, feeInfo.path, registry, deadline)[0];
        }

        // *1, *2
        uni.swapExactTokensForTokens(
            (inputAmount - inputSpentOnFee),
            amountOutMin * (inputAmount - inputSpentOnFee) / inputAmount,
            path,
            user,
            deadline
        );
    }
























    function ethToTokenStopLoss(
        IUniswapV2Router02 uni,
        uint amountOutMin,
        uint amountOutMax,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable {
        uint[] memory amounts = uni.swapExactETHForTokens{value: msg.value}(amountOutMin, path, to, deadline);
        require(amounts[amounts.length-1] <= amountOutMax, "LimitsStops: price too high");
    }

    function tokenToEthStopLoss(
        address payable user,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        uint amountOutMax,
        address[] calldata path,
        address to,
        uint deadline
    ) external userVerified {
        IERC20 token = approveUnapproved(uni, path[0], inputAmount);
        token.transferFrom(user, address(this), inputAmount);
        uint[] memory amounts = uni.swapExactTokensForETH(inputAmount, amountOutMin, path, to, deadline);
        require(amounts[amounts.length-1] <= amountOutMax, "LimitsStops: price too high");
    }

    function tokenToTokenStopLoss(
        address payable user,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        uint amountOutMax,
        address[] calldata path,
        address to,
        uint deadline
    ) external userVerified {
        IERC20 token = approveUnapproved(uni, path[0], inputAmount);
        token.transferFrom(user, address(this), inputAmount);
        uint[] memory amounts = uni.swapExactTokensForTokens(inputAmount, amountOutMin, path, to, deadline);
        require(amounts[amounts.length-1] <= amountOutMax, "LimitsStops: price too high");
    }




    function approveUnapproved(IUniswapV2Router02 uni, address tokenAddr, uint amount) private returns (IERC20 token) {
        token = IERC20(tokenAddr);
        if (token.allowance(address(this), address(uni)) < amount) {
            token.approve(address(uni), MAX_UINT);
        }
    }

    function transferApproveUnapproved(IUniswapV2Router02 uni, address tokenAddr, uint amount, address user) private {
        IERC20 token = approveUnapproved(uni, tokenAddr, amount);
        token.transferFrom(user, address(this), amount);
    }

    function setDefaultFeeInfo(FeeInfo calldata newDefaultFee) external onlyOwner {
        _defaultFeeInfo = newDefaultFee;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Getters                         //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function getDefaultFeeInfo() external view returns (FeeInfo memory) {
        return _defaultFeeInfo;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Modifiers                       //
    //                                                          //
    //////////////////////////////////////////////////////////////

    modifier userVerified() {
        require(msg.sender == userVeriForwarder, "LimitsStops: not userForw");
        _;
    }

    modifier userFeeVerified() {
        require(msg.sender == userFeeVeriForwarder, "LimitsStops: not userFeeForw");
        _;
    }

    // Needed to receive excess ETH when calling swapETHForExactTokens
    receive() external payable {}
}