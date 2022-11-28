Hotel booking Solidity smart contract

The Hotel booking smart contract  allows one to rent a hotel room. It allows someone to make a payment for a room if the room is vacant. After eth payment is made to the contract the funds are managed by the owner. 

-it is possible to reserve only whole weeek
-three typs of rooms are available:
        standardRoom (1-4)
        economyRoom  (101-105)
        exclusiveRoom (201-204)

-owner can change price of rooms ( default value 50,100 and 150 USD)

    -for price data ETH/USD, 
    -this smart contract uses Chainlink oracle/AggregatorV3Interface/Data Feeds
    - LINK token are added to the contract for Chainlink fees
-after reservation guest generates the room key (1-9999)
    -random number is provided by Chainlink  VRF 

-only owner and guest can get the key

Testing:

    -unit tests:
    -ganache local tests with mocks

    -integritiy tests:
    -goerli network tests


