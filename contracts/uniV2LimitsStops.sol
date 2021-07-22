pragma solidity ^0.8;


import "../interfaces/IUniswapV2Router02.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


contract UniV2LimitsStops {

    address public autonomyVF;
    uint256 private constant MAX_UINT = type(uint256).max;

    constructor(address autonomyVF_) {
        autonomyVF = autonomyVF_;
    }

    function ethToTokenLimitOrder(
        IUniswapV2Router02 uni,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable {
        uni.swapExactETHForTokens{value: msg.value}(amountOutMin, path, to, deadline);
    }

    function tokenToEthLimitOrder(
        address payable sender,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external onlyAutonomyVF {
        IERC20 token = approveUnapproved(uni, path[0], inputAmount);
        token.transferFrom(sender, address(this), inputAmount);
        uni.swapExactTokensForETH(inputAmount, amountOutMin, path, to, deadline);
    }

    function tokenToTokenLimitOrder(
        address payable sender,
        IUniswapV2Router02 uni,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external onlyAutonomyVF {
        IERC20 token = approveUnapproved(uni, path[0], inputAmount);
        token.transferFrom(sender, address(this), inputAmount);
        uni.swapExactTokensForTokens(inputAmount, amountOutMin, path, to, deadline);
    }

    function approveUnapproved(IUniswapV2Router02 uni, address tokenAddr, uint inputAmount) private returns (IERC20 token) {
        token = IERC20(tokenAddr);
        if (token.allowance(address(this), address(uni)) < inputAmount) {
            token.approve(address(uni), MAX_UINT);
        }
    }

    modifier onlyAutonomyVF() {
        require(msg.sender == autonomyVF, "Only Autonomy. Nice try");
        _;
    }

}