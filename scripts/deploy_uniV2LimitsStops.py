from brownie import accounts, UniV2LimitsStops, Timelock
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
WETH_ADDR = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
UNIV2_ADDR = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

# Ropsten
# WETH_ADDR = '0xc778417E063141139Fce010982780140Aa0cD5Ab'
# UNIV2_ADDR = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

# Avalanche mainnet
# WETH_ADDR = '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7'
# UNIV2_ADDR = '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106'

# Avalanche testnet
# WETH_ADDR = '0xd00ae08403B9bbb9124bB305C09058E32C39A48c'
# UNIV2_ADDR = '0x2D99ABD9008Dc933ff5c0CD271B88309593aB921'

REG_ADDR = '0x18d087F8D22D409D3CD366AF00BD7AeF0BF225Db'
UF_ADDR = '0xcE675B50034a2304B01DC5e53787Ec77BB7965D4'
UFF_ADDR = '0x4F54277e6412504EBa0B259A9E4c69Dc7EE4bB9c'
tl_addr = '0x9Ce05ad236Ad29B9EF6597633201631c097c3f10'


def main():
    DEPLOYER = auto_accs[4]
    print(DEPLOYER)
    tl = Timelock.at(tl_addr)
    uniV2LimitsStops = DEPLOYER.deploy(UniV2LimitsStops, REG_ADDR, UF_ADDR, UFF_ADDR, WETH_ADDR, (UNIV2_ADDR, (ADDR_0, WETH_ADDR), False), publish_source=True)
    uniV2LimitsStops.transferOwnership(tl, {'from': DEPLOYER})
    