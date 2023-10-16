Feature: Autocomplete

  Scenario Outline: Testing Autocomplete features
    Given a <entity> named "<name>"
    When I search for a <entity> with the term "<term>" using the "<url_name>" URL
    Then I should receive a response containing "<expected>"

    Examples:
      | entity  | name                  | term     | url_name              | expected              |
      | artist  | Michael Jackson       | Mich     | artist-autocomplete   | Michael Jackson       |
      | venue   | Madison Square Garden | Madison  | venue-autocomplete    | Madison Square Garden |
      | opener  | Britney Spears        | Brit     | opener-autocomplete   | Britney Spears        |

    Scenario: Access artist detail through an AJAX request
      Given an artist named "John Doe"
      When I make an AJAX request to the detail page of artist "John Doe"
      Then I should receive a JSON response containing the name "John Doe"

    Scenario: Create an artist through an AJAX request
      Given I have a registered user Sam
      And Sam is logged in
      When I submit the artist creation form with name "John Doe" using AJAX
      Then I should receive a JSON response indicating success
      And the response should contain the artist id and name "John Doe"

    Scenario: Create a venue through an AJAX request
      Given I have a registered user "Sam"
      And "Sam" is logged in
      When I submit the venue creation form with name "Awesome Venue", city "New York", and country "US" using AJAX
      Then I should receive a JSON response indicating success
      And the response should contain the venue id, name "Awesome Venue", city "New York", and country "US"

    Scenario: View concert detail through an AJAX request
      Given a concert exists
      When I request the detail of the existing concert using AJAX
      Then I should receive a JSON response containing the correct concert details

    Scenario: Create a concert through an AJAX request
      Given I have a registered user "Sam"
      And "Sam" is logged in
      When I submit the concert creation form using AJAX
      Then I should receive a JSON response indicating success
