@ui @smoke
Feature: Google Search
  As a user
  I want to search on Google
  So that I can find information

  Background:
    Given the browser is open on Google

  @positive
  Scenario: Search for a topic and see results
    When the user types "Selenium automation" in search box
    And the user presses Enter
    Then the results page should load
    And the URL should contain "search"

  @positive
  Scenario: Google homepage has search box
    Then the search box should be visible
    And the page title should contain "Google"

  @data-driven
  Scenario Outline: Search for different topics
    When the user types "<topic>" in search box
    And the user presses Enter
    Then the results page should load

    Examples:
      | topic              |
      | Python testing     |
      | Selenium WebDriver |
      | pytest framework   |