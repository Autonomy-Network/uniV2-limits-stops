from consts import *
from brownie import a, reverts, Contract, web3, chain
from brownie.test import given, strategy
import time
from utils import *


# test reverting by calling from different accounts, and from wrong forwarder
# really small input amount that doesn't cover the cost of execution


def test_ethToTokenLimitOrderPaySpecific_eth(auto, evmMaths, uni_router2, any, uniLS):
    path = [WETH_ADDR, ANY_ADDR]
    input_amount = int(0.1 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(init_output * 1.1)
    call_data = uniLS.ethToTokenLimitOrderPaySpecific.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, DEFAULT_FEE_INFO, limit_output, path, auto.CHARLIE, time.time() * 2)
    msg_value = input_amount
    any_start_bal = any.balanceOf(auto.CHARLIE)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, msg_value, input_amount, True, True, False)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, input_amount, True, True, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == msg_value
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    uni_router2.swapExactTokensForETH(whale_amount, 1, path[::-1], auto.WHALE, time.time()*2, auto.FR_WHALE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == msg_value
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    fee_input = evmMaths.mul3div1(EXPECTED_GAS, INIT_GAS_PRICE_FAST, PAY_ETH_BPS, BASE_BPS)
    trade_output = uni_router2.getAmountsOut(msg_value - fee_input, path)[-1]

    # Execute successfully :D
    # Annoyingly, this fails for some reason, probably due to an issue with mainnet-fork in brownie. Assuming a gas
    # usage of 300k gas
    # expected_gas = auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST) + fee_input
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == trade_output
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO


def test_ethToTokenLimitOrderPaySpecific_AUTO(auto, evmMaths, uni_router2, any, uniLS):
    new_default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)

    path = [WETH_ADDR, ANY_ADDR]
    input_amount = int(0.1 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(init_output * 1.1)
    call_data = uniLS.ethToTokenLimitOrderPaySpecific.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, new_default_fee_info, limit_output, path, auto.CHARLIE, time.time() * 2)
    msg_value = input_amount
    any_start_bal = any.balanceOf(auto.CHARLIE)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, msg_value, msg_value, True, True, True)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, msg_value, True, True, True, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == msg_value
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    uni_router2.swapExactTokensForETH(whale_amount, 1, path[::-1], auto.WHALE, time.time()*2, auto.FR_WHALE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == msg_value
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    fee_output = get_AUTO_for_exec(evmMaths, EXPECTED_GAS, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    fee_input = uni_router2.getAmountsIn(fee_output, [WETH_ADDR, auto.AUTO])[0]
    # Assumes the traded token is not AUTO
    trade_output = uni_router2.getAmountsOut(msg_value - fee_input, path)[-1]

    # Execute successfully :D
    # Annoyingly, this fails for some reason, probably due to an issue with mainnet-fork in brownie. Assuming a gas
    # usage of 300k gas
    # expected_gas = auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST)
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == trade_output
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == fee_output
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO


@given(
    input_amount=strategy('uint', min_value=10000, max_value=INIT_ETH_BAL),
    whale_amount=strategy('uint', min_value=10000, max_value=INIT_ANY_BAL),
    expected_gas=strategy('uint', min_value=MIN_GAS, max_value=EXPECTED_GAS),
    pay_with_AUTO=strategy('bool')
)
def test_ethToTokenLimitOrderPaySpecific_random(auto, evmMaths, uni_router2, any, uniLS, input_amount, whale_amount, expected_gas, pay_with_AUTO):
    if pay_with_AUTO:
        new_default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
    else:
        new_default_fee_info = DEFAULT_FEE_INFO
    path = [WETH_ADDR, ANY_ADDR]
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(init_output * 1.1)
    msg_value = input_amount
    call_data = uniLS.ethToTokenLimitOrderPaySpecific.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, new_default_fee_info, limit_output, path, auto.CHARLIE, time.time() * 2)
    any_start_bal = any.balanceOf(auto.CHARLIE)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, msg_value, input_amount, True, True, pay_with_AUTO)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, input_amount, True, True, pay_with_AUTO, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == msg_value
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    uni_router2.swapExactTokensForETH(whale_amount, 1, path[::-1], auto.WHALE, time.time()*2, auto.FR_WHALE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == msg_value
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    if pay_with_AUTO:
        fee_output = get_AUTO_for_exec(evmMaths, expected_gas, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
        fee_input = uni_router2.getAmountsIn(fee_output, [WETH_ADDR, auto.AUTO])[0]
    else:
        fee_input = evmMaths.mul3div1(expected_gas, INIT_GAS_PRICE_FAST, PAY_ETH_BPS, BASE_BPS)

    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    # Not enough ETH to pay the fee
    if msg_value < fee_input:
        with reverts():
            tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    # In the case of ETH to token where the token is less valuable, it shouldn't be an issue to
    # trade small amounts, just just to have a consistent testing method
    elif msg_value >= fee_input + MIN_TRADE_AMOUNT and cur_output < limit_output:
        with reverts(REV_MSG_UNI_OUTPUT):
            tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    elif msg_value >= fee_input + MIN_TRADE_AMOUNT and cur_output >= limit_output:
        if pay_with_AUTO:
            # Assumes the traded token is not AUTO
            trade_output = uni_router2.getAmountsOut(msg_value - fee_input, path)[-1]
        else:
            trade_output = uni_router2.getAmountsOut(msg_value - fee_input, path)[-1]
        
        tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        
        assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
        assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST) \
            if pay_with_AUTO else INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST) + fee_input
        assert uniLS.balance() == 0
        assert auto.r.balance() == 0
        assert any.balanceOf(auto.CHARLIE) == trade_output
        assert any.balanceOf(auto.EXEC) == 0
        assert any.balanceOf(uniLS) == 0
        assert any.balanceOf(auto.r) == 0
        assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
        assert auto.AUTO.balanceOf(auto.EXEC) == (fee_output if pay_with_AUTO else 0)
        assert auto.AUTO.balanceOf(uniLS) == 0
        assert auto.AUTO.balanceOf(auto.r) == 0
        assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO