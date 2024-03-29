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
# REG_ADDR = '0xF2f9793f55c9DAA0b9ba784BC558D90e2035ba86'
# UF_ADDR = '0x39B9d6ee676ebA7fC7ABD2ef61A9910c1102a0F2'
# UFF_ADDR = '0x408D163EeC8451dF88c882A7FeA47c7b5286d1D5'
# tl_addr = '0xF64920bD9dF221FFAAC03e8a74255391EE7dFc30'
# WETH_ADDR = '0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d'
# UNIV2_ADDR = '0x1C232F01118CB8B424793ae03F870aa7D0ac7f77'

# Polygon mainnet
# REG_ADDR = '0x18d02301E534cab22267460eD8fBdf2B8382A3ff'
# UF_ADDR = '0x0457670781c6A779594572BE6D6DBdac1f75d5AD'
# UFF_ADDR = '0x9075ee07E1c41fbc5Ecd20f3061Acc534b39aa7b'
# tl_addr = '0x79E0fEc218BbfC89A70C92A289C451D1f8F59269'
# WETH_ADDR = '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270'
# UNIV2_ADDR = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'

# Fantom mainnet
REG_ADDR = '0x6e5Ec7f4C98B34e0aAAA02D8D2136e626ED33B10'
UF_ADDR = '0xD73909B3924Ec5b4677E31a445220820065377B6'
UFF_ADDR = '0x5f56BcdcCfcafD27b7E9e05D8bc663d3F2D74Fc3'
tl_addr = '0x33d57095b9d0cc2Fa8ef8384BBfe3fB8d526A76e'
WETH_ADDR = '0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83'
UNIV2_ADDR = '0x1b02da8cb0d097eb8d57a175b88c7d8b47997506'


publish = False

def main():        
    if publish:
        contract_address = '0xe392288087Be9BABa755B5349CE11Cf02310d85F'
        print('Publishing contract at {}'.format(contract_address))
        contract = UniV2LimitsStops.at(contract_address)
        UniV2LimitsStops.publish_source(contract)
    else:
        DEPLOYER = auto_accs[0]
        print(DEPLOYER)
        tl = Timelock.at(tl_addr)
        uniV2LimitsStops = DEPLOYER.deploy(UniV2LimitsStops, REG_ADDR, UF_ADDR, UFF_ADDR, WETH_ADDR, (UNIV2_ADDR, (ADDR_0, WETH_ADDR), False))
        uniV2LimitsStops.transferOwnership(tl, {'from': DEPLOYER})
        UniV2LimitsStops.publish_source(uniV2LimitsStops)
