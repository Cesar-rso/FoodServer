 # FoodServer
 **English** A basic back-end system for restaurants, where orders can be made through an REST API in local network.
 **Português** Um sistema de back-end básico para restaurantes, onde pedidos podem ser feitos por API REST na rede local.
 
 ## API structure
 
 ### URL 'api/check-order'
 ***method:***
 GET
 
 ***parameters:***
 "table": integer
 
 ***body:*** 
 {}
 
 ***It returns the following:***
{"order": order_number,
 "products": {"product1": product_id, "product2": product_id, ...},
 "table": table_number,
 "status": order_status}
 

### URL 'api/place'
***method:***
POST

***parameters:***


***body:***
{"products": {"product1": product_id, "product2": product_id, ...},
 "table": table_number,
 "status": order_status} 
 
 ***It returns the following:***  
 {"status": "Order placed!"}
 
 ### URL 'api/cancel'
 ***method:***
POST

 ***parameters:***
 
 
 ***body:*** 
 {"table": table_number}
 
 *** It returns the following: ***
 {"status": "Order canceled!"}
 
 
### URL 'api/product'
***method:***
GET

***parameters:***
 "id": integer

***body:*** 
{} 
 
***It returns the following:***
{"name": product_name
 "description": product_description
 "price": product_price}
 
 
 ### URL 'api/auth_token'
 ***method:***
 POST
 
 ***parameters:***
 
 
 ***body:*** 
{"username": username, 
"password": password} 

***It returns the following:***
{ 'token' : '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b' }
