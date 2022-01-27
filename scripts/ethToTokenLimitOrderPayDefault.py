from brownie import accounts, UniV2LimitsStops, Registry, Contract
import time
import sys
import yaml
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()

with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# BSC testnet
# WETH_ADDR = '0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd'
# BSC mainnet
# WETH_ADDR = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
# UNIV2_ADDR = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
# REG_ADDR = '0x18d087F8D22D409D3CD366AF00BD7AeF0BF225Db'
# AVAX testnet
WETH_ADDR = '0xd00ae08403B9bbb9124bB305C09058E32C39A48c'
UNIV2_ADDR = '0x2D99ABD9008Dc933ff5c0CD271B88309593aB921'
REG_ADDR = '0x2d2C856115911C0D14B9DBfe0FEaB1baBE358D77'

def main():
    SENDER = accounts.add(cfg['AUTONOMY_PRIV'])
    print(SENDER)
    uniLS = UniV2LimitsStops.at('0x0BD4762f46c56900fbc7F767673DD3ae48778fA0')
    r = Registry.at(REG_ADDR)
    uni = Contract.from_explorer(UNIV2_ADDR)

    path = [WETH_ADDR, "0xFe143522938e253e5Feef14DB0732e9d96221D72"]
    input_amount = int(0.1 * E_18)
    init_output = uni.getAmountsOut(input_amount, path)[-1]
    call_data = uniLS.ethToTokenRangePayDefault.encode_input(SENDER, MIN_GAS, 10**21, MAX_UINT, UNIV2_ADDR, init_output, MAX_UINT, path, time.time() * 2)
    r.newReq(uniLS, ADDR_0, call_data, input_amount, True, True, False, {'value': input_amount + 10**16, 'from': SENDER})
