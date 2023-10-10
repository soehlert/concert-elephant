Feature: API Endpoints

  @api @auth
  Scenario: Don't allow anonymous create
    Given I am an anonymous user
    When I create a new artist with {"name": "Test Artist"}
    Then the response status code should be 403

  @api
  Scenario Outline: Test list views
    Given I am an anonymous user
    When I request the <entity> list
    Then I should receive a list of entities

  Examples:
    | entity  |
    | artist  |
    | venue   |
    | concert |

  @api
  Scenario: Retrieve a user's concert reviews list
    Given I have a registered user Sam
    And Sam has created 3 concert reviews
    Given I have a registered user Alice
    When Alice requests the list of concert reviews for Sam
    Then the response should contain an empty list of reviews

  @api
  Scenario: Update a user's own concert review
    Given I have a registered user Sam
    And I am a token authenticated user Sam
    And Sam has created a concert review with note Original review and the rating 4
    When I update the concert review with note Updated review
    Then The concert review should be updated to Updated review

  @api
  Scenario: User cannot update another user's concert review
    Given I have a registered user Bob
    And I am a token authenticated user Bob
    And Bob has created a concert review with note Original review and the rating 4
    Given I have a registered user Dop
    And I am a token authenticated user Dop
    When Dop tries to update the concert review created by Bob with note Hacked review
    Then the response status code should be 404
    Then the concert review should be updated to Original review

  @api
  Scenario: Delete a user's own concert review
    Given I have a registered user Bob
    And I am a token authenticated user Bob
    And Bob has created a concert review with note Original Review and the rating 3
    When I delete the concert review
    Then The concert review should be removed from the database

  @api
  Scenario: User cannot delete another user's concert review
    Given I have a registered user Bob
    And I am a token authenticated user Bob
    And Bob has created a concert review with note Dope concert and the rating 4
    Given I have a registered user Sam
    And I am a token authenticated user Sam
    When I try to delete the concert review created by Bob
    Then the response status code should be 404

  @api @auth
  Scenario: End to end test
    Given I have a registered user Sam
    And I am a token authenticated user Sam
    When I create a new artist with {"name": "Test Artist"}
    Then The artist should be added to the database
    When I create a new venue with {"name": "Test Venue", "city": "Test City"}
    Then The venue should be added to the database
    When I create a new concert with {"title": "Test Concert", "date": "2023-10-10"}
    Then The concert should be added to the database
    When I create a new review with {"rating": 5, "note": "It was amazing!"}
    Then The review should be added to the database
