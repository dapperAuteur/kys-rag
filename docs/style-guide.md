# Style Guide for Temba Financial Dashboard

1. Colors
Use the following color scheme defined in globals.css:

Variable	Light Mode	Dark Mode	Usage
--background	#ffffff	#0a0a0a	Background color for the entire app.
--foreground	#171717	#ededed	Text and primary UI elements.
--form-text   #000000  #ffffff  Form inputs and labels.

Example Usage
```css
input, select, textarea {
  color: var(--form-text);
}

2. Typography
Use the Geist font family for a modern and clean look. It’s already configured in layout.tsx.

Font Family	Usage
Geist	Primary font for all text.
Geist Mono	Monospace font for code or numbers.
Example Usage
const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

Copy

Apply

3. Spacing
Use a consistent spacing scale for margins and padding. Use multiples of 0.25rem (4px) for consistency.

Size	Value	Usage
xs	0.25rem	Small spacing (e.g., between icons).
sm	0.5rem	Medium spacing (e.g., between buttons).
md	1rem	Large spacing (e.g., section padding).
lg	2rem	Extra-large spacing (e.g., page margins).
Example Usage
.container {
  padding: 1rem; /* md */
  margin-bottom: 2rem; /* lg */
}

Copy

Apply

4. Shadows
Use subtle shadows to create depth and hierarchy.

Shadow	Value	Usage
default	0 1px 3px rgba(0, 0, 0, 0.1)	Cards, buttons, and dropdowns.
hover	0 4px 6px rgba(0, 0, 0, 0.1)	Hover states for interactive elements.
Example Usage
.card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.button:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

Copy

Apply

5. Borders
Use consistent border styles for separation and focus.

Border	Value	Usage
default	1px solid rgba(0, 0, 0, 0.1)	Dividers, input fields, and cards.
focus	2px solid #3b82f6	Focus states for inputs and buttons.
Example Usage
.input {
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.input:focus {
  border: 2px solid #3b82f6;
}

Copy

Apply

6. Buttons
Use consistent button styles for primary and secondary actions.

Button Type	Styles	Usage
Primary	Background: #3b82f6, Text: #ffffff	Main actions (e.g., "Submit").
Secondary	Background: #e2e8f0, Text: #171717	Secondary actions (e.g., "Cancel").
Example Usage
.button-primary {
  background: #3b82f6;
  color: #ffffff;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}

.button-secondary {
  background: #e2e8f0;
  color: #171717;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}

Copy

Apply

7. Layout
Use a consistent layout structure for pages and components.

Component	Styles	Usage
Container	Max-width: 1200px, Margin: 0 auto	Center content on the page.
Grid	Display: grid, Gap: 1rem	Layout for cards, lists, or forms.
Example Usage
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

Copy

Apply

8. Icons
Use a consistent icon size and color for visual harmony.

Icon Size	Value	Usage
Small	16px	Inline icons (e.g., buttons).
Medium	24px	Standalone icons (e.g., navigation).
Large	32px	Hero icons (e.g., empty states).
Example Usage
.icon-small {
  width: 16px;
  height: 16px;
}

.icon-medium {
  width: 24px;
  height: 24px;
}

Copy

Apply

9. Breakpoints
Use consistent breakpoints for responsive design.

Breakpoint	Value	Usage
sm	640px	Small screens (e.g., mobile).
md	768px	Medium screens (e.g., tablets).
lg	1024px	Large screens (e.g., desktops).
Example Usage
@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}

Copy

Apply

10. Accessibility
Ensure all components are accessible by following these guidelines:

Use semantic HTML (e.g., <button> for buttons).
Add aria-label for icons and non-text elements.
Ensure sufficient color contrast (e.g., text vs. background).
This style guide ensures a clean, consistent, and maintainable UI for the temba-fin-dashboard project. Let me know when you’re ready for more advanced improvements! 🚀