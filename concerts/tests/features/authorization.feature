Feature: Authorization

  Scenario Outline: Unauthenticated user tries to access a protected page
    Given I am an unauthenticated user
    When I try to access a protected page <url_name>
    Then I get a 302 status code
    Then I am on the "account_login" page

    Examples: Our login required create pages
    | url_name                       |
    | concerts:artist-create         |
    | concerts:venue-create          |
    | concerts:concert-create        |
    | concerts:add-concert-review    |
    | concerts:attend-concert        |
    | concerts:unattend-concert      |
    | concerts:update-concert-review |
    | concerts:delete-concert-review |


  Scenario Outline: Authenticated user tries to access a protected page
    Given I have a registered user "Sam"
    Given "Sam" is logged in
    When I try to access a protected page <url_name>
    Then I should be able to view the page

    Examples: Our login required create pages
    | url_name                       |
    | concerts:artist-create         |
    | concerts:venue-create          |
    | concerts:concert-create        |
    | concerts:attend-concert        |
    | concerts:unattend-concert      |
