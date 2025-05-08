# UI Component Guidelines

This document outlines the guidelines for developing UI components in this project. We are using Next.js with the App Router, TypeScript, and Tailwind CSS. Adhering to these guidelines will help ensure consistency, maintainability, and a cohesive user experience.

## 1. Component Structure and Organization

### 1.1. Atomic Design

We encourage the use of the Atomic Design methodology to structure our components. This promotes reusability and scalability.

* **Atoms:** Basic building blocks (e.g., buttons, inputs, labels).
* **Molecules:** Simple combinations of atoms (e.g., search bar, form field).
* **Organisms:** Relatively complex UI components composed of molecules and/or atoms (e.g., header, product card).
* **Templates:** Page-level layouts that define the structure of the UI.
* **Pages:** Specific instances of templates with real content.

### 1.2. Single Responsibility Principle (SRP)

* Each component should ideally have a single, well-defined purpose.
* If a component becomes too complex, break it down into smaller, more focused components.

### 1.3. Directory Structure

* Group related components in directories within the `app` directory (following Next.js App Router conventions).
* Organize components by feature or domain.
    * Example: `app/components/users/UserCard.tsx`, `app/components/products/ProductList.tsx`
* If using Atomic Design, you might have directories like:
    * `app/components/atoms/Button.tsx`
    * `app/components/molecules/FormField.tsx`
    * `app/components/organisms/ProductCard.tsx`
* Place any associated styles, tests, or documentation within the same directory as the component.
    * Example: `app/components/button/Button.tsx`, `app/components/button/Button.module.css`, `app/components/button/Button.test.tsx`

### 1.4. Component Composition

* Favor composition over inheritance. Use props to pass data and functionality to child components.
* Keep the component tree relatively shallow to improve performance and maintainability. Avoid deeply nested component structures.
* Utilize Next.js's built-in composition patterns (e.g., children prop, slots) where appropriate.

## 2. Props and State Management

### 2.1. Props

* Use descriptive and clear prop names.
* Define prop types rigorously using TypeScript interfaces or types.
    * Example:

    ```typescript
    interface ButtonProps {
      label: string;
      onClick: () => void;
      color?: 'primary' | 'secondary';
      disabled?: boolean;
    }
    ```

* Use default prop values where appropriate.
    * Example: `const Button: React.FC<ButtonProps> = ({ label, onClick, color = 'primary', disabled = false }) => { ... }`
* Destructure props within the function body for better readability.
    * Example: `const Button: React.FC<ButtonProps> = ({ label, onClick, color, disabled }) => { ... }`
* Document the purpose and expected values of each prop using JSDoc comments.
* Follow a consistent order for props (e.g., data props, event handler props, styling props).

### 2.2. State

* Manage component state effectively using `useState`.
* Lift state up to the nearest common ancestor when state needs to be shared between components.
* For complex state management, consider using libraries like Zustand or Recoil (if necessary). Evaluate if Next.js Context is sufficient before adding a state management library.
* Avoid unnecessary state. Only store data that needs to trigger UI updates.
* When updating state, especially objects and arrays, use immutable techniques to avoid unexpected side effects.
    * Example: `{ ...prevState, newProperty: newValue }` or `[...prevArray, newValue]`

### 2.3. Context

* Use Next.js Context API for passing data that needs to be accessible to many components at different nesting levels (e.g., theme, user authentication).
* Use Context sparingly, as it can make data flow harder to track.

### 2.4. Server Components

* Leverage Next.js Server Components for data fetching, accessing backend resources, and improving performance.
* Clearly differentiate between Server Components and Client Components.
* Pass data fetched in Server Components as props to Client Components when needed.
* Avoid using browser-specific APIs or `useState`, `useEffect` in Server Components.

## 3. Styling Conventions

### 3.1. Tailwind CSS

* We are using Tailwind CSS for styling.
* Utilize Tailwind's utility classes to style components.
* Avoid creating custom CSS unless absolutely necessary.
* If custom styles are required, use CSS Modules for component-level scoping.
    * Example: `Button.module.css`

### 3.2. Class Naming

* When using CSS Modules, use descriptive and specific class names.
* Follow a consistent naming convention (e.g., kebab-case).
    * Example: `button-primary`, `form-input`, `user-card-name`

### 3.3. Responsive Design

* Utilize Tailwind's responsive modifiers (e.g., `sm:`, `md:`, `lg:`, `xl:`) to create responsive layouts.
* Design components to be responsive and adapt to different screen sizes.

### 3.4. Theming

* If theming is required, leverage Tailwind's configuration to customize colors, fonts, etc.
* Define clear theming variables and guidelines.

## 4. Accessibility (a11y)

* **Semantic HTML:** Use semantic HTML elements (e.g., `<button>`, `<nav>`, `<article>`) to provide structure and meaning to your content.
* **ARIA Roles:** Use ARIA roles to provide additional context to assistive technologies when semantic HTML is not sufficient.
* **Keyboard Navigation:** Ensure that all interactive elements are accessible via keyboard.
* **Focus Management:** Manage focus states to provide clear visual cues for keyboard users.
* **Alt Text:** Provide descriptive alt text for images.
* **Labels:** Associate labels with form elements correctly.
* **Color Contrast:** Ensure sufficient color contrast between text and background (WCAG 2.0 AA compliance).
* **Testing:** Test components with assistive technologies to ensure accessibility.

## 5. Testing

* Use Jest and React Testing Library for testing.
* Write unit tests for individual components to ensure they function correctly in isolation.
* Focus on testing component behavior rather than implementation details.
* Aim for reasonable test coverage to ensure code quality.
* Follow a consistent naming convention for test files and test cases.
    * Example: `Button.test.tsx`
* Utilize testing strategies recommended by React Testing Library (e.g., "screen" object, "getByRole").

## 6. Documentation

* Document the props, state, and events of each component using JSDoc comments.
* Provide clear usage examples within the component's documentation or in a separate documentation file.
* Consider using Storybook or a similar tool to create a living style guide and component library (highly recommended).

## 7. Component File Template

```typescript
import React, { useState } from 'react';
import { ... } from 'react'; // Import necessary React hooks/types
import PropTypes from 'prop-types'; // If using PropTypes (less common with TypeScript)
import styles from './ComponentName.module.css'; // If using CSS Modules

interface ComponentNameProps {
  // Define your props here using TypeScript
  prop1: string;
  prop2?: number;
  onClick: () => void;
}

/**
 * Description of the component.
 *
 * @param {string} prop1 - Description of prop1.
 * @param {number} [prop2] - Description of prop2 (optional).
 * @param {() => void} onClick - Description of onClick.
 * @returns {JSX.Element} The component's JSX.
 */
const ComponentName: React.FC<ComponentNameProps> = ({ prop1, prop2, onClick }) => {
  const [localState, setLocalState] = useState<string>('');

  // Component logic here

  return (
    <div className={styles.container}>
      {/* Component JSX here */}
      <button onClick={onClick}>{prop1}</button>
    </div>
  );
};

// If using PropTypes (less common with TypeScript)
ComponentName.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.number,
  onClick: PropTypes.func.isRequired,
};

export default ComponentName;