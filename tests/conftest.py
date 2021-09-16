import pytest
from brownie import a
from consts import *
import time


# Test isolation
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# Deploy the contracts for repeated tests without having to redeploy each time

def deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock):
    class Context:
        pass

    auto = Context()
    # It's a bit easier to not get mixed up with accounts if they're named
    # Can't define this in consts because a needs to be imported into the test
    auto.DEPLOYER = a[0]
    auto.FR_DEPLOYER = {"from": auto.DEPLOYER}
    auto.EXEC = a[1]
    auto.FR_EXEC = {"from": auto.EXEC}
    auto.WHALE = a[2]
    auto.FR_WHALE = {"from": auto.WHALE}
    auto.CHARLIE = a[3]
    auto.FR_CHARLIE = {"from": auto.CHARLIE}
    auto.DENICE = a[4]
    auto.FR_DENICE = {"from": auto.DENICE}
    
    auto.AUTO = auto.DEPLOYER.deploy(AUTO, "Autonomy Network", "AUTO")
    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o, auto.AUTO)
    auto.uf = auto.DEPLOYER.deploy(Forwarder)
    auto.ff = auto.DEPLOYER.deploy(Forwarder)
    auto.uff = auto.DEPLOYER.deploy(Forwarder)
    auto.r = auto.DEPLOYER.deploy(
        Registry,
        auto.AUTO,
        auto.sm,
        auto.o,
        auto.uf,
        auto.ff,
        auto.uff
    )
    auto.uf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.ff.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.uff.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.m = auto.DEPLOYER.deploy(
        Miner,
        auto.AUTO,
        auto.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )

    # Create timelock for OP owner
    auto.tl = auto.DEPLOYER.deploy(Timelock, auto.DEPLOYER, 2*DAY)
    auto.po.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.o.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.uf.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.ff.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.uff.transferOwnership(auto.tl, auto.FR_DEPLOYER)

    auto.all = [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m, auto.tl]
    
    auto.AUTO.approve(auto.r, MAX_UINT, auto.FR_CHARLIE)

    return auto


@pytest.fixture(scope="module")
def auto(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock):
    return deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock)


@pytest.fixture(scope="module")
def uni_factory(auto):
    return Contract.from_explorer(UNIV2_FACTORY_ADDR)


@pytest.fixture(scope="module")
def uni_router2(auto):
    uni = Contract.from_explorer(UNIV2_ROUTER2_ADDR)

    # Add an AUTO pool so that AUTO can be bought as the fee token
    auto.AUTO.approve(UNIV2_ROUTER2_ADDR, MAX_UINT, auto.FR_DEPLOYER)
    auto.AUTO.approve(UNIV2_ROUTER2_ADDR, MAX_UINT, auto.FR_WHALE)
    uni.addLiquidityETH(auto.AUTO, INIT_PAIR_BAL_AUTO, 1, 1, auto.DEPLOYER, time.time()*2, {'value': INIT_PAIR_BAL_ETH, 'from': auto.DEPLOYER})
    eth_input = int(0.0001*E_18)
    auto_output_max = int(eth_input*INIT_AUTO_PER_ETH)
    assert 0.99*auto_output_max <= uni.getAmountsOut(eth_input, [WETH_ADDR, auto.AUTO])[-1] <= auto_output_max

    return uni


# Using AUTO since it's a basic ERC20 anyway
@pytest.fixture(scope="module")
def weth(AUTO):
    return AUTO.at(WETH_ADDR)


@pytest.fixture(scope="module")
def dai(auto, UniV2LimitsStops):
    return Contract.from_explorer(DAI_ADDR)


# Use ANY just because it's quite illiquid on UniswapV2 and therefore is easy to move the price
@pytest.fixture(scope="module")
def any(auto, UniV2LimitsStops):
    return Contract.from_explorer(ANY_ADDR)


@pytest.fixture(scope="module")
def uniLS(auto, any, dai, uni_router2, UniV2LimitsStops):
    uniLS =  auto.DEPLOYER.deploy(UniV2LimitsStops, auto.r, auto.uf, auto.uff, WETH_ADDR, DEFAULT_FEE_INFO)
    uniLS.transferOwnership(auto.tl, auto.FR_DEPLOYER)

    # The top holder from https://etherscan.io/token/0xf99d58e463A2E07e5692127302C20A191861b4D6#balances
    # which is actually SushiSwap, so there should always be some tokens here
    whale = a.at('0xEc78bD3b23aC867FcC028f2db405A1d9A0A2f712', force=True)
    any.transfer(auto.WHALE, INIT_ANY_BAL, {'from': whale})
    assert any.balanceOf(auto.WHALE) == INIT_ANY_BAL
    any.approve(uni_router2, MAX_UINT, auto.FR_WHALE)

    auto.AUTO.transfer(auto.WHALE, int(INIT_AUTO_SUPPLY/10), auto.FR_DEPLOYER)
    auto.AUTO.approve(uni_router2, MAX_UINT, auto.FR_WHALE)

    dai_whale = a.at('0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True)
    dai.transfer(auto.WHALE, INIT_ANY_BAL, {'from': dai_whale})
    assert dai.balanceOf(auto.WHALE) == INIT_ANY_BAL
    dai.approve(uni_router2, MAX_UINT, auto.FR_WHALE)

    return uniLS


# Need to test gas usage with the exact same rounding profile that Solidity
# uses vs Python
@pytest.fixture(scope="module")
def evmMaths(auto, EVMMaths):
    return auto.DEPLOYER.deploy(EVMMaths)
    