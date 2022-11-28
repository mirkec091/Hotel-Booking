from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from brownie import network
from scripts.deploy_HotelBooking import deploy_Hotel_Booking
import pytest


@pytest.fixture()
def hotelBooking_contract():
    return deploy_Hotel_Booking()
