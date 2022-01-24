from brownie import accounts, chain, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock, UniV2LimitsStops
import time
import sys
import os
sys.path.append(os.path.abspath('tests'))
from consts import *
sys.path.pop()


HOUR = 60 * 60

AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)

# AVAX mainnet
TL_ADDR = '0xA9E74167a120B139eBdf0858401FFd85b64E4810'
UNIV2_ADDR = '0x60aE616a2155Ee3d9A68541Ba4544862310933d4'
UNIV2_LS_ADDR = '0xE3e761127cBD037E18186698a2733d1e71623ebE'
WETH_ADDR = '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7'


def main():
    DEPLOYER = auto_accs[4]
    FR_DEPLOYER = {"from": DEPLOYER}

    uni_ls = UniV2LimitsStops.at(UNIV2_LS_ADDR)
    tl = Timelock.at(TL_ADDR)

    callData = uni_ls.setDefaultFeeInfo.encode_input((UNIV2_ADDR, (ADDR_0, WETH_ADDR), False))
    exec_time = time.time() + (12 * HOUR) + 100
    print(exec_time)
    args = (uni_ls, 0, "", callData, 1642857744)
    # tl.queueTransaction(*args, FR_DEPLOYER)

    tl.executeTransaction(*args, FR_DEPLOYER)