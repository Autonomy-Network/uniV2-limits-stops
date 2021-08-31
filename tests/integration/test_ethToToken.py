from consts import *
from brownie import a, reverts, Contract, chain
import time


def test_ethToTokenLimitOrder_swapExactTokensForETH_swapExactTokensForETH_execute(auto, uni_router2, any, uniLS):
    path = [WETH_ADDR, ANY_ADDR]
    # For 0.1 ETH
    input_amount = int(0.1 * E_18)
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(cur_output * 1.1)
    call_data = uniLS.ethToTokenLimitOrder.encode_input(MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, limit_output, path, auto.CHARLIE, time.time() * 2)
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

    # Swap ANY to the Uniswap contract to make the price of ANY slightly cheaper
    whale_amount = int(0.1 * E_18)
    any.approve(uni_router2, whale_amount, auto.FR_WHALE)
    uni_router2.swapExactTokensForETH(whale_amount, 1, [ANY_ADDR, WETH_ADDR], auto.WHALE, time.time()*2, auto.FR_WHALE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    with reverts(REV_MSG_UNI_OUTPUT):
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    any.approve(uni_router2, whale_amount, auto.FR_WHALE)
    uni_router2.swapExactTokensForETH(whale_amount, 1, [ANY_ADDR, WETH_ADDR], auto.WHALE, time.time()*2, auto.FR_WHALE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    # Execute successfully :D
    expected_gas = auto.r.executeHashedReq.call(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    # assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost + (max_fee - (tx.return_value * INIT_GAS_PRICE_FAST))
    assert any.balanceOf(auto.CHARLIE) >= any_start_bal + limit_output
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0


def test_ethToTokenStopLoss_swapExactETHForTokens_swapExactETHForTokens(auto, uni_router2, any, uniLS):
    path = [WETH_ADDR, ANY_ADDR]
    # For 0.1 ETH
    input_amount = int(0.1 * E_18)
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    min_output = int(cur_output * 0.8)
    max_output = int(cur_output * 0.9)
    call_data = uniLS.ethToTokenStopLoss.encode_input(MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, min_output, max_output, path, auto.CHARLIE, time.time() * 2)
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

    # Swap ANY to the Uniswap contract to make the price of ANY slightly cheaper
    whale_amount = int(0.01 * E_18)
    any.approve(uni_router2, whale_amount, auto.FR_WHALE)
    uni_router2.swapExactETHForTokens(1, [WETH_ADDR, ANY_ADDR], auto.WHALE, time.time()*2, {'value': whale_amount, 'from': auto.WHALE})
    
    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    with reverts(REV_MSG_PRICE_HIGH):
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Swap ANY to the Uniswap contract to make the price of ANY slightly cheaper
    while not (min_output < uni_router2.getAmountsOut(input_amount, path)[-1] < max_output):
        whale_amount = int(0.1*E_18)
        any.approve(uni_router2, whale_amount, auto.FR_WHALE)
        uni_router2.swapExactETHForTokens(1, [WETH_ADDR, ANY_ADDR], auto.WHALE, time.time()*2, {'value': whale_amount, 'from': auto.WHALE})
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]

    # Execute successfully :D
    expected_gas = auto.r.executeHashedReq.call(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    # assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost + (max_fee - (tx.return_value * INIT_GAS_PRICE_FAST))
    assert any.balanceOf(auto.CHARLIE) == any_start_bal + cur_output
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0