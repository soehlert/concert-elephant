Feature: Authorization

  Scenario: Unauthenticated user tries to access a protected page
    Given I am an unauthenticated user
    When I try to access a protected page
    Then I get a 302 status code
    Then I am on the "account_login" page

  Scenario: Authenticated user tries to access a protected page
    Given I have valid credentials
    When I login and access a protected page
    Then I should be able to view the page
