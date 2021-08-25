from consts import *
from brownie import a, reverts, Contract
from brownie.test import given, strategy
import time


@given(
    input_amount=strategy('uint', min_value=10000, max_value=INIT_ETH_BAL),
    whale_amount=strategy('uint', min_value=10000, max_value=INIT_ANY_BAL/2)
)
def test_ethToTokenLimitOrder_random(auto, uni_router2, any, uniLS, input_amount, whale_amount):
    path = [WETH_ADDR, ANY_ADDR]
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(cur_output * 1.1)
    call_data = uniLS.ethToTokenLimitOrder.encode_input(UNIV2_ROUTER2_ADDR, limit_output, path, auto.CHARLIE, time.time() * 2)
    max_fee = int(0.01 * E_18)
    msg_value = input_amount + max_fee
    any_start_bal = any.balanceOf(auto.CHARLIE)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, msg_value, input_amount, False, False, False)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, input_amount, False, False, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    any.approve(uni_router2, whale_amount, auto.FR_WHALE)
    uni_router2.swapExactTokensForETH(whale_amount, 1, [ANY_ADDR, WETH_ADDR], auto.WHALE, time.time()*2, auto.FR_WHALE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    if uni_router2.getAmountsOut(input_amount, path)[-1] >= limit_output:
        # Execute successfully :D
        expected_gas = auto.r.executeHashedReq.call(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

        # assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost + (max_fee - (tx.return_value * INIT_GAS_PRICE_FAST))
        assert any.balanceOf(auto.CHARLIE) >= any_start_bal + limit_output
        assert uniLS.balance() == 0
        assert any.balanceOf(uniLS) == 0
    else:
        with reverts(REV_MSG_UNI_OUTPUT):
            auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_ethToTokenLimitOrder_rev_msgValue(auto, uni_router2, any, uniLS):
    path = [WETH_ADDR, ANY_ADDR]
    # For 0.1 ETH
    input_amount = int(0.1 * E_18)
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(cur_output * 1.1)
    call_data = uniLS.ethToTokenLimitOrder.encode_input(UNIV2_ROUTER2_ADDR, limit_output, path, auto.CHARLIE, time.time() * 2)
    msg_value = input_amount + int(0.01 * E_18)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, msg_value, 0, False, False, False)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, 0, False, False, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    any.approve(uni_router2, whale_amount, auto.FR_WHALE)
    uni_router2.swapExactTokensForETH(whale_amount, 1, [ANY_ADDR, WETH_ADDR], auto.WHALE, time.time()*2, auto.FR_WHALE)
    
    with reverts(REV_MSG_UNI_INPUT):
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_ethToTokenLimitOrder_rev_no_price_change(auto, uni_router2, any, uniLS):
    path = [WETH_ADDR, ANY_ADDR]
    # For 0.1 ETH
    input_amount = int(0.1 * E_18)
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(cur_output * 1.1)
    call_data = uniLS.ethToTokenLimitOrder.encode_input(UNIV2_ROUTER2_ADDR, limit_output, path, auto.CHARLIE, time.time() * 2)
    msg_value = input_amount + int(0.01 * E_18)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, msg_value, input_amount, False, False, False)

    # Make the request
    auto.r.newReq(uniLS, auto.DENICE, call_data, input_amount, False, False, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    # Check that the request reverts without the condition being fulfilled
    with reverts(REV_MSG_UNI_OUTPUT):
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})