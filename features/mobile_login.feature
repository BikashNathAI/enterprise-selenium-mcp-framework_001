@mobile
Feature: Mobile Login
  As a mobile app user
  I want to login with my credentials
  So that I can access my account

  Background:
    Given the mobile app login screen is open

  @smoke @positive
  Scenario: Successful login with valid credentials
    When the user enters mobile email "testuser@example.com"
    And the user enters mobile password "Test@1234"
    And the user taps the login button
    Then the mobile login should be successful
    And no error message should be displayed

  @negative
  Scenario: Failed login with wrong password
    When the user enters mobile email "testuser@example.com"
    And the user enters mobile password "wrongpassword"
    And the user taps the login button
    Then a mobile error message should appear
    And the error should say "Invalid email or password"

  @negative
  Scenario Outline: Login blocked for invalid inputs
    When the user enters mobile email "<email>"
    And the user enters mobile password "<password>"
    And the user taps the login button
    Then a mobile error message should appear

    Examples:
      | email                  | password   |
      | wrong@email.com        | Test@1234  |
      | testuser@example.com   | wrongpass  |
      |                        | Test@1234  |