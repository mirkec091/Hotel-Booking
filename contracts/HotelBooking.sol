// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract HotelBooking is VRFConsumerBase {
    // it is posible to rseserve only whole weeek ...52 weeks /year
    // number of room   uint8
    // maping weekNumber >> room number  >> is Available
    mapping(uint8 => mapping(uint8 => bool)) public weeks_reservation;
    // maping weekNumber >> room number  >> room key
    mapping(uint8 => mapping(uint8 => uint256)) internal room_keys;
    // maping weekNumber >> room number  >> addres of guest
    mapping(uint8 => mapping(uint8 => address)) public guests_data;
    uint8 standardRoom = 50;
    uint8 economyRoom = 100;
    uint8 exclusiveRoom = 150;
    uint8[13] public roomNumbers = [
        1,
        2,
        3,
        4,
        101,
        102,
        103,
        104,
        105,
        201,
        202,
        203,
        204
    ];
    uint8 lastReservedDate;
    uint8 lastReservedRoom;
    address contractOwner;
    AggregatorV3Interface public priceFeed;

    uint256 public fee;
    bytes32 public keyhash;
    uint256 public randomness;
    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeed,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        fee = _fee;
        keyhash = _keyhash;
        contractOwner = msg.sender;
    }

    function get_owner() public view returns (address) {
        return contractOwner;
    }

    function changRoomPrice(
        uint8 _standardRoom,
        uint8 _economyRoom,
        uint8 _exclusiveRoom
    ) public {
        require(msg.sender == contractOwner);
        standardRoom = _standardRoom;
        economyRoom = _economyRoom;
        exclusiveRoom = _exclusiveRoom;
    }

    function showBalance() public view returns (uint256) {
        require(msg.sender == contractOwner);
        return address(this).balance;
    }

    function transfer(address payable _receiver, uint256 amount) public {
        require(msg.sender == contractOwner);
        require(
            address(this).balance >= amount,
            "Not enough ethers in contract"
        );
        _receiver.transfer(amount);
    }

    function isReserved(uint8 _weekNumber, uint8 _room)
        public
        view
        returns (bool)
    {
        return weeks_reservation[_weekNumber][_room];
    }

    function checkReservation(uint8 _weekNumber, uint8 _room)
        public
        view
        returns (bool)
    {
        require(
            (guests_data[_weekNumber][_room] == (msg.sender)) ||
                (msg.sender == contractOwner),
            "You did not reserve this room"
        );
        return weeks_reservation[_weekNumber][_room];
    }

    function getKey(uint8 _weekNumber, uint8 _room)
        public
        view
        returns (uint256)
    {
        require(
            (guests_data[_weekNumber][_room] == (msg.sender)) ||
                (msg.sender == contractOwner),
            "You did not reserve this room"
        );
        return room_keys[_weekNumber][_room];
    }

    function reserve(uint8 _week, uint8 _room) public payable {
        require(
            weeks_reservation[_week][_room] == false,
            "Sorry,this room is not available this week"
        );
        require(((_week < 53) && (0 < _week)), "Wrong week is selected");
        // loop through all `room numbers
        bool roomFound = false;
        for (uint256 i; i < roomNumbers.length; i++) {
            if (roomNumbers[i] == _room) {
                // requested room found
                roomFound = true;
            }
        }
        require(roomFound, "No existing room is selected");
        // pay is done with eths
        // price of rooms "1-4" is standardRoom,"101-105" ..economyRoom and 201-204..exclusive
        if (_room < 100) {
            require(msg.value >= getRoomFee(standardRoom), "Not enough funds");
        }
        if ((100 < _room) && (_room < 200)) {
            require(msg.value >= getRoomFee(economyRoom), "Not enough funds");
        }
        if (_room > 200) {
            require(msg.value >= getRoomFee(exclusiveRoom), "Not enough funds");
        }
        weeks_reservation[_week][_room] = true;
        guests_data[_week][_room] = msg.sender;
        lastReservedDate = _week;
        lastReservedRoom = _room;
    }

    function cancelReservation(uint8 _weekNumber, uint8 _room) public {
        require(msg.sender == contractOwner);
        weeks_reservation[_weekNumber][_room] = false;
    }

    function getPrice() public view returns (uint256) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        return uint256(answer * 10000000000);
    }

    function get_randomness() public view returns (uint256) {
        return randomness;
    }

    function getConversionRate(uint256 ethAmount)
        public
        view
        returns (uint256)
    {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / (10**18);
        return ethAmountInUsd;
    }

    function getRoomFee(uint256 _roomPriceUSD) public view returns (uint256) {
        // price of the room
        uint256 priceUSD = _roomPriceUSD * 10**18;
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        /// because of rounding error we add "1"
        return ((priceUSD * precision) / price);
    }

    function genereteKeyRoom(uint8 _week, uint8 _room) public {
        require(
            guests_data[_week][_room] == msg.sender,
            " you did not reserve this room"
        );
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    /// this function is called by vrf coordinator ( chainlink)
    function fulfillRandomness(bytes32 requestId, uint256 _randomness)
        internal
        override
    {
        require(_randomness > 0, "random-not-found");

        randomness = _randomness;
        room_keys[lastReservedDate][lastReservedRoom] = _randomness % 10000;
    }
}
