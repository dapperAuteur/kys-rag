# Back-End Coding Guidelines (Litestar/Python) - Data Sharing and Function Building

This section of the coding guidelines focuses on how data should be structured and shared within the Litestar back-end, as well as best practices for building functions.

## 1. Data Handling

###   1.1. Pydantic Models

* **Purpose:** Use Pydantic models for:
    * Data validation: Ensure incoming data conforms to the expected structure and types.
    * Data serialization: Convert Python objects to JSON for API responses.
    * Documentation: Pydantic models serve as a form of schema documentation.
* **Naming:**
    * Use PascalCase for model names (e.g., `UserCreate`, `ItemResponse`).
    * Model names should clearly indicate their purpose (e.g., `UserCreate` for data used to create a user, `ItemResponse` for the data returned in an item response).
* **Field Naming:**
    * Use camelCase for field names within Pydantic models (e.g., `firstName`, `itemId`, `createdAt`).
    * Be descriptive and meaningful.
    * Use consistent abbreviations (e.g., `id`, `desc`, `addr`).
    * For fields representing foreign keys or relationships, use the related model name with "Id" suffix (e.g., `userId`, `orderId`).
* **Data Types:**
    * Use specific data types from Pydantic and Python's `typing` module (e.g., `str`, `int`, `float`, `bool`, `datetime.datetime`, `List`, `Optional`).
    * Leverage Pydantic's validators to enforce data constraints (e.g., `constr` for string constraints, `conint` for integer constraints).
* **Example:**

    ```python
    from datetime import datetime
    from typing import List, Optional

    from pydantic import BaseModel, Field, validator

    class UserCreate(BaseModel):
        firstName: str = Field(..., min_length=2, max_length=50, example="John")
        lastName: str = Field(..., min_length=2, max_length=50, example="Doe")
        email: str = Field(..., example="john.doe@example.com")
        password: str = Field(..., min_length=8, example="password123")

        @validator("email")
        def validate_email(cls, value: str) -> str:
            if "@" not in value:
                raise ValueError("Invalid email format")
            return value

    class UserResponse(BaseModel):
        id: int
        firstName: str
        lastName: str
        email: str
        created_at: datetime
    
    class ItemCreate(BaseModel):
        name: str = Field(..., min_length=2, max_length=100, example="Example Item")
        description: Optional[str] = Field(None, max_length=500, example="An example item description")
        price: float = Field(..., gt=0, example=10.99)
    
    class ItemResponse(BaseModel):
        id: int
        name: str
        description: Optional[str]
        price: float
    ```

###   1.2. Data Transfer

* **Format:** Use JSON for all data transfer between the back-end and front-end.
* **Consistency:**
    * Maintain consistent data structures in API requests and responses.
    * Use the Pydantic models to define these structures.
* **API Responses:**
    * Return appropriate HTTP status codes to indicate the success or failure of a request.
    * Provide clear and informative error messages in the response body when necessary.
    * Structure responses consistently (e.g., always include a `data` field for successful responses and an `errors` field for error responses).
* **Example (Successful Response):**

    ```json
    {
        "data": {
            "id": 123,
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "created_at": "2024-10-27T10:00:00"
        }
    }
    ```

* **Example (Error Response):**

    ```json
    {
        "errors": [
            {
                "message": "Invalid email format",
                "field": "email"
            }
        ]
    }
    ```

## 2. Function Building

###   2.1. Function Naming

* Use descriptive and concise names.
* Use snake\_case for function names (e.g., `get_user`, `create_item`, `calculate_total`).
* Function names should clearly indicate what the function does.
* For utility functions, group them in modules and name them accordingly (e.g., `utils.security.hash_password()`).

###   2.2. Function Structure

* **Single Responsibility Principle:** Each function should have a single, well-defined purpose.
* **Function Length:** Keep functions relatively short and focused. Break down complex logic into smaller, more manageable functions.
* **Type Hinting:** Use type hints extensively to improve code readability and maintainability.
* **Docstrings:** Write clear and concise docstrings to explain the function's purpose, parameters, and return value.
* **Error Handling:**
    * Use `try...except` blocks to handle exceptions.
    * Raise specific exceptions when appropriate.
    * Log errors appropriately.
* **Asynchronous Functions:**
    * Use `async def` for functions that perform I/O-bound operations.
    * Use `await` to call other asynchronous functions.

###   2.3. Function Parameters

* Use descriptive and meaningful parameter names.
* Use type hints to specify the expected data type of each parameter.
* Use default values for optional parameters.
* Use Pydantic models for complex parameter validation (e.g., for request bodies).
* Limit the number of function parameters. If a function requires many parameters, consider using a Pydantic model or a data class to group them.

###   2.4. Return Values

* Be explicit about what a function returns.
* Use type hints to specify the return type.
* Return Pydantic models when returning data to the API.
* Return consistent data types.
* Handle potential errors and return appropriate error values or raise exceptions.

###   2.5. Litestar-Specific Considerations

* **Routes:**
    * Define API routes using Litestar's routing decorators (e.g., `@router.get()`, `@router.post()`).
    * Use clear and consistent route paths.
    * Follow RESTful principles for route design.
    * Use path parameters (`/items/{item_id}`) and query parameters (`/items?limit=10`) appropriately.
* **Dependencies:**
    * Use Litestar's dependency injection system to manage dependencies.
    * Define dependencies as functions or classes.
    * Use type hints to specify dependency types.
* **Middleware:**
    * Use middleware for cross-cutting concerns (e.g., authentication, logging, CORS).
    * Keep middleware functions focused and efficient.
* **Example (Litestar Route):**

    ```python
    from typing import List

    from litestar import Litestar, Router, get, post
    from litestar.exceptions import HTTPException
    from litestar.status_codes import HTTP_201_CREATED

    from models import Item, ItemCreate
    from database import items  # Assuming a simple in-memory store for example

    @get("/items", response_model=List[Item])
    async def get_items() -> List[Item]:
        """
        Retrieves a list of all items.
        """
        return items

    @post("/items", response_model=Item, status_code=HTTP_201_CREATED)
    async def create_item(data: ItemCreate) -> Item:
        """
        Creates a new item.
        """
        new_item = Item(id=len(items) + 1, **data.dict())
        items.append(new_item)
        return new_item

    @get("/items/{item_id:int}", response_model=Item)
    async def get_item(item_id: int) -> Item:
        """
        Retrieves a single item by its ID.
        """
        try:
            return items[item_id - 1]
        except IndexError:
            raise HTTPException(status_code=404, detail="Item not found")

    item_router = Router(path="/items", route_handlers=[get_items, create_item, get_item])

    app = Litestar(route_handlers=[item_router])
    ```

By adhering to these guidelines, you'll create a robust, maintainable, and well-structured back-end with Litestar.