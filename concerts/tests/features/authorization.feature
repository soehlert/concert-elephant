Feature: Authentication

  Scenario: Unauthenticated user tries to access a protected page
     Given I am an unauthenticated user
     When I try to access a protected page
     Then I should be redirected to the login page

  Scenario: Authenticated user tries to access a protected page
     Given I have valid credentials
     When I login and access a protected page
     Then I should be able to view the page
