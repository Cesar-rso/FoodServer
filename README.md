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
{"order": integer,
 "products": {"product1": integer, "product2": integer, ...},
 "table": integer,
 "status": string}
 

### URL 'api/place'
***method:***
POST

***parameters:***


***body:***
{"products": {"product1": integer, "product2": integer, ...},
 "table": integer,
 "status": string} 
 
 ***It returns the following:***
 {"status": "Order placed!"}
 
 ### URL 'api/cancel'
 ***method:***
POST

 ***parameters:***
 
 
 ***body:*** 
 {"table": integer}
 
 ***It returns the following:***
 {"status": "Order canceled!"}
 
 
### URL 'api/product'
***method:***
GET

***parameters:***
 "id": integer

***body:*** 
{} 
 
***It returns the following:***
{"name": string
 "description": string
 "price": float}
 
 
 ### URL 'api/auth_token'
 ***method:***
 POST
 
 ***parameters:***
 
 
 ***body:*** 
{"username": string, 
"password": string} 

***It returns the following:***
{ 'token' : string }
