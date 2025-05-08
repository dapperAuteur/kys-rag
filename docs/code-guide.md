# Coding Guidelines

This document outlines the coding guidelines for the KYS-RAG project, which features a Next.js (TypeScript) frontend and a Python backend. Following these guidelines will promote consistency, readability, and maintainability, making it easier for everyone to understand and contribute to the codebase.

## 1. General Principles

* **KISS (Keep It Simple, Stupid):** Aim for simplicity in your code. Avoid unnecessary complexity.
* **DRY (Don't Repeat Yourself):** Avoid duplicating code. Extract common logic into reusable functions or components.
* **YAGNI (You Ain't Gonna Need It):** Don't implement features or code that you think you might need in the future. Focus on the current requirements.
* **Code Readability:** Write code that is easy to understand. Use clear naming, comments, and formatting.

## 2. Project Structure

*   **General Overview:** Maintain a clear separation between frontend (`/frontend` or `/web`) and backend (`/backend` or `/api`) directories if not using a monorepo manager that dictates structure.
*   **Frontend (Next.js):**
    *   Follow Next.js App Router conventions primarily within its dedicated directory.
    *   Organize components, pages, services, and utilities logically.
*   **Backend (Python):**
    *   Structure the Python backend logically, for example:
        *   `src/` or `app/`: Main application code.
        *   `core/` or `common/`: Core logic, shared utilities.
        *   `models/` or `schemas/`: Data models, Pydantic schemas.
        *   `services/` or `use_cases/`: Business logic.
        *   `api/` or `routers/` or `endpoints/`: API route definitions.
        *   `tests/`: Unit and integration tests for the backend.
        *   `main.py` or `app.py`: Application entry point.

## 3. Language-Specific Guidelines

### 3.1. Frontend: TypeScript & Next.js

*   **Strict Typing:** Utilize TypeScript's strong typing features. Define types/interfaces for props, state, API responses, and function signatures.
*   **Interfaces and Types:** Prefer interfaces for public APIs and object shapes, types for unions, intersections, or more complex type manipulations.
*   **Enums:** Use enums for sets of related constants (e.g., status codes, roles).
*   **Async/Await:** Use `async/await` for asynchronous operations (e.g., data fetching).
*   **Error Handling:** Use `try...catch` blocks for handling promise rejections and other exceptions.
*   **JSX/TSX Specifics:** Follow React best practices for component design.

### 3.2. Backend: Python

*   **PEP 8:** Adhere strictly to PEP 8, the style guide for Python code. Use linters like Flake8 and formatters like Black to enforce this.
*   **Type Hinting:** Use Python type hints (Python 3.6+) for all function signatures and important variables to improve code clarity and allow for static analysis.
*   **Virtual Environments:** Always use virtual environments (e.g., `venv`, `conda`, or managed by tools like Poetry/PDM) to isolate project dependencies.
*   **Dependency Management:** Use `requirements.txt` (with `pip freeze`) or preferably a `pyproject.toml` file with a tool like Poetry or PDM for managing dependencies.
*   **Error Handling:** Use `try...except` blocks for robust error handling. Define custom exceptions for application-specific errors where appropriate.
*   **Logging:** Utilize the standard `logging` module for application logging. Configure appropriate log levels and handlers.

## 4. Naming Conventions

### 4.1. General (Cross-Cutting)

*   **Markdown Files:**
    *   Be Descriptive: The filename should clearly indicate the content.
    *   Use Kebab-Case: Separate words with hyphens (e.g., `user-authentication.md`).
    *   Keep it Short (but Clear): Aim for brevity while maintaining clarity.
    *   Lowercase: Use all lowercase letters.
    *   Use `.md` Extension: Always use the `.md` extension.
    *   Avoid Special Characters: Stick to letters, numbers, and hyphens.
    *   Numbers with Padding: If you have a series of documents, pad numbers with leading zeros (e.g., `01-introduction.md`).
*   **Routes/APIs (Endpoints):**
    *   Use kebab-case for route segments (e.g., `/users`, `/products/details`).
    *   Follow RESTful principles for API design (e.g., `/users` for getting all users, `/users/{id}` for a specific user).
    *   Use clear and consistent naming for API endpoints.

### 4.2. Frontend (TypeScript/JavaScript)

*   **Variables & Constants:**
    * Use descriptive and meaningful names.
    * Use camelCase (e.g., `userName`, `productPrice`).
    * Avoid single-letter variables except for loop counters (e.g., `i`, `j`).
    * Use consistent abbreviations (e.g., `btn` for button, `msg` for message).
    * Use nouns for variables that hold data (e.g., `users`, `products`).
    * Use booleans with prefixes like `is`, `has`, `should` (e.g., `isLoggedIn`, `hasPermission`, `shouldUpdate`).
    * Use `UPPER_SNAKE_CASE` for constants (e.g., `MAX_USERS = 100`).
* **Functions:**
    * Use verbs or verb phrases for function names (e.g., `getUser`, `calculateTotal`, `sendEmail`).
    * Use camelCase (e.g., `fetchUserData`, `formatDate`).
    * Be clear about what the function does and what it returns.
    * For event handlers in UI, use `handle` prefix (e.g., `handleClick`, `handleChange`).
* **Classes & React Components:**
    * Use PascalCase (e.g., `UserForm`, `ProductList`).
    * Name files according to the class/component they contain (e.g., `UserForm.tsx`).
* **Objects:**
    * Use descriptive names that reflect the data they hold (e.g., `userData`, `productDetails`).
    * Maintain consistency in the keys used within objects.
* **Parameters:**
    * Use descriptive names that indicate the purpose of the parameter.
    * Be consistent with parameter order across functions.
    * Consider using destructuring for complex objects to improve readability.

### 4.3. Backend (Python)

*   **Variables & Functions:**
    *   Use `snake_case` (e.g., `user_name`, `product_price`, `calculate_total`).
    *   Use descriptive and meaningful names.
    *   Avoid single-letter variables except for loop counters or well-known contexts (e.g., `e` in `try...except e`).
*   **Classes:**
    *   Use `PascalCase` (e.g., `UserService`, `ProductRepository`).
*   **Constants:**
    *   Use `UPPER_SNAKE_CASE` (e.g., `MAX_CONNECTIONS = 10`).
*   **Modules:**
    *   Use short, `snake_case`, all-lowercase names. Avoid using special characters like hyphens.
*   **Packages:**
    *   Use short, all-lowercase names. Underscores are discouraged but can be used if it improves readability.
*   **Parameters:**
    *   Use `snake_case`.
    *   Be descriptive.

## 5. Data Handling and API Design

### 5.1. Data Structures and Formats

*   **General:** Use appropriate data structures for the task (lists/arrays, dictionaries/objects, maps, sets).
*   **Frontend (TypeScript):** Define interfaces or types for data objects.
*   **Backend (Python):** Use Pydantic models or dataclasses for structured data, especially for API request/response bodies.
*   **API Data Exchange:** Use JSON as the primary format for request and response payloads between frontend and backend.
*   **Data Formats:** Specify and consistently use data formats (e.g., ISO 8601 for dates, currency formats).
*   **Documentation:** Document the shape of data returned from APIs (see API Documentation section).

### 5.2. API Design (Primarily for Python Backend)

*   **RESTful Principles:** Follow RESTful principles where applicable.
*   **Request Methods:** Use consistent HTTP request methods (GET, POST, PUT, DELETE, PATCH).
*   **Endpoints:** Define clear, consistent, and resource-oriented endpoints (as per Naming Conventions).
*   **Status Codes:** Return appropriate HTTP status codes (e.g., 200, 201, 400, 401, 403, 404, 500).
*   **Error Responses:** Provide meaningful error messages in JSON format for client-side handling.
*   **Request/Response Formats:** Document request and response schemas (e.g., using OpenAPI/Swagger).
*   **Pagination:** Implement pagination for API endpoints that return large datasets.
*   **Versioning:** Consider API versioning (e.g., `/api/v1/...`) if significant breaking changes are anticipated.

### 5.3. Function Design and Best Practices (General)

* **Single Responsibility Principle:** Each function should do one thing and do it well.
* **Function Length:** Keep functions relatively short and focused. If a function gets too long, break it down into smaller functions.
* **Parameters:**
    * Limit the number of function parameters. If a function needs many parameters, consider passing an object instead.
    * Use default parameters where appropriate.
* **Return Values:**
    * Be explicit about what a function returns.
    * Return consistent data types.
    * Handle potential errors and return appropriate error values or throw exceptions.
* **Side Effects:**
    * Minimize side effects (modifying variables outside the function's scope).
    * Clearly document any side effects that a function might have.
* **Comments:**
    * Write clear and concise comments to explain complex logic or non-obvious code.
    * Document function purpose, parameters, and return values, especially for public functions.

### 5.4. Data Persistence (Backend)

*   **General:**
    *   Choose appropriate data storage solutions based on project needs (e.g., SQL, NoSQL, file system).
    *   Abstract data access logic into repositories or data access layers (DALs).
*   **If using an ORM (e.g., SQLAlchemy, Django ORM):**
    *   Follow ORM best practices for defining models, queries, and managing sessions/connections.
    *   Be mindful of query performance (N+1 problem, efficient querying).
*   **If using a NoSQL database (e.g., MongoDB, DynamoDB):**
    *   Design document structures or schemas optimized for access patterns.
    *   Use appropriate indexing.
    *   Follow naming conventions specific to the database if they differ from general Python conventions (though aim for consistency).
*   **Migrations:** Use a migration tool (e.g., Alembic for SQLAlchemy, Django migrations) for managing database schema changes.

## 4. UI Component Guidelines

*   See `/Users/bam/Code_NOiCloud/projects/kys-rag/docs/ui-component-guidelines.md` for detailed UI component guidelines for the Next.js frontend. This document covers component structure, props, state, styling, accessibility, testing, and documentation for UI components.

## 6. Version Control

* Use Git for version control.
* Follow a clear branching strategy (e.g., Gitflow).
* Write descriptive commit messages.
* Use pull requests for code reviews.

## 7. Testing Guidelines

*   **General Principles:**
    *   Write unit, integration, and (where appropriate) end-to-end tests.
    *   Aim for high test coverage of critical business logic.
    *   Tests should be readable, maintainable, and fast.
    *   Follow a consistent naming convention for test files and test cases (e.g., `test_*.py` or `*.test.ts`).
*   **Frontend (Next.js/TypeScript):**
    *   Use Jest and React Testing Library for testing UI components and utility functions.
    *   Focus on testing component behavior from a user's perspective.
    *   Mock API calls and external dependencies.
*   **Backend (Python):**
    *   Use `pytest` (recommended) or `unittest` for writing tests.
    *   Utilize mocking libraries (e.g., `unittest.mock` or `pytest-mock`) to isolate units of code.
    *   Test API endpoints, service logic, and utility functions.
    *   For database interactions, consider using in-memory databases for tests or a dedicated test database.

## 8. Documentation

*   **General:**
    *   Write clear, concise, and up-to-date documentation.
    *   Document non-obvious code, complex algorithms, and architectural decisions.
*   **Code Comments:**
    *   Use inline comments for clarifying complex or tricky parts of the code.
*   **Frontend (TypeScript/JSDoc):**
    *   Use JSDoc comments for functions, components, props, and complex types.
*   **Backend (Python Docstrings):**
    *   Write comprehensive docstrings for all public modules, classes, functions, and methods.
    *   Follow a consistent docstring format (e.g., Google, NumPy, or reStructuredText recognized by Sphinx).
    *   Example (Google style):
        ```python
        def my_function(param1: int, param2: str) -> bool:
            """Does something interesting.

            Args:
                param1: The first parameter.
                param2: The second parameter.

            Returns:
                True if successful, False otherwise.
            """
            # ... implementation ...
        ```
*   **API Documentation (Backend):**
    *   Generate or write API documentation. Tools like FastAPI can auto-generate OpenAPI (Swagger) docs.
    *   Alternatively, maintain Postman collections or use other API documentation tools.
*   **Project-Level Documentation:** Maintain `README.md` files for setup, architecture overview, and deployment instructions.

## 9. Code Review Process

* Be respectful and constructive during code reviews.
* Provide clear and actionable feedback.
* Be open to receiving feedback on your own code.

## 10. Tools and Technologies

### 10.1. Frontend (Next.js/TypeScript)
*   **Linting:** ESLint (with appropriate plugins for React, TypeScript, Next.js).
*   **Formatting:** Prettier.
*   **IDE:** VS Code with recommended extensions (e.g., ESLint, Prettier, EditorConfig).

### 10.2. Backend (Python)
*   **Linting:** `Flake8` (combines PyFlakes, pycodestyle, McCabe). Consider plugins like `flake8-bugbear`, `flake8-comprehensions`.
*   **Formatting:** `Black` (opinionated, consistent formatter). `autopep8` is an alternative.
*   **Type Checking:** `Mypy` for static type analysis.
*   **IDE:** VS Code (with Python, Pylance, Ruff extensions) or PyCharm.

### 10.3. Environment Management
*   **Secrets:** Use `.env` files (added to `.gitignore`) for local development secrets and environment variables. Use `python-dotenv` (Python) or Next.js built-in env var support.
*   **Configuration:** Store environment-specific configurations appropriately.

## 11. Security Best Practices

*   **Input Validation:** Validate and sanitize all user inputs on both frontend and backend.
*   **Output Encoding:** Encode output appropriately to prevent XSS attacks (React does much of this automatically, but be mindful).
*   **Authentication & Authorization:** Implement robust authentication and authorization mechanisms for backend APIs.
*   **Secrets Management:** Never commit secrets directly to version control. Use environment variables or a secrets management system.
*   **Dependency Vulnerabilities:** Regularly scan dependencies for known vulnerabilities (e.g., `npm audit`, `pip-audit` or Snyk/Dependabot).
*   **HTTPS:** Ensure HTTPS is used in production.
*   **Rate Limiting:** Implement rate limiting on APIs to prevent abuse.

By adhering to these coding guidelines, we can create a high-quality, secure, and maintainable KYS-RAG codebase that is easy to understand, extend, and showcase.