Feature: Discussion Home
  In order to interact with my instructor and other learners
  As a course enrollee
  I want to access and browse the forums

  Scenario: User can access the discussion tab
    Given I visit the discussion tab
    Then I should see the discussion home screen

  Scenario: User can post threads and comments
    Given I visit the discussion tab
    Then I can post, read, and search in the forums with this text:
        | text                  |
        | hello world           |
        | goodbye cruel world   |

