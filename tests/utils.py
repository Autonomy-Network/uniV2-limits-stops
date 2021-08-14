from consts import *
import time
import math


# Get the amount of input needed in a trade such that a proceeding 2nd trade with a given
# input and output will be exact. Input token initial reserve, output token initial reserve,
# 2nd trade input amount, and 2nd trade output amount
def get_input_from_min_out2(init_in_bal, init_out_bal, in_amnt2, out_amnt2):
    a = 997000 * out_amnt2
    b = 1997000 * out_amnt2 * init_in_bal + (997 ** 2) * out_amnt2 * in_amnt2
    c = (1000 ** 2) * out_amnt2 * (init_in_bal ** 2) + 997000 * out_amnt2 * in_amnt2 * init_in_bal - 997000 * init_out_bal * in_amnt2 * init_in_bal

    in_amnt1_pos = int((-b + math.sqrt((b ** 2) - (4 * a * c))) / (2 * a))
    in_amnt1_neg = int((-b - math.sqrt((b ** 2) - (4 * a * c))) / (2 * a))
    print(f'in_amnt1_pos = {in_amnt1_pos}')
    print(f'in_amnt1_neg = {in_amnt1_neg}')

    if in_amnt1_pos <= 0 and in_amnt1_neg <= 0:
        print(f'Error, in_amnt1_pos = {in_amnt1_pos}, in_amnt1_neg = {in_amnt1_neg}')
        return
    if in_amnt1_pos > 0 and in_amnt1_neg < 0:
        return in_amnt1_pos
    if in_amnt1_neg > 0 and in_amnt1_pos < 0:
        return in_amnt1_neg
    # If they're both positive, return the one with the lowest value to be conservative
    if in_amnt1_neg < in_amnt1_pos and in_amnt1_neg > 0:
        return in_amnt1_neg
    if in_amnt1_pos < in_amnt1_neg and in_amnt1_pos > 0:
        return in_amnt1_pos
    if in_amnt1_pos == in_amnt1_neg:
        return in_amnt1_pos
    # # All the cases should be covered above but default to what is most likely the + value


# def move_market(path, in_amnt2, out_amnt2):
#     # Get the market price very close to the limit price
#     pair_addr = uni_factory.getPair(path[0], path[-1])
#     out_amnt1 = get_input_from_min_out2(pair[0].balanceOf(pair_addr), pair[-1].balanceOf(pair_addr), input_amount, init_output/LIMIT_FACTOR)
#     in_amnt1 = uni_router2.getAmountsOut(out_amnt1, path)[-1]
#     any.approve(uni_router2, in_amnt1, auto.FR_WHALE)
#     uni_router2.swapExactTokensForETH(in_amnt1, 1, path.reverse(), auto.WHALE, time.time()*2, auto.FR_WHALE)
#     assert limit_output*0.999 <= uni_router2.getAmountsOut(input_amount, path)[-1] <= limit_output


def get_AUTO_for_exec(evmMaths, expected_gas, AUTOPerETH, gasPriceFast):
    # Need to account for differences in division between Python and Solidity
    return evmMaths.mul4Div2(expected_gas, gasPriceFast, AUTOPerETH, PAY_AUTO_BPS, BASE_BPS, E_18)