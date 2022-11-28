from brownie import HotelBooking, config, network
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
import time


def deploy_Hotel_Booking():
    account = get_account()
    hotelBooking = HotelBooking.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Contract deployed to {hotelBooking.address}")
    return hotelBooking


def main():
    deploy_Hotel_Booking()
