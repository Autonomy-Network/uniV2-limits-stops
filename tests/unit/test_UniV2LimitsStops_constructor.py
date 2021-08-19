from consts import *


def test_constructor(auto, uniLS):
    assert uniLS.registry() == auto.r
    assert uniLS.userVeriForwarder() == auto.uf
    assert uniLS.userFeeVeriForwarder() == auto.uff
    assert uniLS.WETH() == WETH_ADDR
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO