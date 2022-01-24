pragma solidity 0.8.6;


import "@openzeppelin/contracts/token/ERC20/ERC20.sol";


/**
* @title    AUTO contract
* @notice   The AUTO utility token which is used to stake in Autonomy and pay for
*           execution fees with
* @author   Quantaf1re (James Key)
*/
contract Token is ERC20 {

    constructor(
        string memory name,
        string memory symbol,
        address receiver,
        uint256 mintAmount
    ) ERC20(name, symbol) {
        _mint(receiver, mintAmount);
    }

}
