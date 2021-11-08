from consts import *
from brownie import a, reverts, Contract
from brownie.test import given, strategy
import time


@given(
    input_amount=strategy('uint', min_value=10000, max_value=INIT_ANY_BAL/2),
    whale_amount=strategy('uint', min_value=10000, max_value=INIT_ETH_BAL)
)
def test_tokenToTokenLimitOrder(auto, uni_router2, any, dai, uniLS, input_amount, whale_amount):
    path = [ANY_ADDR, WETH_ADDR, DAI_ADDR]
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(cur_output * 1.1)
    call_data = uniLS.tokenToTokenRange.encode_input(auto.CHARLIE, MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, input_amount, limit_output, MAX_UINT, path, auto.CHARLIE, time.time() * 2)
    msg_value = int(0.01 * E_18)
    req = (auto.CHARLIE.address, uniLS.address, ADDR_0, call_data, msg_value, 0, True, False, False)

    any.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    any.approve(uniLS, input_amount, auto.FR_CHARLIE)
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    # Make the request
    auto.r.newReq(uniLS, ADDR_0, call_data, 0, True, False, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    uni_router2.swapExactETHForTokens(1, [WETH_ADDR, ANY_ADDR], auto.WHALE, time.time()*2, {'value': whale_amount, 'from': auto.WHALE})

    if uni_router2.getAmountsOut(input_amount, path)[-1] >= limit_output:
        # Execute successfully :D
        auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})
        assert dai.balanceOf(auto.CHARLIE) >= limit_output
        assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == MAX_UINT - input_amount
        assert any.balanceOf(auto.CHARLIE) == 0
    else:
        with reverts(REV_MSG_UNI_OUTPUT):
            auto.r.executeHashedReq(0, req, EXPECTED_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})



def test_tokenToTokenLimitOrder_rev_input_approve(auto, uni_router2, any, dai, uniLS):
    # For 1 ANY
    input_amount = E_18
    path = [ANY_ADDR, WETH_ADDR, DAI_ADDR]
    cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
    limit_output = int(cur_output * 1.1)
    call_data = uniLS.tokenToTokenRange.encode_input(auto.CHARLIE, MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, input_amount, limit_output, MAX_UINT, path, auto.CHARLIE, time.time() * 2)
    msg_value = int(0.01 * E_18)
    req = (auto.CHARLIE.address, uniLS.address, ADDR_0, call_data, msg_value, 0, True, False, False)

    any.transfer(auto.CHARLIE, input_amount, auto.FR_WHALE)
    assert any.allowance(uniLS, UNIV2_ROUTER2_ADDR) == 0
    assert dai.balanceOf(auto.CHARLIE) == 0
    # Make the request
    auto.r.newReq(uniLS, ADDR_0, call_data, 0, True, False, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})

    # Swap ANY to the Uniswap contract to make the price of ANY much cheaper
    eth_amount = 10**19
    uni_router2.swapExactETHForTokens(1, [WETH_ADDR, ANY_ADDR], auto.WHALE, time.time()*2, {'value': eth_amount, 'from': auto.WHALE})

    eth_start_bal = auto.CHARLIE.balance()
    with reverts(REV_MSG_EXCEED_ALLOWANCE):
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': auto.EXEC, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_tokenToTokenLimitOrder_rev_sender(a, auto, uniLS):
    for addr in list(a) + auto.all:
        if addr.address != auto.uf.address:
            with reverts(REV_MSG_USERFORW):
                uniLS.tokenToTokenRange(auto.CHARLIE, MAX_GAS_PRICE, UNIV2_ROUTER2_ADDR, 1, 1, [], auto.CHARLIE, time.time() * 2, {'from': addr})


@given(
    max_gas_price=strategy('uint', min_value=1, max_value=MAX_GAS_PRICE),
    gas_price=strategy('uint', min_value=1, max_value=MAX_GAS_PRICE)
)
def test_tokenToTokenLimitOrder_rev_gasPrice(a, auto, uniLS, max_gas_price, gas_price):
    if gas_price > max_gas_price:
        with reverts(REV_MSG_GASPRICE_HIGH):
            uniLS.tokenToTokenRange(auto.CHARLIE, max_gas_price, UNIV2_ROUTER2_ADDR, 1, 1, [], auto.CHARLIE, time.time() * 2, {'from': auto.DEPLOYER, 'gasPrice': gas_price})