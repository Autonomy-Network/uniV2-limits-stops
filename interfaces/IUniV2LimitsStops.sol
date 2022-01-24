// pragma solidity 0.8.6;


// import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
// import "../interfaces/IUniswapV2Router02.sol";


// // Comments referenced throughout
// // *1:
// // Reduce amountOutMin proportionally so that the price of execution is the same
// // as what was intended by the user. This is done so that the trade executes at
// // the price intended by the user, even though they'll receive less than if
// // that'd market bought/sold at that price (because they pay for the execution
// // in regular ETH tx fees with normal Uniswap market orders). The naive way is
// // to do the trade, then take the output token, and trade some of that for
// // whatever the fee is paid in - this will execute at the intended price, but
// // is gas inefficient because it then requires sending the output tokens here
// // (and then requiring an additional transfer to the user), rather than inputing
// // the recipient into the Uniswap trade. Instead, we can have 2 Uniswap trades
// // (in the worst case scenario where the fee token isn't one of the traded tokens)
// // that sends the fee in the 1st, and reduce amountOutMin in the 2nd proportional
// // to the fees spent, such that the total execution price is the same as what was
// // intended by the user, even though there are fewer input tokens to spend on the
// // trade
// // *2:
// // Can't do `tradeInput = (inputAmount - inputSpentOnFee)` because of stack too deep


// /**
// * @title    UniV2LimitsStops
// * @notice   Wraps around an arbitrary UniV2 router contract and adds conditions
// *           of price to create limit orders and stop losses. Ensures that
// *           only a specific user can call a trade because the Autonomy Registry
// *           forces that the first argument of the calldata is the user's address
// *           and this contract knows that condition is true when the call is coming
// *           from an appropriate proxy
// * @author   Quantaf1re (James Key)
// */
// interface IUniV2LimitsStops {

//     using SafeERC20 for IERC20;

//     address payable public immutable registry;
//     address public immutable userVeriForwarder;
//     address public immutable userFeeVeriForwarder;
//     address public immutable WETH;
//     FeeInfo private _defaultFeeInfo;
//     uint256 private constant MAX_UINT = type(uint256).max;


//     struct FeeInfo {
//         // Need a known instance of UniV2 that is guaranteed to have the token
//         // that the default fee is paid in, along with enough liquidity, since
//         // an arbitrary instance of UniV2 is passed to fcns in this contract
//         IUniswapV2Router02 uni;
//         address[] path;
//         // Whether or not the fee token is AUTO, because that needs to
//         // get sent to the user, since `transferFrom` is used from them directly
//         // in the Registry to charge the fee
//         bool isAUTO;
//     }

//     // Hold arguments for calling Uniswap to avoid stack to deep errors
//     struct UniArgs{
//         uint inputAmount;
//         uint amountOutMin;
//         uint amountOutMax;
//         address[] path;
//         uint deadline;
//     }


//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////
//     ////                                                          ////
//     ////-----------------------ETH to token-----------------------////
//     ////                                                          ////
//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////

//     /**
//      * @notice  Only calls swapExactETHForTokens if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired.
//      */
//     function ethToTokenRange(
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         address to,
//         uint deadline
//     ) external payable gasPriceCheck(maxGasPrice) {
//         uint[] memory amounts = uni.swapExactETHForTokens{value: msg.value}(amountOutMin, path, to, deadline);
//         require(amounts[amounts.length-1] <= amountOutMax, "LimitsStops: price too high");
//     }

//     function _ethToTokenPayDefault(
//         address user,
//         uint feeAmount,
//         IUniswapV2Router02 uni,
//         UniArgs memory uniArgs
//     ) private {
//         FeeInfo memory feeInfo = _defaultFeeInfo;
//         if (feeInfo.isAUTO) {
//             feeInfo.path[0] = WETH;
//         }

//         _ethToTokenPaySpecific(user, feeAmount, uni, feeInfo, uniArgs);
//     }

//     function _ethToTokenPaySpecific(
//         address user,
//         uint feeAmount,
//         IUniswapV2Router02 uni,
//         FeeInfo memory feeInfo,
//         UniArgs memory uniArgs
//     ) private {
//         // Pay the execution fee
//         uint tradeInput = msg.value;
//         if (feeInfo.isAUTO) {
//             tradeInput -= feeInfo.uni.swapETHForExactTokens{value: msg.value}(
//                 feeAmount,
//                 feeInfo.path,
//                 user,
//                 uniArgs.deadline
//             )[0];
//         } else {
//             registry.transfer(feeAmount);
//             tradeInput -= feeAmount;
//         }

//         // *1, *2
//         uint[] memory amounts = uni.swapExactETHForTokens{value: tradeInput}(
//             uniArgs.amountOutMin * tradeInput / msg.value,
//             uniArgs.path,
//             user,
//             uniArgs.deadline
//         );

