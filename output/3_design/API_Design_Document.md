```markdown
# API Design Document - Warehouse Management System

This document specifies the APIs for the Warehouse Management System.  The system uses a RESTful API architecture.  All APIs are versioned (v1) to allow for future changes.  Responses are in JSON format.

## Authentication Service APIs (v1)

These APIs handle user authentication and authorization.

**1. User Login**

* **Endpoint:** `/v1/auth/login`
* **Method:** `POST`
* **Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```
* **Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 123
}
```
* **Response (401 Unauthorized):**
```json
{
  "error": "Invalid credentials"
}
```

**2. User Registration (for Admins only)**

* **Endpoint:** `/v1/auth/register`
* **Method:** `POST`
* **Request:**
```json
{
  "username": "newuser@example.com",
  "password": "securepassword",
  "role": "user" // or "admin"
}
```
* **Response (201 Created):**
```json
{
  "message": "User registered successfully"
}
```
* **Response (400 Bad Request):**
```json
{
  "error": "Username already exists"
}
```


## Inventory Management Service APIs (v1)

These APIs manage inventory information.

**1. Get Inventory Items**

* **Endpoint:** `/v1/inventory/items`
* **Method:** `GET`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Parameters:**
    * `page` (integer, optional): Page number for pagination
    * `pageSize` (integer, optional): Number of items per page
    * `name` (string, optional): Filter by item name
    * `code` (string, optional): Filter by item code
* **Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Product A",
      "code": "A123",
      "quantity": 100,
      "price": 10000,
      "supplier": "Supplier X"
    },
    // ...
  ],
  "total": 100,
  "page": 1,
  "pageSize": 20
}
```
* **Response (400 Bad Request):** Invalid pagination parameters
* **Response (401 Unauthorized):** Missing or invalid token

**2. Add Inventory Item**

* **Endpoint:** `/v1/inventory/items`
* **Method:** `POST`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Body:**
```json
{
  "name": "Product B",
  "code": "B456",
  "quantity": 50,
  "price": 5000,
  "supplier": "Supplier Y"
}
```
* **Response (201 Created):**
```json
{
  "id": 2,
  "message": "Item added successfully"
}
```
* **Response (400 Bad Request):** Missing or invalid data
* **Response (401 Unauthorized):** Missing or invalid token


**3. Update Inventory Item**

* **Endpoint:** `/v1/inventory/items/{id}`
* **Method:** `PUT`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Body:**  (Similar to Add Item, but only fields to be updated are included)
* **Response (200 OK):** `{ "message": "Item updated successfully" }`
* **Response (400 Bad Request):** Missing or invalid data, item not found
* **Response (401 Unauthorized):** Missing or invalid token


**4. Delete Inventory Item**

* **Endpoint:** `/v1/inventory/items/{id}`
* **Method:** `DELETE`
* **Request Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):** `{ "message": "Item deleted successfully" }`
* **Response (404 Not Found):** Item not found
* **Response (401 Unauthorized):** Missing or invalid token


## Warehouse Management Service APIs (v1)

These APIs manage warehouse transactions.


**1. Record Stock In**

* **Endpoint:** `/v1/warehouse/stockin`
* **Method:** `POST`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Body:**
```json
{
  "item_id": 1,
  "quantity": 20,
  "date": "2023-10-27",
  "notes": "New delivery"
}
```
* **Response (201 Created):** `{ "message": "Stock-in recorded successfully" }`
* **Response (400 Bad Request):** Missing or invalid data
* **Response (401 Unauthorized):** Missing or invalid token

**2. Record Stock Out**

* **Endpoint:** `/v1/warehouse/stockout`
* **Method:** `POST`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Body:** (similar to Stock In)
* **Response (201 Created):** `{ "message": "Stock-out recorded successfully" }`
* **Response (400 Bad Request):** Missing or invalid data, insufficient stock
* **Response (401 Unauthorized):** Missing or invalid token

**3. Get Transaction History**

* **Endpoint:** `/v1/warehouse/transactions`
* **Method:** `GET`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Parameters:** (similar to Get Inventory Items)
* **Response (200 OK):**  (Similar structure to Get Inventory Items)
* **Response (400 Bad Request):** Invalid pagination parameters
* **Response (401 Unauthorized):** Missing or invalid token


## Reporting Service APIs (v1)

These APIs provide reporting functionalities.

**1. Get Inventory Report**

* **Endpoint:** `/v1/reports/inventory`
* **Method:** `GET`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Parameters:** (similar to Get Inventory Items)
* **Response (200 OK):**  (Similar structure to Get Inventory Items)
* **Response (400 Bad Request):** Invalid parameters
* **Response (401 Unauthorized):** Missing or invalid token

**2. Get Transaction Report**

* **Endpoint:** `/v1/reports/transactions`
* **Method:** `GET`
* **Request Headers:** `Authorization: Bearer <token>`
* **Request Parameters:** (similar to Get Transaction History)
* **Response (200 OK):** (Similar structure to Get Transaction History)
* **Response (400 Bad Request):** Invalid parameters
* **Response (401 Unauthorized):** Missing or invalid token


## Error Handling

All APIs will return standard HTTP status codes.  Error responses will include a JSON object with an `error` field describing the problem.

## Pagination

For endpoints returning lists of items (inventory, transactions), pagination will be used to improve performance and handle large datasets.  The `page` and `pageSize` parameters control pagination.


```