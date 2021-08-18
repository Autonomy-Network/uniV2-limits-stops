from consts import *
from brownie import a, reverts, Contract, web3, chain
from brownie.test import given, strategy
import time
from utils import *


def test_tokenToEthLimitOrderPayDefault_eth(auto, evmMaths, uni_router2, any, uniLS):
    path = [ANY_ADDR, WETH_ADDR]
    input_amount = int(10 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(init_output * 1.01)
    call_data = uniLS.tokenToEthLimitOrderPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, limit_output, path, time.time() * 2)
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
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**19
    uni_router2.swapExactETHForTokens(1, path[::-1], auto.WHALE, time.time()*2, {'value': whale_amount,'from': auto.WHALE})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO

    fee_output = evmMaths.mul3div1(EXPECTED_GAS, INIT_GAS_PRICE_FAST, PAY_ETH_BPS, BASE_BPS)
    trade_output = uni_router2.getAmountsOut(input_amount, path)[-1]

    # Execute successfully :D
    # Annoyingly, this fails for some reason, probably due to an issue with mainnet-fork in brownie. Assuming a gas
    # usage of 300k gas
    # expected_gas = auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost + trade_output - fee_output
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST) + fee_output
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


def test_tokenToEthLimitOrderPayDefault_AUTO(auto, evmMaths, uni_router2, any, uniLS):
    default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
    uniLS.setDefaultFeeInfo(default_fee_info)

    path = [ANY_ADDR, WETH_ADDR]
    input_amount = int(10 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(init_output * 1.1)
    call_data = uniLS.tokenToEthLimitOrderPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, limit_output, path, time.time() * 2)
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
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**19
    uni_router2.swapExactETHForTokens(1, path[::-1], auto.WHALE, time.time()*2, {'value': whale_amount,'from': auto.WHALE})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
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

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost + trade_output
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST)
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == MAX_UINT - input_amount
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == fee_output
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info


def test_tokenToEthLimitOrderPayDefault_AUTO_trade_AUTO(auto, evmMaths, uni_router2, any, uniLS):
    default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
    uniLS.setDefaultFeeInfo(default_fee_info)

    path = [auto.AUTO, WETH_ADDR]
    input_amount = int(10 * E_18)
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(init_output * 1.1)
    call_data = uniLS.tokenToEthLimitOrderPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, limit_output, path, time.time() * 2)
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
    assert auto.AUTO.balanceOf(auto.CHARLIE) == input_amount
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**19
    uni_router2.swapExactETHForTokens(1, path[::-1], auto.WHALE, time.time()*2, {'value': whale_amount,'from': auto.WHALE})
    assert uni_router2.getAmountsOut(input_amount, path)[-1] >= limit_output
    print(uni_router2.getAmountsOut(input_amount, path))

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
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

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost + trade_output
    assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST)
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == 0
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
    assert auto.AUTO.balanceOf(auto.EXEC) == fee_output
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == MAX_UINT - (input_amount - fee_input)
    assert uniLS.getDefaultFeeInfo() == default_fee_info


