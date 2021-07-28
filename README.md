# DevOps Squad Project - Team Recommendations

[![Build Status](https://travis-ci.com/dev-ops-recommendation/recommendations.svg?branch=main)](https://travis-ci.com/dev-ops-recommendation/recommendations)  [![codecov](https://codecov.io/gh/dev-ops-recommendation/recommendations/branch/main/graph/badge.svg?token=ILG2TMAKL8)](https://codecov.io/gh/dev-ops-recommendation/recommendations)

## Introduction
 In this DevOps project, each team will have  RESTful microservice that will be developed based on a resource from an eCommerce application. This is the repository for Team Recommendations.

<!-- ## Recommendations
The `recommendations resource` is a representation a product recommendation based on another product. 
* It's essentially a relationship between two products that "go together" (e.g., radio and batteries, printers and ink, shirts and pants, etc.). 
* It could also recommend based on what other customers have purchased like "customers who bought item A usually buy item B". 
* Recommendations should have a recommendation type like cross-sell, upsell, accessory, etc. This way a product page could request all of the up-sells for a product.

## Requirements 
This is the list of expected functions:

* List Resources
* Read a Resource
* Create a Resource
* Update a Resource
* Delete a Resource
* Query Resources by some attribute of the Resource
* Perform some stateful Action on the Resource -->
## How to Start Service
<!-- Run ```vagrant up && vagrant ssh``` and then ```cd /vagrant```   

<!-- Start server at 0.0.0.0:5000 ```FLASK_APP=service:app flask run -h 0.0.0.0``` -->

### Setup
Download and Install [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/).

### Start Server
```
$ git clone https://github.com/dev-ops-recommendation/recommendations
$ cd recommendations
$ vagrant up
$ vagrant ssh
$ cd /vagrant
$ FLASK_APP=service:app flask run -h 0.0.0.0
```
### Run TDD Unit Tests
```
$ nosetests
```

### Terminate Service
```
$ exit
$ vagrant halt
```



## Supported Operations
### Create a recommendation between two product ids
```POST http://0.0.0.0:5000/recommendations```  
body  
```
{
  "product_id": 1,
  "recommendation_product_id": 2,
  "relationship": "UP_SELL"
}
```
Note that relationship between ```{"product_id": 1, "recommendation_product_id": 2}``` and ```{"product_id": 2, "recommendation_product_id": 1}``` are different.   
This means that you could define different relationships for 1&2 and then for 2&1.      
If you are trying to create relationship for 1&2 while the relationship already exists, an error will be returned   
and indicate that the recommendation cannot be returned.   

Supported relationships are  
```
GO_TOGETHER 
CROSS_SELL 
UP_SELL
ACCESSORY 
```  
Other kinds of relationships will result in ```Cannot create relationship``` error

### Read a recommendation between two product ids
```GET http://0.0.0.0:5000/recommendations/1/recommended-products/2```   
returns    
```
{
  "likes": 0,
  "product_id": 1,
  "recommendation_product_id": 2,
  "relationship": "UP_SELL"
}
```
If no relationship exits between given product ids, a 404 error will be issued  

### Update a recommendation between two product ids
```PUT http://0.0.0.0:5000/recommendations/1/recommended-products/2``` 
body  
```
{
  "product_id": 1,
  "recommendation_product_id": 2,
  "relationship": "CROSS_SELL"
}
```
returns    
```
{
  "likes": 0,
  "product_id": 1,
  "recommendation_product_id": 2,
  "relationship": "CROSS_SELL"
}
```
If no relationship exits between given product ids, a 404 error will be issued 

### Delete a recommendation between two product ids
```DELETE http://0.0.0.0:5000/recommendations/1/recommended-products/2```
body
```
{
  "product_id": 1,
  "recommendation_product_id": 2,
  "relationship": "CROSS_SELL"
}
```


### Read a recommendation between two product ids
```GET http://0.0.0.0:5000/recommendations/1/recommended-products/2```
body
```
{
  "likes": 0,
  "product_id": 1,
  "recommendation_product_id": 2,
  "relationship": "CROSS_SELL"
}
```
If no relationship exits between given product ids, a 404 error will be issued

### Query recommendation of a product id for a certain type
Query endpoint takes a product id and relationship type. It will return empty list if no result or will return a list of relationship for input product_id and relationship type.   
Example result after creating relationship {1,2,UP_SELL}, {1,10,UP_SELL}, {1,15,CROSS_SELL}  
GET http://0.0.0.0:5000/recommendations/1?type=UP_SELL  
```
[
    {
        "likes": 0,
        "product_id": 1,
        "recommendation_product_id": 2,
        "relationship": "UP_SELL"
    },
    {
        "likes": 0,
        "product_id": 1,
        "recommendation_product_id": 10,
        "relationship": "UP_SELL"
    }
]
```

### Stateful Action - Like a Recommendation
When a recommendation is created, like count is default to 0  
To like an existing recommendation, call   
```PUT http://0.0.0.0:5000/recommendations/1/recommended-products/2/like```   
```
{
    "likes": 1,
    "product_id": 1,
    "recommendation_product_id": 2,
    "relationship": "UP_SELL"
}
```


### Clear all data entries
To reset the database, simply call   
DELETE http://0.0.0.0:5000/recommendations

All data entries will be cleared and GET http://0.0.0.0:5000/recommendations should return empty list now



## Team Member
* [Mandy Xu - mandy-cmd && emxxxm](https://github.com/mandy-cmd)
* [Sarah Lin - procrasprincess](https://github.com/procrasprincess)
* [Kefei Wu - Aurora1024](https://github.com/Aurora1024)
* [Vipul Goyal - vg2134](https://github.com/vg2134)
* [Yuyin Zhang - zyy9871](https://github.com/zyy9871)

