 # FoodServer
 **English** A basic back-end system for restaurants, where orders can be made through an REST API in local network.

 **Português** Um sistema de back-end básico para restaurantes, onde pedidos podem ser feitos por API REST na rede local.
 
 ## API structure
 
 ### URL 'api/order'
 ***method:***
 GET
 
 ***parameters:***

 | field | type | requirement |
 |-------|------|-------------|
 | table | integer | optional |

If no parameter is passed, the API returns all entries
 
 ***body:*** 

 -Empty-
 
 ***It returns the following JSON:***

```
{
  "order": integer,
 "products": {"product1": integer, "product2": integer, ...},
 "table": integer,
 "status": string
 }
```
 

 ___________________________________________________________
***method:***
POST

***parameters:***

-Empty-

***body:***

| field | type | requirement |
 |-------|------|-------------|
 | table | integer | mandatory |
 | products* | dict | mandatory |
 | status | string | mandatory |

*Each key in the products dictionary must be named "product" + an number enumerating the product

Example:
```
{
 "products": {"product1": 5, "product2": 11},
 "table": 2,
 "status": "WA"
} 
 ```
 
 ***It returns the following JSON:***

```
 {
  "status": "Order placed!"
 }
 ```

  ___________________________________________________________
***method:***
PUT

***parameters:***

-Empty

***body:***

| field | type | requirement |
 |-------|------|-------------|
 | id | integer | mandatory |
 | table | integer | mandatory |
 | products* | dict | mandatory |
 | status | string | mandatory |

*Each key in the products dictionary must be named "product" + an number enumerating the product

Example:

```
{"id": 2,
 "products": {"product1": 4, "product2": 13},
 "table": 6,
 "status": "PP"}
 ``` 
 
 ***It returns the following JSON:***
```
 {
  "status": "Order updated!"
 }
```
 
 ___________________________________________________________
 ***method:***
DELETE

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

 | field | type | requirement |
 |-------|------|-------------|
 | table | integer | mandatory |

 Example:
 ```
{
  "table: 4
}
 ```
 
 ***It returns the following JSON:***

```
 {
  "status": "Order canceled!"
 }
 ```
 
 
### URL 'api/product'
***method:***
GET

***parameters:***

| field | type | requirement |
 |-------|------|-------------|
 | id | integer | optional |

 If no parameter is passed, the API returns all entries

***body:*** 

-Empty- 
 
***It returns the following JSON:***

```
{
 "name": string,
 "description": string,
 "price": float
}
 ```

 ___________________________________________________________
 ***method:***
POST

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
| name | string | mandatory |
| description | string | mandatory |
| price | float | mandatory |
| cost | float | mandatory |
| picture* | string | mandatory |
| supplier | integer| mandatory |

*The picture field is the location configured for static files in Django settings

Example:

```
 {"name": "Soda", 
  "description": "Soda 350ml bottle", 
   "price": 3.56, 
   "cost": 2.41, 
   "picture": "/product/Soda1.jpg", 
   "supplier": 1}
 ```

 ***It returns the following JSON:***

```
 {
  "status": "New product successfully registered!"
 }
 ```
 
 ___________________________________________________________
 ***method:***
PUT

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
| id | integer | mandatory |
| name | string | mandatory |
| description | string | mandatory |
| price | float | mandatory |
| cost | float | mandatory |
| picture* | string | mandatory |
| supplier | integer| mandatory |

Example:

```
 {
  "id": 3, 
  "name": "Beef Wellington", 
  "description": "Wagyu beef, dough, mushrooms", 
  "price": 34.65, 
  "cost": 20.12, 
  "picture": "/products/BfWellington.jpg", 
  "supplier": 5
 }
 ```
 
 ***It returns the following JSON:***

```
 {
  "status": "Product successfully updated!"
 }
 ```

 ___________________________________________________________
 ***method:***
DELETE

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
| id | integer | mandatory |
 
 ***It returns the following JSON:***

```
 {
  "status": "Product successfully deleted!"
 }
 ```


 ### URL 'api/supplier'
 ***method:***
 GET

 ***parameters:***

| field | type | requirement |
 |-------|------|-------------|
| id | integer | optional |

If no parameter is passed, the API returns all entries

***body:*** 

-Empty-
 
***It returns the following JSON:***

```
{
  "name": string,
 "address": string,
 "phone": integer,
 "supply_type": string
}
 ```

 ___________________________________________________________
 ***method:***
POST

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
 | name | string | mandatory |
 | address | string | mandatory |
 | phone | integer | mandatory |
 | supply_type | string | mandatory |

 Example:

```
 {
  "name": " Happy Daisy",
 "address": "548 Farm Street, City-ST",
 "phone": 518798989,
 "supply_type": "Dairy products"
 }
 ```

 ***It returns the following JSON:***

```
 {
  "status": "New supplier successfully registered!"
 }
 ```

 ___________________________________________________________
 ***method:***
PUT

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
 | id | integer | mandatory |
 | name | string | mandatory |
 | address | string | mandatory |
 | phone | integer | mandatory |
 | supply_type | string | mandatory |

 Example:

```
 {
  "id": 4,
  "name": " Happy Daisy Inc.",
 "address": "538 Farm Street, City-ST",
 "phone": 518798989,
 "supply_type": "Dairy products"
 }
 ```

 ***It returns the following JSON:***

```
 {
  "status": "Supplier successfully updated!"
 }
 ```
 ___________________________________________________________
 ***method:***
DELETE

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
 | id | integer | mandatory |
  
  Example:

```
 {"id": 4}
 ```
 
 ***It returns the following JSON:***

```
 {
  "status": "Supplier deleted!"
 }
 ```


 ### URL 'api/messages'
 ***method:***
GET

 ***parameters:***

| field | type | requirement |
 |-------|------|-------------|
 | message_id | integer | optional |
 | sender | integer | optional |

 If no parameter is passed, the API returns all entries
 
 ***body:*** 

 -Empty-
 
 ***It returns the following JSON in case of error:***

```
 {
  "status": "Error retriving messages!"
 }
 ```
  ___________________________________________________________
   ***method:***
POST

 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
 | receiver | integer | mandatory |
 | sender | integer | mandatory |
 | date | date | mandatory |
 | subject | string | mandatory |
 | message | string | mandatory |

Example:

```
 {
  "sender": 2,
  "receiver": 5,
  "date": "2024-05-12",
  "subject": "Supplier Bill",
  "message": "Just a reminder to pay the supplier 2 before 12AM"
 }
```
 
 ***It returns the following JSON:***

```
 {
  "status": "Message sent!"
 }
 ```
  ___________________________________________________________
   ***method:***
DELETE

 ***parameters:***
 
 -Empty
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
 | message_id | integer | mandatory |

Example:
```
 {
  "message_id": 3
 }
 ```
 
 ***It returns the following JSON:***

```
 {
  "status": "Message deleted!"
 }
 ```
  ___________________________________________________________

 
 ### URL 'api/auth_token'
 ***method:***
 POST
 
 ***parameters:***
 
 -Empty-
 
 ***body:*** 

| field | type | requirement |
 |-------|------|-------------|
 | username | string | mandatory |
 | password | string | mandatory |

Example:
```
{
  "username": "Johnny3", 
  "password": "Ef44@"
} 
```

***It returns the following JSON:***

```
{
  "token": string 
}
```
