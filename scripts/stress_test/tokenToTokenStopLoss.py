from brownie import accounts, Token, UniV2LimitsStops, Registry, Contract
from datetime import datetime
import logging
import sys
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()

USER = accounts.add(os.environ['STRESS_USER_PRIV'])
FR_USER = {'from': USER, 'required_confs':0}
print(f'USER = {USER}')


# AVAX testnet
REG_ADDR = '0xA0F25b796dD59E504077F87Caea1c0472Cd6b7b4'
UNI_LS_ADDR = '0x17F65b6f5853B99a16D4d643DA1632b69255CdF5'
WETH_ADDR = '0xd00ae08403B9bbb9124bB305C09058E32C39A48c'
UNIV2_ADDR = '0x2D99ABD9008Dc933ff5c0CD271B88309593aB921'
SCA_ADDR = '0x171ee22328a936d7e9D67Af0978fE973403F09c7'
SCB_ADDR = '0x25c0110ef543a51eDb3C857f7718746BD1681046'
DEADLINE = 2429910000
NUM_TRADES = 10000


uni_ls = UniV2LimitsStops.at(UNI_LS_ADDR)
r = Registry.at(REG_ADDR)
uni = Contract.from_explorer(UNIV2_ADDR)
sca = Token.at(SCA_ADDR)
scb = Token.at(SCB_ADDR)

logging.basicConfig(
    filename=f'user-requests-{datetime.now().strftime("%Y-%m-%d")}.log',
    filemode='w',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s     %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('USER NEW REQUEST')


def approve(tokens, addrs_to_approve):
    for token in tokens:
        for addr in addrs_to_approve:
            if token.allowance(USER, addr) < MAX_UINT/2:
                token.approve(addr, MAX_UINT, FR_USER)


def main():
    approve([sca, scb], [uni_ls])
    start_id = r.getHashedReqsLen()
    for i in range(start_id, start_id + NUM_TRADES):
        path = [SCA_ADDR, SCB_ADDR]
        # + i so that the id is visible just looking at the executed request
        input_amount = E_18 + i
        init_output = uni.getAmountsOut(input_amount, path)[-1]
        # The stop loss should trigger when the price falls 1% below its current price
        max_output = int(init_output * 0.9)
        call_data = uni_ls.tokenToTokenRangePayDefault.encode_input(USER, 0, MAX_UINT, UNIV2_ADDR, input_amount, 1, max_output, path, DEADLINE)
        tx = r.newReq(uni_ls, ADDR_0, call_data, 0, True, True, False, FR_USER)
        logger.info(f'id = {i}, txid = {tx.txid}, input_amount = {input_amount}, stop_price = {max_output / input_amount}, current_price = {init_output / input_amount}')