//         require(amounts[amounts.length-1] <= uniArgs.amountOutMax * tradeInput / msg.value, "LimitsStops: price too high");
//     }

//     /**
//      * @notice  Only calls swapExactETHForTokens if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired. Additionally, 
//      *          takes part of the trade and uses it to pay `feeAmount`,
//      *          in the default fee token, to the registry
//      */
//     function ethToTokenRangePayDefault(
//         address user,
//         uint feeAmount,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         uint deadline
//     ) external payable gasPriceCheck(maxGasPrice) userFeeVerified {
//         _ethToTokenPayDefault(
//             user,
//             feeAmount,
//             uni,
//             UniArgs(0, amountOutMin, amountOutMax, path, deadline)
//         );
//     }

//     /**
//      * @notice  Only calls swapExactETHForTokens if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired. Additionally, 
//      *          takes part of the trade and uses it to pay `feeAmount`,
//      *          in the specified fee token, to the registry.
//      *          WARNING: only use this if you want to do things non-standard
//      */
//     function ethToTokenRangePaySpecific(
//         address user,
//         uint feeAmount,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         FeeInfo memory feeInfo,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         uint deadline
//     ) external payable gasPriceCheck(maxGasPrice) userFeeVerified {
//         _ethToTokenPaySpecific(
//             user,
//             feeAmount,
//             uni,
//             feeInfo,
//             UniArgs(0, amountOutMin, amountOutMax, path, deadline)
//         );
//     }


//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////
//     ////                                                          ////
//     ////-----------------------Token to ETH-----------------------////
//     ////                                                          ////
//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////

//     /**
//      * @notice  Only calls swapExactTokensForETH if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired.
//      */
//     function tokenToEthRange(
//         address user,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         uint inputAmount,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         address to,
//         uint deadline
//     ) external gasPriceCheck(maxGasPrice) userVerified {
//         transferApproveUnapproved(uni, path[0], inputAmount, user);
//         uint[] memory amounts = uni.swapExactTokensForETH(inputAmount, amountOutMin, path, to, deadline);
//         require(amounts[amounts.length-1] <= amountOutMax, "LimitsStops: price too high");
//     }

//     function _tokenToEthPayDefault(
//         address user,
//         uint feeAmount,
//         IUniswapV2Router02 uni,
//         UniArgs memory uniArgs
//     ) private {
//         FeeInfo memory feeInfo = _defaultFeeInfo;
//         // The fee path only needs to be modified when not paying in ETH (since
//         // the output of the trade is ETH and that can be used) and when the input
//         // token isn't AUTO anyway (since that can be used without a 2nd trade)
//         if (feeInfo.isAUTO && uniArgs.path[0] != feeInfo.path[feeInfo.path.length-1]) {
//             address[] memory newFeePath = new address[](3);
//             newFeePath[0] = uniArgs.path[0];               // src token
//             newFeePath[1] = WETH;   // WETH_ since path in tokenToETH ends in WETH_
//             newFeePath[2] = feeInfo.path[feeInfo.path.length-1];   // AUTO since feePath here ends in AUTO
//             feeInfo.path = newFeePath;
//         }

//         _tokenToEthPaySpecific(user, feeAmount, uni, feeInfo, uniArgs);
//     }

//     function _tokenToEthPaySpecific(
//         address user,
//         uint feeAmount,
//         IUniswapV2Router02 uni,
//         FeeInfo memory feeInfo,
//         UniArgs memory uniArgs
//     ) private {
//         // Pay the execution fee
//         uint tradeInput = uniArgs.inputAmount;
//         if (feeInfo.isAUTO) {
//             // If the src token is AUTO
//             if (uniArgs.path[0] == feeInfo.path[feeInfo.path.length-1]) {
//                 // The user already holds inputAmount of AUTO, so don't move them
//                 tradeInput -= feeAmount;
//                 transferApproveUnapproved(uni, uniArgs.path[0], tradeInput, user);
//             } else {
//                 transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
//                 approveUnapproved(feeInfo.uni, uniArgs.path[0], uniArgs.inputAmount);
//                 tradeInput -= feeInfo.uni.swapTokensForExactTokens(feeAmount, uniArgs.inputAmount, feeInfo.path, user, uniArgs.deadline)[0];
//             }
//         } else {
//             transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
//         }

//         // *1, *2
//         uint[] memory amounts = uni.swapExactTokensForETH(
//             tradeInput,
//             uniArgs.amountOutMin * tradeInput / uniArgs.inputAmount,
//             uniArgs.path,
//             // Sending it all to the registry means that the fee will be kept
//             // (if it's in ETH) and the excess sent to the user
//             feeInfo.isAUTO ? user : registry,
//             uniArgs.deadline
//         );
//         require(amounts[amounts.length-1] <= uniArgs.amountOutMax * tradeInput / uniArgs.inputAmount, "LimitsStops: price too high");
//     }

