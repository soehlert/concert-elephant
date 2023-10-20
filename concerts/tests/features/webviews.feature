Feature: List Views

Scenario Outline: Authenticated user can view a list of entities
    Given I have a registered user "testuser"
    And "testuser" is logged in
    And there is a <entity_type> in the system
    When I request the list of <entity_type>
    Then the response status code should be 200

    Examples:
        | entity_type |
        | concert    |
        | artist     |
        | venue      |

Scenario Outline: Authenticated user can create entities
    Given I have a registered user "testuser"
    And "testuser" is logged in
    When I make a new <entity_type> with valid data
    Then the response status code should be 302

    Examples:
        | entity_type |
        | concert     |
        | artist      |
        | venue       |
        | review      |

Scenario Outline: Authenticated user can view details of entities
    Given I have a registered user "testuser"
    And "testuser" is logged in
    And there is a <entity_type> in the system
    When I request details for that <entity_type>
    Then the response status code should be 200

    Examples:
        | entity_type |
        | concert     |
        | artist      |
        | venue       |
        | review      |

Scenario: Authenticated user can attend a concert
    Given I have a registered user "testuser"
    And "testuser" is logged in
    And there is a concert in the system
    When I attend the concert
    Then the response status code should be 302

Scenario: Authenticated user can unattend a concert
    Given I have a registered user "testuser"
    And "testuser" is logged in
    And there is a concert in the system
    And I have attended the concert
    When I unattend the concert
    Then the response status code should be 302

Scenario Outline: Authenticated user cannot create entities with invalid data
    Given I have a registered user "testuser"
    And "testuser" is logged in
    When I attempt to make a new <entity_type> with data <invalid_data>
    Then the response status code should be 200
    Then I should see form errors in the response

    Examples:
        | entity_type | invalid_data                            |
        | concert     | { "artist": "", "venue": "" }           |
        | artist      | { "name": "" }                          |
        | venue       | { "name": "", "city": "", "state": "", "country": ""}|

