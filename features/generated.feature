Feature: AI Generated Test Cases

  Scenario: Valid login test
    Given app is open When I login Then I see dashboard

  Scenario: Invalid username test
    Given app is open When I enter invalid credentials Then I get error message

  Scenario: Empty password test
    Given app is open When I enter valid username and empty password Then I get error message

