Feature: The recommendation store service back-end
    As a Recommendation Product Manager
    I need a RESTful catalog service
    So that I can keep track of all my recommendations

Background:
    Given the following recommendations
        | product_id       | recommendation_product_id | relationship |
        | 9       | 10      | UP_SELL      |
        | 3       | 10      | GO_TOGETHER  |
        | 6       | 8      | ACCESSORY  |



Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a recommendation and read a recommendation
    When I visit the "Home Page"
    And I set the "product_id" to "2"
    And I set the "recommendation_product_id" to "7"
    And I set the "relationship" to "UP_SELL"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "product_id" field
    And I press the "Clear" button
    Then the "product_id" field should be empty
    And the "recommendation_product_id" field should be empty
    And the "relationship" field should be empty
    When I paste the "product_id" field
    And I set the "recommendation_product_id" to "7"
    And I press the "Retrieve" button
    Then I should see "UP_SELL" in the "relationship" field
    

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "UP_SELL" in the results
    And I should see "GO_TOGETHER" in the results
    And I should not see "CROSS_SELL" in the results

Scenario: Search all UP_SELL for product id 9
    When I visit the "Home Page"
    And I set the "product_id" to "9"
    And I set the "relationship" to "UP_SELL"
    And I press the "Search" button
    Then I should see "UP_SELL" in the results
    And I should not see "CROSS_SELL" in the results
    And I should not see "GO_TOGETHER" in the results
    And I should not see "ACCESSORY" in the results

Scenario: Update a recommendation
    When I visit the "Home Page"
    And I set the "product_id" to "3"
    And I set the "recommendation_product_id" to "10"
    And I press the "Retrieve" button
    Then I should see "GO_TOGETHER" in the "relationship" field
    When I change "relationship" to "UP_SELL"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "product_id" field
    And I press the "Clear" button
    And I paste the "product_id" field
    And I set the "recommendation_product_id" to "10"
    And I press the "Retrieve" button
    Then I should see "UP_SELL" in the "relationship" field

Scenario: Delete a recommendation
    When I visit the "Home Page"
    And I set the "product_id" to "9"
    And I set the "recommendation_product_id" to "10"
    And I press the "Retrieve" button
    Then I should see "UP_SELL" in the "relationship" field
    When I press the "Delete" button
    Then I should see the message "Recommendation has been Deleted!"
    