@given(
    input_token_is_AUTO=strategy('bool'),
    input_amount=strategy('uint', min_value=10000, max_value=INIT_ANY_BAL),
    whale_amount=strategy('uint', min_value=10000, max_value=INIT_ETH_BAL),
    expected_gas=strategy('uint', min_value=MIN_GAS, max_value=EXPECTED_GAS),
    pay_with_AUTO=strategy('bool')
)
def test_tokenToEthLimitOrderPayDefault_random(auto, evmMaths, uni_router2, any, uniLS, input_token_is_AUTO, input_amount, whale_amount, expected_gas, pay_with_AUTO):
    if pay_with_AUTO:
        default_fee_info = (UNIV2_ROUTER2_ADDR, (ADDR_0, auto.AUTO), True)
        uniLS.setDefaultFeeInfo(default_fee_info)
    else:
        default_fee_info = DEFAULT_FEE_INFO
    input_token = auto.AUTO if input_token_is_AUTO else any
    path = [input_token, WETH_ADDR]
    init_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(init_output * 1.1)
    call_data = uniLS.tokenToEthLimitOrderPayDefault.encode_input(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, input_amount, limit_output, path, time.time() * 2)
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
    assert auto.AUTO.balanceOf(auto.CHARLIE) == (input_amount if input_token == auto.AUTO else 0)
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    uni_router2.swapExactETHForTokens(1, path[::-1], auto.WHALE, time.time()*2, {'value': whale_amount,'from': auto.WHALE})

    assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost
    assert auto.EXEC.balance() == INIT_ETH_BAL
    assert uniLS.balance() == 0
    assert auto.r.balance() == 0
    assert any.balanceOf(auto.CHARLIE) == (input_amount if input_token == any else 0)
    assert any.balanceOf(auto.EXEC) == 0
    assert any.balanceOf(uniLS) == 0
    assert any.balanceOf(auto.r) == 0
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert auto.AUTO.balanceOf(auto.CHARLIE) == (input_amount if input_token == auto.AUTO else 0)
    assert auto.AUTO.balanceOf(auto.EXEC) == 0
    assert auto.AUTO.balanceOf(uniLS) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert uniLS.getDefaultFeeInfo() == default_fee_info

    if pay_with_AUTO:
        fee_output = get_AUTO_for_exec(evmMaths, expected_gas, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
        if input_token_is_AUTO:
            fee_input = fee_output
            allowance_used = input_amount - fee_input
            if input_amount >= fee_input + MIN_TRADE_AMOUNT:
                trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
        else:
            fee_input = uni_router2.swapTokensForExactTokens(fee_output, MAX_UINT, [any, WETH_ADDR, auto.AUTO], auto.WHALE, time.time()*2, auto.FR_WHALE).return_value[0]
            allowance_used = input_amount
            # Assumes the traded token is not AUTO
            if input_amount >= fee_input + MIN_TRADE_AMOUNT:
                trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
            chain.undo()
    else:
        fee_output = evmMaths.mul3div1(expected_gas, INIT_GAS_PRICE_FAST, PAY_ETH_BPS, BASE_BPS)
        allowance_used = input_amount
        fee_input = uni_router2.getAmountsIn(fee_output, path)[0]

    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    # Not enough ETH to pay the fee
    if input_amount < fee_input:
        with reverts():
            tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    # In the case of ETH to token where the token is less valuable, it shouldn't be an issue to
    # trade small amounts, just just to have a consistent testing method
    elif input_amount >= fee_input + MIN_TRADE_AMOUNT and cur_output < limit_output:
        with reverts(REV_MSG_UNI_OUTPUT):
            tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    elif input_amount >= fee_input + MIN_TRADE_AMOUNT and cur_output >= limit_output:
        assert uni_router2.getAmountsOut(input_amount, path)[-1] >= limit_output

        # if pay_with_AUTO:
        #     # Assumes the traded token is not AUTO
        #     trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
        # else:
        #     trade_output = uni_router2.getAmountsOut(input_amount - fee_input, path)[-1]
        
        tx = auto.r.executeHashedReq(0, req, expected_gas, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        
        # assert auto.CHARLIE.balance() == INIT_ETH_BAL - req_eth_cost + trade_output
        assert auto.EXEC.balance() == INIT_ETH_BAL - (tx.gas_used * INIT_GAS_PRICE_FAST) + (0 if pay_with_AUTO else fee_output)
        assert uniLS.balance() == 0
        assert auto.r.balance() == 0
        assert any.balanceOf(auto.CHARLIE) == 0
        assert any.balanceOf(auto.EXEC) == 0
        assert any.balanceOf(uniLS) == 0
        assert any.balanceOf(auto.r) == 0
        assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == (MAX_UINT - allowance_used if input_token == any else 0)
        assert auto.AUTO.balanceOf(auto.CHARLIE) == 0
        assert auto.AUTO.balanceOf(auto.EXEC) == (fee_output if pay_with_AUTO else 0)
        assert auto.AUTO.balanceOf(uniLS) == 0
        assert auto.AUTO.balanceOf(auto.r) == 0
        assert auto.AUTO.allowance(uniLS, UNIV2_ROUTER2_ADDR) == (MAX_UINT - allowance_used if input_token == auto.AUTO else 0)
        assert uniLS.getDefaultFeeInfo() == default_fee_info


def test_tokenToEthLimitOrderPayDefault_rev_sender(a, auto, uniLS):
    for addr in list(a) + auto.all:
        if addr.address != auto.uff.address:
            with reverts(REV_MSG_USERFEEFORW):
                uniLS.tokenToEthLimitOrderPayDefault(auto.CHARLIE, MIN_GAS, UNIV2_ROUTER2_ADDR, E_18, 1, [], time.time() * 2, {'from': addr})