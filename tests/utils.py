from consts import *
import time


# Get the amount of input needed in a trade such that a proceeding 2nd trade with a given
# input and output will be exact. Input token initial reserve, output token initial reserve,
# 2nd trade input amount, and 2nd trade output amount
def getInputAmountFromMinOutput(Ir1, Or1, Ia2, Oa2):
    a = 997000 * Oa2
    b = 1997000 * Oa2 * Ir1 + (997 ** 2) * Oa2 * Ia2
    c = (1000 ** 2) * Oa2 * (Ir1 ** 2) + 997000 * Oa2 * Ia2 * Ir1 - 997000 * Or1 * Ia2 * Ir1

    Ia1Pos = int((-b + math.sqrt((b ** 2) - (4 * a * c))) / (2 * a))
    Ia1Neg = int((-b - math.sqrt((b ** 2) - (4 * a * c))) / (2 * a))
    log('Ia1Pos = {}'.format(Ia1Pos), 'info')
    log('Ia1Neg = {}'.format(Ia1Neg), 'info')

    if Ia1Pos <= 0 and Ia1Neg <= 0:
        log('Ia1Pos = {}, Ia1Neg = {}'.format(Ia1Pos, Ia1Neg), 'error')
        return
    if Ia1Pos > 0 and Ia1Neg < 0:
        return Ia1Pos
    if Ia1Neg > 0 and Ia1Pos < 0:
        return Ia1Neg
    # If they're both positive, return the one with the lowest value to be conservative
    if Ia1Neg < Ia1Pos and Ia1Neg > 0:
        return Ia1Neg
    if Ia1Pos < Ia1Neg and Ia1Pos > 0:
        return Ia1Pos
    if Ia1Pos == Ia1Neg:
        return Ia1Pos
    # # All the cases should be covered above but default to what is most likely the + value