//     /**
//      * @notice  Only calls swapExactTokensForETH if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired. Additionally, 
//      *          takes part of the trade and uses it to pay `feeAmount`,
//      *          in the default fee token, to the registry
//      */
//     function tokenToEthRangePayDefault(
//         address user,
//         uint feeAmount,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         uint inputAmount,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         uint deadline
//     ) external gasPriceCheck(maxGasPrice) userFeeVerified {
//         _tokenToEthPayDefault(
//             user,
//             feeAmount,
//             uni,
//             UniArgs(inputAmount, amountOutMin, amountOutMax, path, deadline)
//         );
//     }

//     /**
//      * @notice  Only calls swapExactTokensForETH if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired. Additionally, 
//      *          takes part of the trade and uses it to pay `feeAmount`,
//      *          in the specified fee token, to the registry.
//      *          WARNING: only use this if you want to do things non-standard
//      */
//     function tokenToEthRangePaySpecific(
//         address user,
//         uint feeAmount,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         FeeInfo memory feeInfo,
//         uint inputAmount,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         uint deadline
//     ) external gasPriceCheck(maxGasPrice) userFeeVerified {
//         _tokenToEthPaySpecific(
//             user,
//             feeAmount,
//             uni,
//             feeInfo,
//             UniArgs(inputAmount, amountOutMin, amountOutMax, path, deadline)
//         );
//     }

//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////
//     ////                                                          ////
//     ////----------------------Token to token----------------------////
//     ////                                                          ////
//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////

//     /**
//      * @notice  Only calls swapExactTokensForTokens if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired.
//      */
//     function tokenToTokenRange(
//         address user,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         uint inputAmount,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         address to,
//         uint deadline
//     ) external gasPriceCheck(maxGasPrice) userVerified {
//         transferApproveUnapproved(uni, path[0], inputAmount, user);
//         uint[] memory amounts = uni.swapExactTokensForTokens(inputAmount, amountOutMin, path, to, deadline);
//         require(amounts[amounts.length-1] <= amountOutMax, "LimitsStops: price too high");
//     }

//     function _tokenToTokenPayDefault(
//         address user,
//         uint feeAmount,
//         IUniswapV2Router02 uni,
//         UniArgs memory uniArgs
//     ) private {
//         FeeInfo memory feeInfo = _defaultFeeInfo;
//         // The fee path only needs to be modified when the src/dest tokens aren't
//         // AUTO (if paying in AUTO), and when paying in ETH
//         if (feeInfo.isAUTO && uniArgs.path[0] != feeInfo.path[feeInfo.path.length-1]) {
//             address[] memory newFeePath = new address[](3);
//             newFeePath[0] = uniArgs.path[0];                // src token
//             newFeePath[1] = WETH;                  // WETH_ since path in tokenToETH ends in WETH_
//             newFeePath[2] = feeInfo.path[feeInfo.path.length-1];   // AUTO since feePath here ends in AUTO
//             feeInfo.path = newFeePath;
//         } else if (!feeInfo.isAUTO) {
//             feeInfo.path[0] = uniArgs.path[0];
//         }

//         _tokenToTokenPaySpecific(user, feeAmount, uni, feeInfo, uniArgs);
//     }

//     function _tokenToTokenPaySpecific(
//         address user,
//         uint feeAmount,
//         IUniswapV2Router02 uni,
//         FeeInfo memory feeInfo,
//         UniArgs memory uniArgs
//     ) private {
//         // Pay the execution fee
//         uint tradeInput = uniArgs.inputAmount;
//         if (feeInfo.isAUTO) {
//             // If the src token is AUTO
//             if (uniArgs.path[0] == feeInfo.path[feeInfo.path.length-1]) {
//                 // The user already holds inputAmount of AUTO
//                 tradeInput -= feeAmount;
//                 transferApproveUnapproved(uni, uniArgs.path[0], tradeInput, user);
//             // If the dest token is AUTO
//             } else if (uniArgs.path[uniArgs.path.length-1] == feeInfo.path[feeInfo.path.length-1]) {
//                 // Do nothing because it'll all get sent to the user, and the
//                 // fee will be taken from them after that
//                 transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
//             } else {
//                 transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
//                 approveUnapproved(feeInfo.uni, uniArgs.path[0], uniArgs.inputAmount);
//                 tradeInput -= feeInfo.uni.swapTokensForExactTokens(feeAmount, uniArgs.inputAmount, feeInfo.path, user, uniArgs.deadline)[0];
//             }
//         } else {
//             transferApproveUnapproved(uni, uniArgs.path[0], uniArgs.inputAmount, user);
//             approveUnapproved(feeInfo.uni, uniArgs.path[0], uniArgs.inputAmount);
//             tradeInput -= feeInfo.uni.swapTokensForExactETH(feeAmount, uniArgs.inputAmount, feeInfo.path, registry, uniArgs.deadline)[0];
//         }

