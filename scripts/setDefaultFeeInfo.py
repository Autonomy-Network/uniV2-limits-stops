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
# WBNB_ADDR = '0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd'
# BSC mainnet
WBNB_ADDR = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
PANCAKE_ADDR = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

def main():
    UNI_DEPLOYER = auto_accs[4]
    print(UNI_DEPLOYER)
    uniLS = UniV2LimitsStops.at('0x8E43C20ff7E019Ee560a04d5a80CBDDf9f70EB7D')
    uniLS.setDefaultFeeInfo((PANCAKE_ADDR, (ADDR_0, WBNB_ADDR), False), {'from': UNI_DEPLOYER})