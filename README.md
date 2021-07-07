# DevOps Squad Project - Team Recommendations

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
  "product_id1": 1,
  "product_id2": 2,
  "relationship": "UP_SELL"
}
```
Note that relationship between ```{"product_id1": 1, "product_id2": 2}``` and ```{"product_id1": 2, "product_id2": 1}``` are different.   
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
```GET http://0.0.0.0:5000/recommendations/products/1/related-products/2```   
returns    
```
{
  "product_id1": 1,
  "product_id2": 2,
  "relationship": "UP_SELL"
}
```
If no relationship exits between given product ids, a 404 error will be issued  

### Update a recommendation between two product ids
```PUT http://0.0.0.0:5000/recommendations/products/1/related-products/2``` 
body  
```
{
  "product_id1": 1,
  "product_id2": 2,
  "relationship": "CROSS_SELL"
}
```
returns    
```
{
  "product_id1": 1,
  "product_id2": 2,
  "relationship": "CROSS_SELL"
}
```
If no relationship exits between given product ids, a 404 error will be issued 

### Delete a recommendation between two product ids
```DELETE http://0.0.0.0:5000/recommendations/products/1/related-products/2```
body
```
{
  "product_id1": 1,
  "product_id2": 2,
  "relationship": "CROSS_SELL"
}
```
If no relationship exits between given product ids, a 404 error will be issued

### List a recommendation between two product ids
```GET http://0.0.0.0:5000/recommendations/products/1/related-products/2```
body
```
{
  "product_id1": 1,
  "product_id2": 2,
  "relationship": "CROSS_SELL"
}
```
If no relationship exits between given product ids, a 404 error will be issued


## Team Member
* [Mandy Xu - mandy-cmd && emxxxm](https://github.com/mandy-cmd)
* [Sarah Lin - procrasprincess](https://github.com/procrasprincess)
* [Kefei Wu - Aurora1024](https://github.com/Aurora1024)
* [Vipul Goyal - vg2134](https://github.com/vg2134)
* [Yuyin Zhang - zyy9871](https://github.com/zyy9871)

