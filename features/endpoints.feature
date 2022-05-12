
Feature: VIN API

    Scenario: User accesses lookup for VIN not in Cache
        When user accesses lookup endpoint with a new VIN
        Then endpoint should respond with vehicle info
        And vehicle info should indicate the data was not cached

    Scenario: User accesses lookup for invalid VIN
        When user accesses lookup endpoint with a invalid VIN
        Then Server should respond with 400 Client Error

    Scenario: User accesses lookup for VIN in Cache
        Given vehicle info is in cache
        When user accesses lookup endpoint with a new VIN
        Then endpoint should respond with vehicle info
        And vehicle info should indicate the data was cached

    Scenario: User accesses remove for VIN not in Cache
        When user accesses remove endpoint with a new VIN
        Then Endpoint should respond with success: false.
        And response should include VIN

    Scenario: User accesses remove for VIN in Cache
        Given vehicle info is in cache
        When user accesses remove endpoint with a new VIN
        Then endpoint should respond with success: true.
        And response should include VIN

    Scenario: User accesses remove for invalid VIN
        When user accesses remove endpoint with a invalid VIN
        Then server should respond with 400 Client Error

    Scenario: User accesses export while cache is empty
        When user accesses export endpoint
        Then server should respond with empty Parquet

    Scenario: User accesses export while cache contains 2 vehicles
        Given vehicle info is in cache
        And another vehicle's info is in cache
        When user accesses export endpoint
        Then server should respond with both vehicles in Parquet format
