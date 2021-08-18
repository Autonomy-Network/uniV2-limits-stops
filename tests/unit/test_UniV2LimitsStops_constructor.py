from consts import *


def test_constructor(auto, uniLS):
    assert uniLS.getRegistry() == auto.r
    assert uniLS.getUserVerifiedForwarder() == auto.uf
    assert uniLS.getUserFeeVerifiedForwarder() == auto.uff
    assert uniLS.WETH() == WETH_ADDR
    assert uniLS.getDefaultFeeInfo() == DEFAULT_FEE_INFO