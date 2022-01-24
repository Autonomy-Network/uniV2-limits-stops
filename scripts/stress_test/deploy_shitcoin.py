from brownie import accounts, Token
import time
import os


USER = accounts.add(os.environ['STRESS_USER_PRIV'])
print(f'USER = {USER}')
PUBLISH_SOURCE = True


def main():
    USER.deploy(Token, "Shitcoin A", "SCA", USER, 1e27, publish_source=PUBLISH_SOURCE)
    USER.deploy(Token, "Shitcoin B", "SCB", USER, 1e27, publish_source=PUBLISH_SOURCE)