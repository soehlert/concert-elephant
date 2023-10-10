Feature: Concert Review Update

  Scenario: Successful review update by the original author
    Given I have a registered user Sam
    Given Sam is logged in
    And Sam has written a concert review
    When Sam tries to update Sam's concert review
    Then the review update should be successful

  Scenario: Unauthorized review update by a different user
    Given I have a registered user Carrie
    Given I have a registered user Sam
    Given Sam is logged in
    Given Carrie is logged in
    And Sam has written a concert review
    When Carrie tries to update Sam's concert review
    Then the response status code should be 403

  Scenario: Original author deletes their review
    Given I have a registered user Author
    And Author has written a concert review
    And Author is logged in
    When Author tries to delete Authors concert review
    Then the delete operation should be successful

  Scenario: Non-author tries to delete another user's review
    Given I have a registered user Author
    And Author has written a concert review
    And I have a registered user NonAuthor
    And NonAuthor is logged in
    When NonAuthor tries to delete Author's concert review
    Then the response status code should be 403