//         // *1, *2
//         uint[] memory amounts = uni.swapExactTokensForTokens(
//             tradeInput,
//             uniArgs.amountOutMin * tradeInput / uniArgs.inputAmount,
//             uniArgs.path,
//             user,
//             uniArgs.deadline
//         );
//         require(amounts[amounts.length-1] <= uniArgs.amountOutMax * tradeInput / uniArgs.inputAmount, "LimitsStops: price too high");
//     }

//     /**
//      * @notice  Only calls swapExactTokensForTokens if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired. Additionally, 
//      *          takes part of the trade and uses it to pay `feeAmount`,
//      *          in the default fee token, to the registry
//      */
//     function tokenToTokenRangePayDefault(
//         address user,
//         uint feeAmount,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         uint inputAmount,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         uint deadline
//     ) external gasPriceCheck(maxGasPrice) userFeeVerified {
//         _tokenToTokenPayDefault(
//             user,
//             feeAmount,
//             uni,
//             UniArgs(inputAmount, amountOutMin, amountOutMax, path, deadline)
//         );
//     }

//     /**
//      * @notice  Only calls swapExactTokensForTokens if the output is above
//      *          `amountOutMin` and below `amountOutMax`. `amountOutMax`
//      *          is the 'stop price' when used as a stop loss, and
//      *          `amountOutMin` is the 'limit price' when used as a limit
//      *          order. When using this as a classic limit order, `amountOutMax`
//      *          would be sent to the max uint value. When using this
//      *          as a classic stop loss, `amountOutMin` would be set to 0.
//      *          The min/max can also be used to limit downside during flash
//      *          crashes, e.g. `amountOutMin` could be set to 10% lower then
//      *          `amountOutMax` for a stop loss, if desired. Additionally, 
//      *          takes part of the trade and uses it to pay `feeAmount`,
//      *          in the specified fee token, to the registry.
//      *          WARNING: only use this if you want to do things non-standard
//      */
//     function tokenToTokenRangePaySpecific(
//         address user,
//         uint feeAmount,
//         uint maxGasPrice,
//         IUniswapV2Router02 uni,
//         FeeInfo memory feeInfo,
//         uint inputAmount,
//         uint amountOutMin,
//         uint amountOutMax,
//         address[] calldata path,
//         uint deadline
//     ) external gasPriceCheck(maxGasPrice) userFeeVerified {
//         _tokenToTokenPaySpecific(
//             user,
//             feeAmount,
//             uni,
//             feeInfo,
//             UniArgs(inputAmount, amountOutMin, amountOutMax, path, deadline)
//         );
//     }


//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////
//     ////                                                          ////
//     ////-------------------------Helpers--------------------------////
//     ////                                                          ////
//     //////////////////////////////////////////////////////////////////
//     //////////////////////////////////////////////////////////////////

//     function approveUnapproved(IUniswapV2Router02 uni, address tokenAddr, uint amount) private returns (IERC20 token) {
//         token = IERC20(tokenAddr);
//         if (token.allowance(address(this), address(uni)) < amount) {
//             token.approve(address(uni), MAX_UINT);
//         }
//     }

//     function transferApproveUnapproved(IUniswapV2Router02 uni, address tokenAddr, uint amount, address user) private {
//         IERC20 token = approveUnapproved(uni, tokenAddr, amount);
//         token.safeTransferFrom(user, address(this), amount);
//     }

//     function setDefaultFeeInfo(FeeInfo calldata newDefaultFee) external onlyOwner {
//         _defaultFeeInfo = newDefaultFee;
//     }

//     function getDefaultFeeInfo() external view returns (FeeInfo memory) {
//         return _defaultFeeInfo;
//     }

//     modifier userVerified() {
//         require(msg.sender == userVeriForwarder, "LimitsStops: not userForw");
//         _;
//     }

//     modifier userFeeVerified() {
//         require(msg.sender == userFeeVeriForwarder, "LimitsStops: not userFeeForw");
//         _;
//     }

//     modifier gasPriceCheck(uint maxGasPrice) {
//         require(tx.gasprice <= maxGasPrice, "LimitsStops: gasPrice too high");
//         _;
//     }

//     // Needed to receive excess ETH when calling swapETHForExactTokens
//     receive() external payable {}
// }