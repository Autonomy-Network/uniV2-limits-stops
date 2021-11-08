from consts import *
from brownie import a, reverts, Contract
from brownie.test import given, strategy
import time


@given(
    input_amount=strategy('uint', min_value=10000, max_value=INIT_ANY_BAL/2),
    # Can't know the current max output outside of the fcn, so having to use INIT_ETH_BAL
    min_output=strategy('uint', min_value=10000, max_value=INIT_ETH_BAL),
    max_output=strategy('uint', min_value=10000, max_value=INIT_ETH_BAL),
    whale_amount=strategy('uint', min_value=10000, max_value=INIT_ANY_BAL/2)
)
def test_tokenToEthStopLoss(auto, uni_router2, any, uniLS, input_amount, min_output, max_output, whale_amount):
    path = [ANY_ADDR, WETH_ADDR]
    call_data = uniLS.tokenToEthRange.encode_input(auto.CHARLIE, MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, input_amount, min_output, max_output, path, auto.CHARLIE, time.time() * 2)
    msg_value = int(0.01 * E_18)
    eth_start_bal = auto.CHARLIE.balance()
    req = (auto.CHARLIE.address, uniLS.address, ADDR_0, call_data, msg_value, 0, True, False, False)

    any.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    any.approve(uniLS, input_amount, auto.FR_CHARLIE)

    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    # Make the request
    tx = auto.r.newReq(uniLS, ADDR_0, call_data, 0, True, False, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    req_eth_cost = tx.gas_price * tx.gas_used
    assert auto.CHARLIE.balance() == INIT_ETH_BAL - msg_value - req_eth_cost
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert any.balanceOf(auto.CHARLIE) == input_amount
    assert uniLS.balance() == 0
    assert any.balanceOf(uniLS) == 0

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    uni_router2.swapExactTokensForETH(whale_amount, 1, path, auto.WHALE, time.time()*2, {'from': auto.WHALE})

    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    if cur_output < min_output:
        print('a')
        with reverts(REV_MSG_UNI_OUTPUT):
            auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    elif cur_output > max_output:
        print('b')
        with reverts(REV_MSG_PRICE_HIGH):
            auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
    else:
        print('c')
        # Execute successfully :D
        # expected_gas = auto.r.executeHashedReq.call(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})

        assert auto.CHARLIE.balance() >= eth_start_bal - msg_value - req_eth_cost + cur_output
        assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == MAX_UINT - input_amount
        assert any.balanceOf(auto.CHARLIE) == 0


def test_tokenToEthStopLoss_rev_input_approve(auto, uni_router2, any, uniLS):
    # For 1 ANY
    input_amount = E_18
    path = [ANY_ADDR, WETH_ADDR]
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(cur_output * 1.1)
    call_data = uniLS.tokenToEthRange.encode_input(auto.CHARLIE, MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, input_amount, limit_output, MAX_UINT, path, auto.CHARLIE, time.time() * 2)
    msg_value = int(0.01 * E_18)
    req = (auto.CHARLIE.address, uniLS.address, ADDR_0, call_data, msg_value, 0, True, False, False)

    any.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    # Make the request
    auto.r.newReq(uniLS, ADDR_0, call_data, 0, True, False, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    whale_amount = 10**22
    uni_router2.swapExactTokensForETH(whale_amount, 1, path, auto.WHALE, time.time()*2, {'from': auto.WHALE})

    eth_start_bal = auto.CHARLIE.balance()
    with reverts(REV_MSG_EXCEED_ALLOWANCE):
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_tokenToEthStopLoss_rev_sender(a, auto, uniLS):
    for addr in list(a) + auto.all:
        if addr.address != auto.uf.address:
            with reverts(REV_MSG_USERFORW):
                uniLS.tokenToEthRange(auto.CHARLIE, MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, 1, 1, MAX_UINT, [], auto.CHARLIE, time.time() * 2, {'from': addr})


@given(
    max_gas_price=strategy('uint', min_value=1, max_value=MAX_GAS_PRICE),
    gas_price=strategy('uint', min_value=1, max_value=MAX_GAS_PRICE)
)
def test_tokenToEthStopLoss_rev_gasPrice(a, auto, uniLS, max_gas_price, gas_price):
    if gas_price > max_gas_price:
        with reverts(REV_MSG_GASPRICE_HIGH):
            uniLS.tokenToEthRange(auto.CHARLIE, max_gas_price, UNIV2_ROUTER2_ADDR, 1, 1, MAX_UINT, [], auto.CHARLIE, time.time() * 2, {'from': auto.DEPLOYER, 'gasPrice': gas_price})