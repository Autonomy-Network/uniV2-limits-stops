from brownie import accounts, UniV2LimitsStops, Registry, Contract, AUTO
import time
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
    SENDER = auto_accs[4]
    print(SENDER)
    uniLS = UniV2LimitsStops.at('0x0BD4762f46c56900fbc7F767673DD3ae48778fA0')
    r = Registry.at(REG_ADDR)
    uni = Contract.from_explorer(UNIV2_ADDR)
    # A bit of a hack to use AUTO since it's the only quick way to get something with the ERC20 interface for
    # calling approve with
    token = AUTO.at("0xFe143522938e253e5Feef14DB0732e9d96221D72")
    
    token.approve(uniLS, MAX_UINT, {'from': SENDER})
    path = [token, WETH_ADDR, "0xb75a80ED9d41D4fd57414645544D79020EF843C3"]
    # Using USDT which has 6 decimal places, annoyingly
    input_amount = int(100 * 10**6)
    init_output = uni.getAmountsOut(input_amount, path)[-1]
    call_data = uniLS.tokenToTokenRangePayDefault.encode_input(SENDER, MIN_GAS, 10**21, UNIV2_ADDR, input_amount, init_output, path, time.time() * 2)
    r.newReq(uniLS, ADDR_0, call_data, 0, True, True, False, {'value': 10**16, 'from': SENDER})
