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
# WETH_ADDR = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
# UNIV2_ADDR = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
# tl_addr = '0x9Ce05ad236Ad29B9EF6597633201631c097c3f10'

# Ropsten
# WETH_ADDR = '0xc778417E063141139Fce010982780140Aa0cD5Ab'
# UNIV2_ADDR = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

# Avalanche mainnet
# REG_ADDR = '0x5d30C97498F1F81e4A57386Ebea7aC8E3892fb5d'
# UF_ADDR = '0x45b125e4B53621AC16DFbde155380feE988de48a'
# UFF_ADDR = '0xF2f9793f55c9DAA0b9ba784BC558D90e2035ba86'
# tl_addr = '0xA22de268AE155ce9EaC33124890d91294d694497'
# WETH_ADDR = '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7'
# UNIV2_ADDR = '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106'

# Avalanche testnet
# REG_ADDR = '0x57c11ED54e9980E2b02cd6C08fB317d8fF47CA4e'
# UF_ADDR = '0x3d3F8FBc739679Bc499E769d2500c74b9e95C82b'
# UFF_ADDR = '0x1fd3D9d81366dC8278dABa5C5e9706DBE182E4c3'
# tl_addr = '0xfe836357b4c31798C65265D177C0412A5138abfE'
# WETH_ADDR = '0xd00ae08403B9bbb9124bB305C09058E32C39A48c'
# UNIV2_ADDR = '0x2D99ABD9008Dc933ff5c0CD271B88309593aB921'

# Celo testnet
REG_ADDR = '0x31c2E48FDBd0906dF00218091CBF6181AabAbB5A'
UF_ADDR = '0x55f0CB43B438e0C58808770cDBC7C01e9c8B5a46'
UFF_ADDR = '0x2b6CB704f78Bf83275f12645340De9614C7580A4'
tl_addr = '0x8e12602D84c4bc0Ad7c5c2117B7f7903222A8020'
WETH_ADDR = '0xF194afDf50B03e69Bd7D057c1Aa9e10c9954E4C9'
UNIV2_ADDR = '0x2D99ABD9008Dc933ff5c0CD271B88309593aB921'

# Celo mainnet
# REG_ADDR = ''
# UF_ADDR = ''
# UFF_ADDR = ''
# tl_addr = ''
# WETH_ADDR = '0x471EcE3750Da237f93B8E339c536989b8978a438'
# UNIV2_ADDR = ''

PUBLISH_SOURCE = False

def main():
    DEPLOYER = auto_accs[4]
    print(DEPLOYER)
    tl = Timelock.at(tl_addr)
    uniV2LimitsStops = DEPLOYER.deploy(UniV2LimitsStops, REG_ADDR, UF_ADDR, UFF_ADDR, WETH_ADDR, (UNIV2_ADDR, (ADDR_0, WETH_ADDR), False), publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    uniV2LimitsStops.transferOwnership(tl, {'gas_limit': 1e7, 'from': DEPLOYER})
