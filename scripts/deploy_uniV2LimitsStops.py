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
# REG_ADDR = '0x2d2C856115911C0D14B9DBfe0FEaB1baBE358D77'
# UF_ADDR = '0x408D163EeC8451dF88c882A7FeA47c7b5286d1D5'
# UFF_ADDR = '0x5d30C97498F1F81e4A57386Ebea7aC8E3892fb5d'
# tl_addr = '0xa940dC2174cBDA069A1151896A7ef422D808494A'
# WETH_ADDR = '0xd00ae08403B9bbb9124bB305C09058E32C39A48c'
# UNIV2_ADDR = '0x2D99ABD9008Dc933ff5c0CD271B88309593aB921'

# xDai mainnet
REG_ADDR = '0xF2f9793f55c9DAA0b9ba784BC558D90e2035ba86'
UF_ADDR = '0x39B9d6ee676ebA7fC7ABD2ef61A9910c1102a0F2'
UFF_ADDR = '0x408D163EeC8451dF88c882A7FeA47c7b5286d1D5'
tl_addr = '0xF64920bD9dF221FFAAC03e8a74255391EE7dFc30'
WETH_ADDR = '0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d'
UNIV2_ADDR = '0x1C232F01118CB8B424793ae03F870aa7D0ac7f77'


def main():
    DEPLOYER = auto_accs[4]
    print(DEPLOYER)
    tl = Timelock.at(tl_addr)
    uniV2LimitsStops = DEPLOYER.deploy(UniV2LimitsStops, REG_ADDR, UF_ADDR, UFF_ADDR, WETH_ADDR, (UNIV2_ADDR, (ADDR_0, WETH_ADDR), False))
    uniV2LimitsStops.transferOwnership(tl, {'from': DEPLOYER})
    