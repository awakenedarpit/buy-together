# API Specification

## Project: Buy Together
**Base Path**: `/api/v1`  
**Protocol**: REST / JSON  
**Auth Header**: `Authorization: Bearer <JWT_ACCESS_TOKEN>`  

---

## 1. Authentication Endpoints

### 1.1 Register User
- **Method**: `POST`
- **Path**: `/api/v1/auth/register`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "name": "Arpit Sharma",
    "email": "arpit@example.com",
    "password": "SecurePassword123!",
    "role": "MEMBER"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "id": 1,
      "name": "Arpit Sharma",
      "email": "arpit@example.com",
      "role": "MEMBER",
      "created_at": "2026-10-04T12:00:00Z"
    }
    ```
  - `400 Bad Request`: Email already registered.
  - `422 Unprocessable Entity`: Validation failure (weak password, invalid email format).

### 1.2 Login User
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "arpit@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "name": "Arpit Sharma",
        "email": "arpit@example.com",
        "role": "MEMBER"
      }
    }
    ```
  - `401 Unauthorized`: Invalid email or password.

### 1.3 Get Current User Profile
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Access**: Authenticated (`MEMBER` or `MANAGER`)
- **Responses**:
  - `200 OK`: Returns current user object.
  - `401 Unauthorized`: Missing or expired token.

---

## 2. Natural Language Ingestion & Extraction

### 2.1 Submit Message (Ingest & Extract)
- **Method**: `POST`
- **Path**: `/api/v1/messages/`
- **Access**: Authenticated (`MEMBER` or `MANAGER`)
- **Request Body**:
  ```json
  {
    "text": "bhai 2 notebook aur ek blue pen"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "message": {
        "id": 10,
        "text": "bhai 2 notebook aur ek blue pen",
        "created_at": "2026-10-04T12:10:00Z"
      },
      "extracted_items": [
        {
          "id": 101,
          "message_id": 10,
          "name": "notebook",
          "variant": null,
          "quantity": 2,
          "unit": "piece",
          "unit_price": null,
          "status": "PENDING",
          "created_at": "2026-10-04T12:10:01Z"
        },
        {
          "id": 102,
          "message_id": 10,
          "name": "pen",
          "variant": "blue",
          "quantity": 1,
          "unit": "piece",
          "unit_price": null,
          "status": "PENDING",
          "created_at": "2026-10-04T12:10:01Z"
        }
      ]
    }
    ```
  - `400 Bad Request`: Empty message or invalid payload.
  - `502 Bad Gateway`: AI extraction service unavailable (message still saved safely).

---

## 3. Member Personal Requests Endpoints

### 3.1 Get My Requests
- **Method**: `GET`
- **Path**: `/api/v1/requests/my`
- **Access**: Authenticated (`MEMBER` or `MANAGER`)
- **Query Parameters**:
  - `status` (optional, filter by `PENDING`, `APPROVED`, `PURCHASED`, `REJECTED`)
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "id": 101,
        "message_id": 10,
        "name": "notebook",
        "variant": null,
        "quantity": 2,
        "unit": "piece",
        "unit_price": null,
        "status": "PENDING",
        "created_at": "2026-10-04T12:10:01Z",
        "updated_at": "2026-10-04T12:10:01Z"
      }
    ]
    ```

### 3.2 Update Personal Request Item
- **Method**: `PUT`
- **Path**: `/api/v1/requests/{id}`
- **Access**: Authenticated (Owner of the request only)
- **Request Body**:
  ```json
  {
    "name": "notebook",
    "variant": "ruled",
    "quantity": 3,
    "unit": "piece"
  }
  ```
- **Responses**:
  - `200 OK`: Returns updated request item object.
  - `403 Forbidden`: User does not own this item.
  - `404 Not Found`: Item ID not found.

### 3.3 Delete Personal Request Item
- **Method**: `DELETE`
- **Path**: `/api/v1/requests/{id}`
- **Access**: Authenticated (Owner of the request only)
- **Responses**:
  - `204 No Content`: Item deleted successfully.
  - `403 Forbidden`: User does not own this item.
  - `404 Not Found`: Item ID not found.

---

## 4. Manager Procurement & Financial Endpoints

### 4.1 Get All Member Requests (Breakdown)
- **Method**: `GET`
- **Path**: `/api/v1/manager/requests`
- **Access**: Manager Only (`MANAGER`)
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "id": 101,
        "user_id": 1,
        "user_name": "Arpit Sharma",
        "user_email": "arpit@example.com",
        "name": "notebook",
        "variant": null,
        "quantity": 2,
        "unit": "piece",
        "unit_price": 40.00,
        "total_price": 80.00,
        "status": "PENDING",
        "created_at": "2026-10-04T12:10:01Z"
      }
    ]
    ```
  - `403 Forbidden`: Authenticated user is not a manager.

### 4.2 Get Combined Purchasing Requirements
- **Method**: `GET`
- **Path**: `/api/v1/manager/combined`
- **Access**: Manager Only (`MANAGER`)
- **Responses**:
  - `200 OK`:
    ```json
    {
      "items": [
        {
          "name": "notebook",
          "variant": null,
          "unit": "piece",
          "total_quantity": 6,
          "unit_price": 40.00,
          "total_cost": 240.00,
          "request_count": 3,
          "member_names": ["Arpit Sharma", "Rahul Verma", "Priya Nair"],
          "status": "PENDING"
        },
        {
          "name": "pen",
          "variant": "blue",
          "unit": "piece",
          "total_quantity": 5,
          "unit_price": 10.00,
          "total_cost": 50.00,
          "request_count": 2,
          "member_names": ["Arpit Sharma", "Karan Johar"],
          "status": "PENDING"
        }
      ],
      "financial_summary": {
        "total_items_count": 2,
        "total_units_count": 11,
        "grand_total_cost": 290.00
      }
    }
    ```

### 4.3 Update Single Request Item Price
- **Method**: `PATCH`
- **Path**: `/api/v1/manager/requests/{id}/price`
- **Access**: Manager Only (`MANAGER`)
- **Request Body**:
  ```json
  {
    "unit_price": 40.00
  }
  ```
- **Responses**:
  - `200 OK`: Returns updated item with updated unit price.
  - `400 Bad Request`: Negative unit price.

### 4.4 Batch Update Unit Price by Item Signature
- **Method**: `PATCH`
- **Path**: `/api/v1/manager/items/batch-price`
- **Access**: Manager Only (`MANAGER`)
- **Request Body**:
  ```json
  {
    "name": "notebook",
    "variant": null,
    "unit": "piece",
    "unit_price": 40.00
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "updated_count": 3,
      "name": "notebook",
      "variant": null,
      "unit": "piece",
      "unit_price": 40.00
    }
    ```

### 4.5 Update Request Item Status
- **Method**: `PATCH`
- **Path**: `/api/v1/manager/requests/{id}/status`
- **Access**: Manager Only (`MANAGER`)
- **Request Body**:
  ```json
  {
    "status": "APPROVED"
  }
  ```
- **Responses**:
  - `200 OK`: Status updated successfully.
  - `422 Unprocessable Entity`: Invalid status value.
