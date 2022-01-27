from brownie import accounts, UniV2LimitsStops
import sys
import yaml
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()


with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# BSC testnet
# WBNB_ADDR = '0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd'
# BSC mainnet
WBNB_ADDR = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
PANCAKE_ADDR = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

def main():
    UNI_DEPLOYER = accounts.add(cfg['AUTONOMY_PRIV'])
    print(UNI_DEPLOYER)
    uniLS = UniV2LimitsStops.at('0x8E43C20ff7E019Ee560a04d5a80CBDDf9f70EB7D')
    uniLS.setDefaultFeeInfo((PANCAKE_ADDR, (ADDR_0, WBNB_ADDR), False), {'from': UNI_DEPLOYER})
