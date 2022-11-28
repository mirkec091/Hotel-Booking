from scripts.helpful_scripts import (
    get_account,
    fund_with_link,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)

from brownie import exceptions, network
from web3 import Web3
import pytest
import time


def test_price_of_room(hotelBooking_contract):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # price of ether configured in Mock is 2000 USD
    assert hotelBooking_contract.getConversionRate(1) == 2000
    # price of room for 50$  in Wei
    assert hotelBooking_contract.getRoomFee(50) == 25000000000000000
    assert hotelBooking_contract.getRoomFee(100) == 50000000000000000
    assert hotelBooking_contract.getRoomFee(150) == 75000000000000000


def test_change_of_price(hotelBooking_contract):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # new room prce are 15,30 i 50 USD
    hotelBooking_contract.changRoomPrice(45, 56, 79)
    # price of ether configured in Mock is 2000 USD
    # price of room for 50$  in Wei
    assert hotelBooking_contract.getRoomFee(15) == 7500000000000000
    assert hotelBooking_contract.getRoomFee(30) == 15000000000000000
    assert hotelBooking_contract.getRoomFee(50) == 25000000000000000


def test_is_room_reserved(hotelBooking_contract):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # room number 1 in week 1 is reserved?
    print(f"isReserved =  {hotelBooking_contract.isReserved(1,1)}")
    assert hotelBooking_contract.isReserved(1, 1) == False


def test_reserve_with_not_enough_eths(hotelBooking_contract):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # try to reserve a room 1 in week 1 without enough eths("1-4" are 50$)
    account1 = get_account(1)
    with pytest.raises(exceptions.VirtualMachineError):
        hotelBooking_contract.reserve(
            1, 1, {"from": account1, "value": hotelBooking_contract.getRoomFee(40)}
        )
    # try to reserve a room 101 in week 1 without enough eths ( "101-105" ..100$)
    account1 = get_account(1)
    with pytest.raises(exceptions.VirtualMachineError):
        hotelBooking_contract.reserve(
            1, 101, {"from": account1, "value": hotelBooking_contract.getRoomFee(90)}
        )
    # try to reserve a room 201 in week 1 without enough eths ( 201-204..150$)
    account1 = get_account(1)
    with pytest.raises(exceptions.VirtualMachineError):
        hotelBooking_contract.reserve(
            1, 201, {"from": account1, "value": hotelBooking_contract.getRoomFee(140)}
        )


def test_reserve_room(hotelBooking_contract):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # try to reserve a "room 101 in week 1" with enough eths
    account1 = get_account(1)
    hotelBooking_contract.reserve(
        1, 101, {"from": account1, "value": hotelBooking_contract.getRoomFee(100)}
    )
    ####       generate the key ( only guest can do it)
    # add link token to hotelBooking contract
    fund_with_link(hotelBooking_contract)
    # generate key from any address
    account2 = get_account(2)
    with pytest.raises(exceptions.VirtualMachineError):
        transaction = hotelBooking_contract.genereteKeyRoom(1, 101, {"from": account2})
    # guest generate key
    transaction = hotelBooking_contract.genereteKeyRoom(1, 101, {"from": account1})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 1234567
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, hotelBooking_contract.address, {"from": account1}
    )
    # random number is
    assert hotelBooking_contract.get_randomness() == STATIC_RNG
    # is the room reserved
    print(f"room 1,1 is reserved {hotelBooking_contract.isReserved(1, 101)}")
    assert hotelBooking_contract.isReserved(1, 101) == True

    # try to reserve already reserved room
    with pytest.raises(exceptions.VirtualMachineError):
        hotelBooking_contract.reserve(
            1, 101, {"from": account1, "value": hotelBooking_contract.getRoomFee(100)}
        )
    # get the key
    assert hotelBooking_contract.getKey(1, 101) == 4567

    # only conract owner and guest can get the key
    with pytest.raises(exceptions.VirtualMachineError):
        hotelBooking_contract.getKey(1, 101, {"from": account2})

    ######    only owner of the contract can send eths to any address
    assert hotelBooking_contract.showBalance() == 50000000000000000
    # not owner wants to use transfer function
    with pytest.raises(exceptions.VirtualMachineError):
        hotelBooking_contract.transfer(
            account1.address, hotelBooking_contract.getRoomFee(100), {"from": account2}
        )
    #  owner wants to use transfer function
    hotelBooking_contract.transfer(
        account1.address, hotelBooking_contract.getRoomFee(100)
    )

    assert hotelBooking_contract.showBalance() == 0
    ###### cancel reservation ( only owner)
    # not owner wants to cancel reservation
    with pytest.raises(exceptions.VirtualMachineError):
        hotelBooking_contract.cancelReservation(1, 101, {"from": account2})
    print(f"isReserved =  {hotelBooking_contract.isReserved(1,101)}")
    assert hotelBooking_contract.isReserved(1, 101) == True
    # owner wants to cancel reservation
    hotelBooking_contract.cancelReservation(1, 101)
    print(f"isReserved =  {hotelBooking_contract.isReserved(1,101)}")
    assert hotelBooking_contract.isReserved(1, 101) == False
