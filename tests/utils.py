# from consts import *
# import time


# def newReq_ethToTokenLimitOrder(auto, uni_router2, uniLS, input_amount, factor_change):
#     path = [WETH_ADDR, ANY_ADDR]
#     cur_output = uni_router2.getAmountsOut(input_amount, path)[-1]
#     limit_output = int(cur_output * factor_change)
#     call_data = uniLS.ethToTokenLimitOrder.encode_input(auto.CHARLIE, limit_output, path, auto.CHARLIE, time.time() * 2)
#     msg_value = input_amount + int(0.01 * E_18)
#     req = (auto.CHARLIE.address, uniLS.address, auto.DENICE.address, call_data, msg_value, input_amount, True, False)

#     # Make the request
#     auto.r.newReq(uniLS, auto.DENICE, call_data, input_amount, True, False, {'value': msg_value, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': auto.CHARLIE})
