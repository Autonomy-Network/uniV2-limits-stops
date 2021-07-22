import pytest
from brownie import a
from consts import *
import time


# Test isolation
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# Deploy the contracts for repeated tests without having to redeploy each time

def deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner):
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
    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o, auto.AUTO)
    auto.vf = auto.DEPLOYER.deploy(Forwarder)
    auto.r = auto.DEPLOYER.deploy(
        Registry,
        auto.AUTO,
        auto.sm,
        auto.o,
        auto.vf
    )
    auto.vf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.m = auto.DEPLOYER.deploy(
        Miner,
        auto.AUTO,
        auto.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )

    return auto


@pytest.fixture(scope="module")
def auto(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner):
    return deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner)


@pytest.fixture(scope="module")
def uni_router2(auto):
    return Contract.from_explorer(UNIV2_ROUTER2_ADDR)


# Use ANY just because it's quite illiquid on UniswapV2 and therefore is easy to move the price
@pytest.fixture(scope="module")
def any(auto, UniV2LimitsStops):
    return Contract.from_explorer(ANY_ADDR)


@pytest.fixture(scope="module")
def dai(auto, UniV2LimitsStops):
    return Contract.from_explorer(DAI_ADDR)


@pytest.fixture(scope="module")
def uniLS(auto, any, dai, UniV2LimitsStops):
    uniLS =  auto.DEPLOYER.deploy(UniV2LimitsStops, auto.vf)

    # The top holder from https://etherscan.io/token/0xf99d58e463A2E07e5692127302C20A191861b4D6#balances
    # which is actually SushiSwap, so there should always be some tokens here
    whale = a.at('0xEc78bD3b23aC867FcC028f2db405A1d9A0A2f712', force=True)
    any.transfer(auto.WHALE, INIT_ANY_BAL, {'from': whale})
    assert any.balanceOf(auto.WHALE) == INIT_ANY_BAL

    return uniLS
