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

# BSC testnet
WBNB_ADDR = '0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd'

def main():
    UNI_DEPLOYER = auto_accs[4]
    print(UNI_DEPLOYER)
    REG_ADDR = '0xF2f9793f55c9DAA0b9ba784BC558D90e2035ba86'
    UF_ADDR = '0x39B9d6ee676ebA7fC7ABD2ef61A9910c1102a0F2'
    UFF_ADDR = '0x408D163EeC8451dF88c882A7FeA47c7b5286d1D5'
    uniV2LimitsStops = UNI_DEPLOYER.deploy(UniV2LimitsStops, REG_ADDR, UF_ADDR, UFF_ADDR, WBNB_ADDR, (WBNB_ADDR, (ADDR_0, WBNB_ADDR), False))
    print(uniV2LimitsStops.abi)