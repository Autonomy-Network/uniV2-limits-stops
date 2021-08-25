from consts import *
from brownie import a, reverts, Contract, web3, chain
from brownie.test import given, strategy
import time
from utils import *


def test_tokenToTokenStopLossPayDefault_eth(auto, evmMaths, uni_router2, any, dai, uniLS):
    path = [ANY_ADDR, WETH_ADDR, dai]
    input_amount = int(10 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    max_output = int(init_output * 0.9)
    call_data = uniLS.tokenToTokenStopLossPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, 1, max_output, path, time.time() * 2)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, 0, 0, True, True, False)

    any.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    any.approve(uniLS, input_amount, auto.FR_CHARLIE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, 0, True, True, False, {'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL  - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    whale_amount = 10**22
    uni_router2.swapExactTokensForTokens(whale_amount, 1, path, auto.WHALE, time.time()*2, {'from': auto.WHALE})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    fee_output = evmMaths.mul3div1(EXPECTED_GAS, INIT_GAS_PRICE_FAST, PAY_ETH_BPS, BASE_BPS)
    fee_input = uni_router2.swapTokensForExactETH(fee_output, MAX_UINT, [any, WETH_ADDR], auto.WHALE, time.time()*2, auto.FR_WHALE).return_value[0]
    trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
    chain.undo()

    # Execute successfully :D
    # Annoyingly, this fails for some reason, probably due to an issue with mainnet-fork in brownie. Assuming a gas
    # usage of 300k gas
    # expected_gas = auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST) + fee_output
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert dai.balanceOf(auto.CHARLIE) == trade_output
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO


def test_tokenToTokenStopLossPayDefault_AUTO(auto, evmMaths, uni_router2, any, dai, uniLS):
    default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
    uniLS.setDefaultFeeInfo(default_fee_info)

    path = [ANY_ADDR, WETH_ADDR, dai]
    input_amount = int(10 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    max_output = int(init_output * 0.9)
    call_data = uniLS.tokenToTokenStopLossPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, 1, max_output, path, time.time() * 2)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, 0, 0, True, True, True)

    any.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    any.approve(uniLS, input_amount, auto.FR_CHARLIE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, 0, True, True, True, {'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    uni_router2.swapExactTokensForTokens(whale_amount, 1, path, auto.WHALE, time.time()*2, {'from': auto.WHALE})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    fee_output = get_AUTO_for_exec(evmMaths, EXPECTED_GAS, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    fee_input = uni_router2.swapTokensForExactTokens(fee_output, MAX_UINT, [any, WETH_ADDR, auto.AUTO], auto.WHALE, time.time()*2, auto.FR_WHALE).return_value[0]
    # Assumes the traded token is not AUTO
    trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
    chain.undo()

    # Execute successfully :D
    # Annoyingly, this fails for some reason, probably due to an issue with mainnet-fork in brownie. Assuming a gas
    # usage of 300k gas
    # expected_gas = auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST)
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == MAX_UINT - input_amount
    assert dai.balanceOf(auto.CHARLIE) == trade_output
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == fee_output
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info


def test_tokenToTokenStopLossPayDefault_AUTO_trade_from_AUTO(auto, evmMaths, uni_router2, any, dai, uniLS):
    default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
    uniLS.setDefaultFeeInfo(default_fee_info)

    path = [auto.AUTO, WETH_ADDR, dai]
    input_amount = int(10 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    max_output = int(init_output * 0.9)
    call_data = uniLS.tokenToTokenStopLossPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, 1, max_output, path, time.time() * 2)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, 0, 0, True, True, True)

    auto.AUTO.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    auto.AUTO.approve(uniLS, input_amount, auto.FR_CHARLIE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == input_amount
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, 0, True, True, True, {'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == input_amount
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    uni_router2.swapExactTokensForTokens(whale_amount, 1, path, auto.WHALE, time.time()*2, {'from': auto.WHALE})
    assert uni_router2.getAmountsOut(input_amount, path)[-1] <= max_output

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == input_amount
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    fee_output = get_AUTO_for_exec(evmMaths, EXPECTED_GAS, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    fee_input = fee_output
    # Assumes the traded token is not AUTO
    trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
    
    # Execute successfully :D
    # Annoyingly, this fails for some reason, probably due to an issue with mainnet-fork in brownie. Assuming a gas
    # usage of 300k gas
    # expected_gas = auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST)
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == trade_output
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == fee_output
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == MAX_UINT - (input_amount - fee_input)
    assert uniLS.getDefaultFeeInfo() == default_fee_info


def test_tokenToTokenStopLossPayDefault_AUTO_trade_to_AUTO(auto, evmMaths, uni_router2, any, dai, uniLS):
    default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
    uniLS.setDefaultFeeInfo(default_fee_info)

    path = [any, WETH_ADDR, auto.AUTO]
    input_amount = int(10 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    max_output = int(init_output * 0.9)
    call_data = uniLS.tokenToTokenStopLossPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, 1, max_output, path, time.time() * 2)
    req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, 0, 0, True, True, True)

    any.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    any.approve(uniLS, input_amount, auto.FR_CHARLIE)

    assert auto.CHARLIE.balance() == INIT_ETH_BAL
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Make the request
    tx = auto.r.newReq(uniLS, auto.DENICE, call_data, 0, True, True, True, {'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    uni_router2.swapExactTokensForTokens(whale_amount, 1, path, auto.WHALE, time.time()*2, {'from': auto.WHALE})
    assert uni_router2.getAmountsOut(input_amount, path)[-1] <= max_output

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    fee_output = get_AUTO_for_exec(evmMaths, EXPECTED_GAS, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    # Assumes the traded token is not AUTO
    trade_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    
    # Execute successfully :D
    # Annoyingly, this fails for some reason, probably due to an issue with mainnet-fork in brownie. Assuming a gas
    # usage of 300k gas
    # expected_gas = auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST)
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == MAX_UINT - input_amount
    assert dai.balanceOf(auto.CHARLIE) == 0
    assert dai.balanceOf(auto.EXEC) == 0
    assert dai.balanceOf(uniLS) == 0
    assert dai.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == trade_output - fee_output
    assert auto.AUTO.balanceOf(auto.EXEC) == fee_output
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info


@given(
    input_token_id=strategy('uint', min_value=1, max_value=3),
    output_token_id=strategy('uint', min_value=1, max_value=3),
    input_amount=strategy('uint', min_value=MIN_RAND_INPUT_TOKEN, max_value=INIT_ANY_BAL/2),
    min_output=strategy('uint', max_value=INIT_ANY_BAL/2),
    max_output=strategy('uint', max_value=INIT_ANY_BAL/2),
    whale_amount=strategy('uint', min_value=MIN_RAND_INPUT_TOKEN, max_value=INIT_ANY_BAL/2),
    expected_gas=strategy('uint', min_value=MIN_GAS, max_value=EXPECTED_GAS),
    pay_with_AUTO=strategy('bool')
)
def test_tokenToTokenStopLossPayDefault_random(auto, evmMaths, uni_router2, any, dai, uniLS, input_token_id, output_token_id, input_amount, min_output, max_output, whale_amount, expected_gas, pay_with_AUTO):
    id_to_token = {1: any, 2: dai, 3: auto.AUTO}
    
    # Can't trade the same token for itself
    if input_token_id != output_token_id:
        input_token = id_to_token[input_token_id]
        output_token = id_to_token[output_token_id]
        if pay_with_AUTO:
            default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
            uniLS.setDefaultFeeInfo(default_fee_info)
        else:
            default_fee_info = DEFAULT_FEE_INFO
        path = [input_token, WETH_ADDR, output_token]
        init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
        call_data = uniLS.tokenToTokenStopLossPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, min_output, max_output, path, time.time() * 2)
        req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, 0, 0, True, True, pay_with_AUTO)

        input_token.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
        input_token.approve(uniLS, input_amount, auto.FR_CHARLIE)

        assert auto.CHARLIE.balance() == INIT_ETH_BAL
        assert auto.EXEC.balance() == INIT_ETH_BAL
        assert uniLS.balance() == 0
        assert auto.r.balance() == 0
        assert any.balanceOf(auto.CHARLIE) == (input_amount if input_token == any else 0)
        assert any.balanceOf(auto.EXEC) == 0
        assert any.balanceOf(uniLS) == 0
        assert any.balanceOf(auto.r) == 0
        assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
        assert dai.balanceOf(auto.CHARLIE) == (input_amount if input_token == dai else 0)
        assert dai.balanceOf(auto.EXEC) == 0
        assert dai.balanceOf(uniLS) == 0
        assert dai.balanceOf(auto.r) == 0
        assert auto.AUTO.balanceOf(auto.CHARLIE) == (input_amount if input_token == auto.AUTO else 0)
        assert auto.AUTO.balanceOf(auto.EXEC) == 0
        assert auto.AUTO.balanceOf(uniLS) == 0
        assert auto.AUTO.balanceOf(auto.r) == 0
        assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
        assert uniLS.getDefaultFeeInfo() == default_fee_info

        # Make the request
        tx = auto.r.newReq(uniLS, auto.DENICE, call_data, 0, True, True, pay_with_AUTO, {'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

        req_eth_cost = INIT_GAS_PRICE_FAST * tx.gas_used
        assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
        assert auto.EXEC.balance() == INIT_ETH_BAL
        assert uniLS.balance() == 0
        assert auto.r.balance() == 0
        assert any.balanceOf(auto.CHARLIE) == (input_amount if input_token == any else 0)
        assert any.balanceOf(auto.EXEC) == 0
        assert any.balanceOf(uniLS) == 0
        assert any.balanceOf(auto.r) == 0
        assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
        assert dai.balanceOf(auto.CHARLIE) == (input_amount if input_token == dai else 0)
        assert dai.balanceOf(auto.EXEC) == 0
        assert dai.balanceOf(uniLS) == 0
        assert dai.balanceOf(auto.r) == 0
        assert auto.AUTO.balanceOf(auto.CHARLIE) == (input_amount if input_token == auto.AUTO else 0)
        assert auto.AUTO.balanceOf(auto.EXEC) == 0
        assert auto.AUTO.balanceOf(uniLS) == 0
        assert auto.AUTO.balanceOf(auto.r) == 0
        assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
        assert uniLS.getDefaultFeeInfo() == default_fee_info

        # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
        uni_router2.swapExactTokensForTokens(whale_amount, 1, path, auto.WHALE, time.time()*2, {'from': auto.WHALE})

        assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
        assert auto.EXEC.balance() == INIT_ETH_BAL
        assert uniLS.balance() == 0
        assert auto.r.balance() == 0
        assert any.balanceOf(auto.CHARLIE) == (input_amount if input_token == any else 0)
        assert any.balanceOf(auto.EXEC) == 0
        assert any.balanceOf(uniLS) == 0
        assert any.balanceOf(auto.r) == 0
        assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
        assert dai.balanceOf(auto.CHARLIE) == (input_amount if input_token == dai else 0)
        assert dai.balanceOf(auto.EXEC) == 0
        assert dai.balanceOf(uniLS) == 0
        assert dai.balanceOf(auto.r) == 0
        assert auto.AUTO.balanceOf(auto.CHARLIE) == (input_amount if input_token == auto.AUTO else 0)
        assert auto.AUTO.balanceOf(auto.EXEC) == 0
        assert auto.AUTO.balanceOf(uniLS) == 0
        assert auto.AUTO.balanceOf(auto.r) == 0
        assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
        assert uniLS.getDefaultFeeInfo() == default_fee_info

        if pay_with_AUTO:
            fee_output = get_AUTO_for_exec(evmMaths, expected_gas, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
            if input_token == auto.AUTO:
                fee_input = fee_output
                allowance_used = input_amount - fee_input
                if input_amount >= fee_input + MIN_TRADE_AMOUNT:
                    trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
            elif output_token == auto.AUTO:
                fee_input = uni_router2.getAmountsIn(fee_output, path)[0]
                allowance_used = input_amount
                trade_output = uni_router2.getAmountsOut(input_amount, path)[-1]
            else:
                fee_input = uni_router2.swapTokensForExactTokens(fee_output, MAX_UINT, [input_token, WETH_ADDR, auto.AUTO], auto.WHALE, time.time()*2, auto.FR_WHALE).return_value[0]
                allowance_used = input_amount
                if input_amount >= fee_input + MIN_TRADE_AMOUNT:
                    trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
                chain.undo()
        else:
            fee_output = evmMaths.mul3div1(expected_gas, INIT_GAS_PRICE_FAST, PAY_ETH_BPS, BASE_BPS)
            fee_input = uni_router2.swapTokensForExactETH(fee_output, MAX_UINT, [input_token, WETH_ADDR], auto.WHALE, time.time()*2, auto.FR_WHALE).return_value[0]
            allowance_used = input_amount
            if input_amount >= fee_input + MIN_TRADE_AMOUNT:
                trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
            chain.undo()

        print(input_amount, path)
        cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
        print(cur_output, cur_output < (min_output*(input_amount-fee_input)/input_amount))
        # Not enough ETH to pay the fee
        if input_amount < fee_input:
            with reverts():
                tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        elif input_amount >= fee_input + MIN_TRADE_AMOUNT and cur_output < (min_output*(input_amount-fee_input)/input_amount):
            with reverts(REV_MSG_UNI_OUTPUT):
                tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        # In the case of ETH to token where the token is less valuable, it shouldn't be an issue to
        # trade small amounts, just just to have a consistent testing method
        elif input_amount >= fee_input + MIN_TRADE_AMOUNT and cur_output > max_output:
            with reverts(REV_MSG_PRICE_HIGH):
                tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        elif input_amount >= fee_input + MIN_TRADE_AMOUNT and cur_output >= max_output:
            assert uni_router2.getAmountsOut(input_amount, path)[-1] <= max_output

            tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
            
            assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
            assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST) + (0 if pay_with_AUTO else fee_output)
            assert uniLS.balance() == 0
            assert auto.r.balance() == 0
            assert any.balanceOf(auto.CHARLIE) == (trade_output if output_token == any else 0)
            assert any.balanceOf(auto.EXEC) == 0
            assert any.balanceOf(uniLS) == 0
            assert any.balanceOf(auto.r) == 0
            assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == (MAX_UINT - allowance_used if input_token == any else 0)
            assert dai.balanceOf(auto.CHARLIE) == (trade_output if output_token == dai else 0)
            assert dai.balanceOf(auto.EXEC) == 0
            assert dai.balanceOf(uniLS) == 0
            assert dai.balanceOf(auto.r) == 0
            assert dai.allowance(uniLS, UNIV2_ROUTER2_ADDR) == (MAX_UINT - allowance_used if input_token == dai else 0)
            assert auto.AUTO.balanceOf(auto.CHARLIE) == (trade_output if output_token == auto.AUTO else 0)
            assert auto.AUTO.balanceOf(auto.EXEC) == (fee_output if pay_with_AUTO else 0)
            assert auto.AUTO.balanceOf(uniLS) == 0
            assert auto.AUTO.balanceOf(auto.r) == 0
            assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == (MAX_UINT - allowance_used if input_token == auto.AUTO else 0)
            assert uniLS.getDefaultFeeInfo() == default_fee_info


def test_tokenToTokenStopLossPayDefault_rev_sender(a, auto, uniLS):
    for addr in list(a) + auto.all:
        if addr.address != auto.uff.address:
            with reverts(REV_MSG_USERFEEFORW):
                uniLS.tokenToTokenStopLossPayDefault(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, E_18, 1, 1, [], time.time() * 2, {'from': addr})