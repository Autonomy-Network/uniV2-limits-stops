pragma solidity ^0.8;


import "../interfaces/IUniswapV2Router02.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


// TODO: get returned data from calls, so if they revert, can pass on the reason
// TODO: add safeTransfer

contract UniV2LimitsStops is Ownable {

    address payable private immutable _registry;
    address private immutable _userVeriForwarder;
    address private immutable _userGasVeriForwarder;
    FeeInfo private _defaultFeeInfo;
    uint256 private constant MAX_UINT = type(uint256).max;


    constructor(
        address payable registry,
        address userVeriForwarder,
        address userGasVeriForwarder,
        FeeInfo memory defaultFeeInfo
    ) Ownable() {
        _registry = registry;
        _userVeriForwarder = userVeriForwarder;
        _userGasVeriForwarder = userGasVeriForwarder;
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
        address to,
        uint deadline
    ) external payable userGasVerified {
        _ethToTokenLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            _defaultFeeInfo,
            amountOutMin,
            path,
            to,
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
        address to,
        uint deadline
    ) external payable userGasVerified {
        _ethToTokenLimitOrderPaySpecific(
            user,
            feeAmount,
            uni,
            feeInfo,
            amountOutMin,
            path,
            to,
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
        address to,
        uint deadline
    ) private {
        // Pay the execution fee
        uint inputSpentOnFee;
        if (feeInfo.isAUTO) {
            feeInfo.path[0] = path[0];
            inputSpentOnFee = feeInfo.uni.swapETHForExactTokens{value: msg.value}(feeAmount, feeInfo.path, user, deadline)[0];
        } else {
            _registry.transfer(feeAmount);
            inputSpentOnFee = feeAmount;
        }

        // Reduce amountOutMin proportionally so that the price of execution is the same
        // as what was intended by the user. Generally we take the execution fee after the trade.
        // This is done so that the trade executes at the price intended by the user, even though
        // they'll receive less than if that'd market bought/sold at that price (because they pay
        // for the execution in regular ETH tx fees). The naive way is to do the trade, then take
        // the output token, and trade some of that for whatever the fee is paid in - this will
        // execute at the intended price, but is gas inefficient because it then requires sending
        // the tokens manually here, rather than inputing the recipient into the Uniswap trade.
        // Instead, we can send the fee out of the Uniswap trade directly, or directly with ETH,
        // and reduce amountOutMin proportionally to retain the same execution price (amount in
        // is reduced, and so amountOutMin has to be reduced proportionally)
        // Can't do `tradeInput = (msg.value - inputSpentOnFee)` because of stack too deep
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
        IERC20 token = approveUnapproved(uni, path[0], inputAmount);
        token.transferFrom(user, address(this), inputAmount);
        uni.swapExactTokensForETH(inputAmount, amountOutMin, path, to, deadline);
    }

    // function ethToTokenLimitOrderPayDefault(
    //     address user,
    //     uint feeAmount,
    //     IUniswapV2Router02 uni,
    //     uint amountOutMin,
    //     address[] calldata path,
    //     address to,
    //     uint deadline
    // ) external userGasVerified {
    //     _ethToTokenLimitOrderPaySpecific(
    //         user,
    //         feeAmount,
    //         uni,
    //         _defaultFeeInfo,
    //         amountOutMin,
    //         path,
    //         to,
    //         deadline
    //     );
    // }

    // function ethToTokenLimitOrderPaySpecific(
    //     address user,
    //     uint feeAmount,
    //     IUniswapV2Router02 uni,
    //     FeeInfo memory feeInfo,
    //     uint amountOutMin,
    //     address[] calldata path,
    //     address to,
    //     uint deadline
    // ) external userGasVerified {
    //     _ethToTokenLimitOrderPaySpecific(
    //         user,
    //         feeAmount,
    //         uni,
    //         feeInfo,
    //         amountOutMin,
    //         path,
    //         to,
    //         deadline
    //     );
    // }

    // function _tokenToEthLimitOrderPaySpecific(
    //     address user,
    //     uint feeAmount,
    //     IUniswapV2Router02 uni,
    //     FeeInfo memory feeInfo,
    //     uint inputAmount,
    //     uint amountOutMin,
    //     address[] calldata path,
    //     address to,
    //     uint deadline
    // ) private {
    //     // Pay the execution fee
    //     uint inputSpentOnFee;
    //     if (feeInfo.isAUTO) {
    //         if (path[0] == feeInfo.path[feeInfo.path.length-1]) {
    //             // The user already holds inputAmount of AUTO
    //             inputSpentOnFee = feeAmount;
    //         } else {
    //             feeInfo.path[0] = path[0];
    //             inputSpentOnFee = feeInfo.uni.swapTokensForExactTokens(feeAmount, inputAmount, feeInfo.path, user, deadline)[0];
    //         }
    //     } else {
    //         feeInfo.path[0] = path[0];
    //         inputSpentOnFee = feeInfo.uni.swapTokensForExactTokens(feeAmount, inputAmount, feeInfo.path, user, deadline)[0];
            
    //         inputSpentOnFee = feeAmount;
    //     }

    //     // Reduce amountOutMin proportionally so that the price of execution is the same
    //     // as what was intended by the user. Generally we take the execution fee after the trade.
    //     // This is done so that the trade executes at the price intended by the user, even though
    //     // they'll receive less than if that'd market bought/sold at that price (because they pay
    //     // for the execution in regular ETH tx fees). The naive way is to do the trade, then take
    //     // the output token, and trade some of that for whatever the fee is paid in - this will
    //     // execute at the intended price, but is gas inefficient because it then requires sending
    //     // the tokens manually here, rather than inputing the recipient into the Uniswap trade.
    //     // Instead, we can send the fee out of the Uniswap trade directly, or directly with ETH,
    //     // and reduce amountOutMin proportionally to retain the same execution price (amount in
    //     // is reduced, and so amountOutMin has to be reduced proportionally)
    //     // Can't do `tradeInput = (msg.value - inputSpentOnFee)` because of stack too deep
    //     uni.swapExactETHForTokens{value: (msg.value - inputSpentOnFee)}(
    //         amountOutMin * (msg.value - inputSpentOnFee) / msg.value,
    //         path,
    //         user,
    //         deadline
    //     );
    // }






















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

    function getRegistry() external view returns (address) {
        return _registry;
    }

    function getUserVerifiedForwarder() external view returns (address) {
        return _userVeriForwarder;
    }

    function getUserFeeVerifiedForwarder() external view returns (address) {
        return _userGasVeriForwarder;
    }

    function getDefaultFeeInfo() external view returns (FeeInfo memory) {
        return _defaultFeeInfo;
    }

    function setDefaultFeeInfo(FeeInfo calldata newDefaultFee) external onlyOwner {
        _defaultFeeInfo = newDefaultFee;
    }

    modifier userVerified() {
        require(msg.sender == _userVeriForwarder, "LimitsStops: not userForw");
        _;
    }

    modifier userGasVerified() {
        require(msg.sender == _userGasVeriForwarder, "LimitsStops: not userGasForw");
        _;
    }

    // Needed to receive excess ETH when calling swapETHForExactTokens
    receive() external payable {}
}