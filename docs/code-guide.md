# Coding Guidelines

This document outlines the coding guidelines for this project. Following these guidelines will promote consistency, readability, and maintainability, making it easier for everyone to understand and contribute to the codebase.

## 1. General Principles

* **KISS (Keep It Simple, Stupid):** Aim for simplicity in your code. Avoid unnecessary complexity.
* **DRY (Don't Repeat Yourself):** Avoid duplicating code. Extract common logic into reusable functions or components.
* **YAGNI (You Ain't Gonna Need It):** Don't implement features or code that you think you might need in the future. Focus on the current requirements.
* **Code Readability:** Write code that is easy to understand. Use clear naming, comments, and formatting.

## 2. Language-Specific Guidelines

###   2.1. TypeScript

* **Strict Typing:** Utilize TypeScript's strong typing features to improve code safety and maintainability. Define types for variables, function parameters, and return values.
* **Interfaces and Types:** Use interfaces and types to define data structures and object shapes.
* **Enums:** Use enums for a set of related constants.
* **Async/Await:** Use `async/await` for asynchronous operations to improve code readability.
* **Error Handling:** Use `try...catch` blocks to handle exceptions.

## 3. Data Handling and Functions

###   3.1. Naming Conventions

* **Variables:**
    * Use descriptive and meaningful names.
    * Use camelCase (e.g., `userName`, `productPrice`).
    * Avoid single-letter variables except for loop counters (e.g., `i`, `j`).
    * Use consistent abbreviations (e.g., `btn` for button, `msg` for message).
    * Use nouns for variables that hold data (e.g., `users`, `products`).
    * Use booleans with prefixes like `is`, `has`, `should` (e.g., `isLoggedIn`, `hasPermission`, `shouldUpdate`).
    * Use constants for values that don't change, in all caps (e.g., `MAX_USERS = 100`).
* **Functions:**
    * Use verbs or verb phrases for function names (e.g., `getUser`, `calculateTotal`, `sendEmail`).
    * Use camelCase (e.g., `fetchUserData`, `formatDate`).
    * Be clear about what the function does and what it returns.
    * For event handlers in UI, use `handle` prefix (e.g., `handleClick`, `handleChange`).
* **Classes/Components:**
    * Use PascalCase (e.g., `UserForm`, `ProductList`).
    * Name files according to the class/component they contain (e.g., `UserForm.tsx`).
* **Routes/APIs:**
    * Use kebab-case for route segments (e.g., `/users`, `/products/details`).
    * Follow RESTful principles for API design (e.g., `/users` for getting all users, `/users/{id}` for a specific user).
    * Use clear and consistent naming for API endpoints.
* **Objects:**
    * Use descriptive names that reflect the data they hold (e.g., `userData`, `productDetails`).
    * Maintain consistency in the keys used within objects.
* **Data:**
    * Define data structures clearly (e.g., interfaces or types in TypeScript).
    * Document the format of data being passed between functions or components.
* **Parameters:**
    * Use descriptive names that indicate the purpose of the parameter.
    * Be consistent with parameter order across functions.
    * Consider using destructuring for complex objects to improve readability.
* **Markdown Files:**
    * Be Descriptive: The filename should clearly indicate the content.
    * Use Kebab-Case: Separate words with hyphens (e.g., `user-authentication.md`).
    * Keep it Short (but Clear): Aim for brevity while maintaining clarity.
    * Lowercase: Use all lowercase letters.
    * Use `.md` Extension: Always use the `.md` extension.
    * Avoid Special Characters: Stick to letters, numbers, and hyphens.
    * Numbers with Padding: If you have a series of documents, pad numbers with leading zeros (e.g., `01-introduction.md`).

###   3.2. Data Structures and Formats

* Use appropriate data structures (arrays, objects, maps, sets) for the task.
* Define interfaces or types for data objects, especially in TypeScript.
* Specify data formats (e.g., date formats, currency formats).
* Document the shape of data returned from APIs.

###   3.3. API Design

* Follow RESTful principles where applicable.
* Use consistent request methods (GET, POST, PUT, DELETE).
* Define clear and consistent endpoints.
* Handle errors gracefully and return appropriate status codes.
* Document request and response formats.
* Consider pagination for large datasets.

###   3.4. Function Design and Best Practices

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
* **Error Handling:**
    * Use `try...catch` blocks to handle exceptions.
    * Log errors appropriately.
    * Return meaningful error messages to the caller.
* **Asynchronous Functions:**
    * Use `async/await` for asynchronous operations in JavaScript/TypeScript.
    * Handle promise rejections properly.
    * Consider using utility functions for common asynchronous patterns.
* **Comments:**
    * Write clear and concise comments to explain complex logic or non-obvious code.
    * Document function purpose, parameters, and return values, especially for public functions.

You're absolutely right to point that out! We discussed naming conventions for variables, functions, files, etc., but we didn't explicitly cover naming and describing documents in MongoDB. That's an important aspect of data management, so let's address it.

Here's an addition to the "Data Handling and Functions" section of your coding guidelines, focusing on MongoDB:

###   3.5. MongoDB Guidelines

* **Collection Naming:**

    * Use plural nouns for collection names (e.g., `users`, `products`, `orders`). This aligns with RESTful conventions and reflects that a collection holds multiple documents.
    * Use lowercase letters for collection names.
    * Avoid using underscores or hyphens in collection names unless absolutely necessary. Stick to alphanumeric characters.
    * Be concise but descriptive. The collection name should clearly indicate the type of data it stores.

* **Document Structure:**

    * Design documents to represent a single entity or concept.
    * Embed related data within documents when it makes sense for retrieval and performance. Avoid excessive joins.
    * Normalize data when necessary to reduce redundancy and ensure data consistency.
    * Use consistent field names across collections where applicable (e.g., `_id` for primary key, `createdAt` and `updatedAt` for timestamps).
    * Choose appropriate data types for fields (e.g., String, Number, Boolean, Date, Array, Object).
    * Document the schema or structure of your documents, especially for complex data. This can be done with comments, schema validation within MongoDB, or external documentation.

* **Field Naming:**

    * Use camelCase for field names (e.g., `firstName`, `productName`, `orderDate`).
    * Be descriptive and meaningful with field names.
    * Avoid single-letter field names except for very common abbreviations (e.g., `id`).
    * Use consistent abbreviations (e.g., `addr` for address, `desc` for description).
    * Use boolean fields with prefixes like `is`, `has`, `should` (e.g., `isActive`, `hasPermission`).
    * For fields that store IDs of other documents, use the related collection name with "Id" suffix (e.g., `userId` to store the ID of a user document).

* **Example Document (TypeScript Interface):**

    ```typescript
    interface User {
        _id: ObjectId;
        firstName: string;
        lastName: string;
        email: string;
        createdAt: Date;
        updatedAt: Date;
        role: 'admin' | 'user' | 'guest';
        address?: { // Optional field
            street: string;
            city: string;
            zipCode: string;
        };
        orderIds: ObjectId[]; // Array of order IDs
    }
    ```

These guidelines will help you maintain a consistent and organized approach to working with MongoDB, making your database schema easier to understand and manage.

## 4. UI Component Guidelines

* See `UI_COMPONENT_GUIDELINES.md` for detailed UI component guidelines.

## 5. File and Directory Structure

* Organize files and directories logically.
* Group related files together.
* Use consistent naming conventions.
* Follow the Next.js App Router conventions.

## 6. Version Control

* Use Git for version control.
* Follow a clear branching strategy (e.g., Gitflow).
* Write descriptive commit messages.
* Use pull requests for code reviews.

## 7. Testing

* Write unit tests to ensure code quality.
* Use Jest and React Testing Library for testing UI components.
* Aim for reasonable test coverage.
* Follow a consistent naming convention for test files and test cases.

## 8. Documentation

* Write clear and concise documentation.
* Document code using inline comments and JSDoc.
* Keep documentation up-to-date.

## 9. Code Review Process

* Be respectful and constructive during code reviews.
* Provide clear and actionable feedback.
* Be open to receiving feedback on your own code.

## 10. Tools and Technologies

* Use ESLint and Prettier for linting and formatting.
* Use VS Code with recommended extensions for development.
* Document any other relevant tools and technologies used in the project.

By adhering to these coding guidelines, we can create a high-quality codebase that is easy to understand, maintain, and extend.