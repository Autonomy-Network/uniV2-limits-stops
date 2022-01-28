from consts import *
import time
import math
from brownie import chain


def get_AUTO_for_exec(evmMaths, expected_gas, AUTOPerETH, gasPriceFast):
    # Need to account for differences in division between Python and Solidity
    return evmMaths.mul4Div2(expected_gas, gasPriceFast, AUTOPerETH, PAY_AUTO_BPS, BASE_BPS, E_18)


def setDefaultFeeInfoPrep(auto, uni, uniLS, new_default_fee, eta, extra):
    callData = uniLS.setDefaultFeeInfo.encode_input(new_default_fee)
    args = (uniLS, 0, "", callData, chain.time() + eta)
    auto.tl.queueTransaction(*args)
    chain.sleep(eta + extra)

    return args