from consts import *
from brownie import chain, reverts
from brownie.test import given, strategy
from utils import *


@given(
    uni=strategy('address'),
    addr1=strategy('address'),
    addr2=strategy('address'),
    isAUTO=strategy('bool')
)
def test_setDefaultFee(auto, uni, uniLS, addr1, addr2, isAUTO):
    new_default_fee = (uni, (addr1, addr2), isAUTO)
    uniLS.setDefaultFeeInfo(new_default_fee, auto.FR_DEPLOYER)

    assert uniLS.getDefaultFeeInfo() == new_default_fee


@given(
    uni=strategy('address'),
    addr1=strategy('address'),
    addr2=strategy('address'),
    isAUTO=strategy('bool'),
    sender=strategy('address')
)
def test_setDefaultFeeInfo_rev_owner(auto, uni, uniLS, addr1, addr2, isAUTO, sender):
    if sender != auto.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            uniLS.setDefaultFeeInfo((uni, (addr1, addr2), isAUTO), {'from': sender})