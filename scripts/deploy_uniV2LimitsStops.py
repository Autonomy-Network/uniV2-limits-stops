from brownie import accounts, UniV2LimitsStops
import sys
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
# Annoyingly you need to use auto_accs in order to access the private keys directly,
# they can't be found via accounts[0] etc since it doesn't replace the accounts
# and the private keys of the default accounts can't be accessed directly
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)


def main():
    UNI_DEPLOYER = auto_accs[4]
    print(UNI_DEPLOYER)
    # Ropsten
    # FORWARDER_ADDR = '0xD1DEdEb7871F1dd55cA26746650378723c26Be5d'
    # Polygon testnet
    FORWARDER_ADDR = '0xb85050D4429c5923B4Bad4F8A9E5F3d08e2179db'
    uniV2LimitsStops = UNI_DEPLOYER.deploy(UniV2LimitsStops, FORWARDER_ADDR)
    # print(mockUniLimit.abi)