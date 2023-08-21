 # FoodServer
 **English** A basic back-end system for restaurants, where orders can be made through an REST API in local network.
 **Português** Um sistema de back-end básico para restaurantes, onde pedidos podem ser feitos por API REST na rede local.
 
 ## API structure
 
 ### URL 'api/order'
 ***method:***
 GET
 
 ***parameters:***
 "table": integer - (optional)
 
 ***body:*** 
 {}
 
 ***It returns the following:***
{"order": integer,
 "products": {"product1": integer, "product2": integer, ...},
 "table": integer,
 "status": string}
 

### ___________________________________________________________
***method:***
POST

***parameters:***


***body:***
{"products": {"product1": integer, "product2": integer, ...},
 "table": integer,
 "status": string} 
 
 ***It returns the following:***
 {"status": "Order placed!"}

 ### ___________________________________________________________
***method:***
PUT

***parameters:***


***body:***
{"id": integer,
 "products": {"product1": integer, "product2": integer, ...},
 "table": integer,
 "status": string} 
 
 ***It returns the following:***
 {"status": "Order updated!"}
 
### ___________________________________________________________
 ***method:***
DELETE

 ***parameters:***
 
 
 ***body:*** 
 {"table": integer}
 
 ***It returns the following:***
 {"status": "Order canceled!"}
 
 
### URL 'api/product'
***method:***
GET

***parameters:***
 "id": integer - (optional)

***body:*** 
{} 
 
***It returns the following:***
{"name": string
 "description": string
 "price": float}

### ___________________________________________________________
 ***method:***
POST

 ***parameters:***
 
 
 ***body:*** 
 {"name": string, 
  "description": string, 
   "price": float, 
   "cost": float, 
   "picture": string, 
   "supplier": integer}
 
 ***It returns the following:***
 {"status": "New product successfully registered!"}
 
### ___________________________________________________________
 ***method:***
PUT

 ***parameters:***
 
 
 ***body:*** 
 {"id": integer, 
  "name": string, 
  "description": string, 
  "price": float, 
  "cost": float, 
  "picture": string, 
  "supplier": integer}
 
 ***It returns the following:***
 {"status": "Product successfully updated!"}

### ___________________________________________________________
 ***method:***
DELETE

 ***parameters:***
 
 
 ***body:*** 
 {"id": integer}
 
 ***It returns the following:***
 {"status": "Product successfully deleted!"}
 
 ### URL 'api/auth_token'
 ***method:***
 POST
 
 ***parameters:***
 
 
 ***body:*** 
{"username": string, 
"password": string} 

***It returns the following:***
{ 'token' : string }
