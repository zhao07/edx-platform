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
        | text                              |
        | This post contains ASCII          |
        | Thís pøst çòñtáins Lätin-1 tæxt   |
        | ｲんﾉ丂 ｱo丂ｲ co刀ｲﾑﾉ刀丂 cﾌズ     |
        | 𝕋𝕙𝕚𝕤 𝕡𝕠𝕤𝕥 𝕔𝕠𝕟𝕥𝕒𝕚𝕟𝕤 𝕔𝕙𝕒𝕣𝕒𝕔𝕥𝕖𝕣𝕤 𝕠𝕦𝕥𝕤𝕚𝕕𝕖 𝕥𝕙𝕖 𝔹𝕄ℙ |
        | "\" This , post > contains < delimiter ] and [ other } special { characters ; that & may ' break things" |
        | This post contains %s string interpolation #{syntax} |
