# uniV2-limit-stop
Autonomy Network is a protocol for decentralised automation. The Autonomy contracts themselves can be found [here](https://github.com/Autonomy-Network/autonomy-contracts).

In order to automate something with a condition using Autonomy, that condition needs to be codified in a wrapper contract around the target contract. This repo is an example of that - used in production to add limit orders and stop losses to UniswapV2. Only 1 instance of this contract needs to be deployed per blockchain, since it can be used for limits and stops to anything that fits the UniswapV2 interface - such as any UniswapV2 fork, which most DEXes are.
