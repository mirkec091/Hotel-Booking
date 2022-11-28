from scripts.helpful_scripts import (
    get_account,
    fund_with_link,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
import time
from brownie import network, exceptions, HotelBooking
import pytest


def test_integration_deploy_HotelBooking(hotelBooking_contract):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # deploy form account 1
    # price of eth in usd
    assert hotelBooking_contract.getConversionRate(1) > 1000


def test_integration__reserveRoom():
    hotelBooking_contract = HotelBooking[-1]
    # try to reserve a "room 101 in week 1" with enough eths
    account = get_account()  # change .env file with guest address  account 2
    hotelBooking_contract.reserve(
        1, 101, {"from": account, "value": hotelBooking_contract.getRoomFee(100)}
    )
    # room number 101 in week 1 is reserved?
    print(f"isReserved =  {hotelBooking_contract.isReserved(1,101)}")
    assert hotelBooking_contract.isReserved(1, 101) == True
    # guest generate key
    # our contract must have link tokens for chainlink fee
    fund_with_link(hotelBooking_contract)
    hotelBooking_contract.genereteKeyRoom(1, 101, {"from": account})
    # get the key
    key = hotelBooking_contract.getKey(1, 101, {"from": account})
    print("key = ", key)
    assert key > 0


def test_integration_cancelReservation():
    hotelBooking_contract = HotelBooking[-1]
    # owner wants to cancel reservation  # change .env file
    account = get_account()
    hotelBooking_contract.cancelReservation(1, 101, {"from": account})
    assert hotelBooking_contract.isReserved(1, 101) == True
