from consts import *
from utils import *


def test_get_input_from_min_out2(auto, uni_router2, any):
    # ETH > ANY
    path = [WETH_ADDR, auto.AUTO]
    in_amnt2 = int(0.01 * E_18)
    cur_output = uni_router2.getAmountsOut(in_amnt2, path)[-1]
    print(f'cur_output = {cur_output/E_18}')
    out_amnt2 = int(cur_output * 0.99)
    print(f'out_amnt2 = {out_amnt2/E_18}')
    in_amnt1 = get_input_from_min_out2(INIT_PAIR_BAL_ETH, INIT_PAIR_BAL_AUTO, in_amnt2, out_amnt2)
    print(in_amnt1/E_18)
    uni_router2.swapExactETHForTokens(1, path, auto.CHARLIE, E_18, {'value': in_amnt1, 'from': auto.CHARLIE})

    assert out_amnt2 * (1 - ERROR_FACTOR) <= uni_router2.getAmountsOut(in_amnt2, path)[-1] <= out_amnt2 * (1 + ERROR_FACTOR)