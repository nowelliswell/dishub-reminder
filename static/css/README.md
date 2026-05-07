# 🎨 Dishub Reminder - Design System Documentation

## 📁 File Structure

```
static/css/
├── design-system.css   # CSS variables, base styles, typography
├── components.css      # Reusable UI components (buttons, cards, forms)
└── utilities.css       # Helper classes (spacing, colors, display)
```

---

## 🚀 Quick Start

### Include in HTML
```html
<link rel="stylesheet" href="/static/css/design-system.css">
<link rel="stylesheet" href="/static/css/components.css">
<link rel="stylesheet" href="/static/css/utilities.css">
```

---

## 🎨 Color Palette

### Primary Colors (Dishub Blue)
```css
var(--primary)        /* #0B41D4 - Main brand color */
var(--primary-dark)   /* #082f9e - Hover states */
var(--primary-light)  /* #e8eeff - Backgrounds */
var(--primary-hover)  /* #0a3bc0 - Button hover */
```

### Semantic Colors
```css
var(--success)        /* #10b981 - Green */
var(--warning)        /* #f59e0b - Orange */
var(--danger)         /* #ef4444 - Red */
var(--info)           /* #06b6d4 - Cyan */
```

### Neutral Colors
```css
var(--white)          /* #ffffff */
var(--gray-50)        /* #f9fafb - Lightest */
var(--gray-100)       /* #f3f4f6 */
var(--gray-200)       /* #e5e7eb */
var(--gray-300)       /* #d1d5db */
var(--gray-500)       /* #6b7280 */
var(--gray-700)       /* #374151 */
var(--gray-900)       /* #111827 - Darkest */
```

---

## 🔘 Buttons

### Basic Usage
```html
<!-- Primary (main actions) -->
<button class="btn btn-primary">Save</button>

<!-- Secondary (cancel, back) -->
<button class="btn btn-secondary">Cancel</button>

<!-- Success (approve, confirm) -->
<button class="btn btn-success">Approve</button>

<!-- Warning (caution actions) -->
<button class="btn btn-warning">Reset</button>

<!-- Danger (delete, remove) -->
<button class="btn btn-danger">Delete</button>

<!-- Info (information) -->
<button class="btn btn-info">Info</button>
```

### Button Sizes
```html
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Normal</button>
<button class="btn btn-primary btn-lg">Large</button>
```

### Outline Variants
```html
<button class="btn btn-outline-primary">Outline Primary</button>
<button class="btn btn-outline-secondary">Outline Secondary</button>
<button class="btn btn-outline-danger">Outline Danger</button>
```

### With Icons
```html
<button class="btn btn-primary">
  <i class="bi bi-save"></i> Save
</button>

<button class="btn btn-danger">
  <i class="bi bi-trash"></i> Delete
</button>
```

### Disabled State
```html
<button class="btn btn-primary" disabled>Disabled</button>
```

---

## 🃏 Cards

### Basic Card
```html
<div class="card">
  <div class="card-body">
    Card content here
  </div>
</div>
```

### Card with Header & Footer
```html
<div class="card">
  <div class="card-header">
    <h5>Card Title</h5>
  </div>
  <div class="card-body">
    <p>Card content here</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Action</button>
  </div>
</div>
```

---

## 🏷️ Badges

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-danger">Danger</span>
<span class="badge badge-info">Info</span>
<span class="badge badge-secondary">Secondary</span>
```

---

## 📝 Forms

### Form Group
```html
<div class="mb-3">
  <label class="form-label">Email address</label>
  <input type="email" class="form-control" placeholder="name@example.com">
  <div class="form-text">We'll never share your email.</div>
</div>
```

### Validation States
```html
<!-- Invalid -->
<input type="text" class="form-control is-invalid">
<div class="invalid-feedback">
  This field is required
</div>

<!-- Valid -->
<input type="text" class="form-control is-valid">
```

### Select
```html
<select class="form-control">
  <option>Option 1</option>
  <option>Option 2</option>
  <option>Option 3</option>
</select>
```

### Textarea
```html
<textarea class="form-control" rows="3"></textarea>
```

---

## 📊 Tables

```html
<table class="table">
  <thead>
    <tr>
      <th>Name</th>
      <th>Email</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>John Doe</td>
      <td>john@example.com</td>
      <td>
        <button class="btn btn-sm btn-primary">Edit</button>
      </td>
    </tr>
  </tbody>
</table>
```

---

## 🚨 Alerts

```html
<div class="alert alert-success">
  Success message here
</div>

<div class="alert alert-warning">
  Warning message here
</div>

<div class="alert alert-danger">
  Error message here
</div>

<div class="alert alert-info">
  Info message here
</div>
```

---

## ⏳ Spinners

```html
<!-- Normal spinner -->
<div class="spinner"></div>

<!-- Small spinner -->
<div class="spinner spinner-sm"></div>

<!-- Large spinner -->
<div class="spinner spinner-lg"></div>

<!-- In button -->
<button class="btn btn-primary">
  <span class="spinner spinner-sm"></span>
  Loading...
</button>
```

---

## 🛠️ Utility Classes

### Spacing
```html
<!-- Margin -->
<div class="m-0">No margin</div>
<div class="m-3">Medium margin</div>
<div class="mt-3">Margin top</div>
<div class="mb-3">Margin bottom</div>

<!-- Padding -->
<div class="p-0">No padding</div>
<div class="p-3">Medium padding</div>
```

### Display
```html
<div class="d-none">Hidden</div>
<div class="d-block">Block</div>
<div class="d-flex">Flex</div>
<div class="d-inline-flex">Inline flex</div>
```

### Flexbox
```html
<div class="d-flex justify-center items-center gap-3">
  Centered content with gap
</div>

<div class="d-flex justify-between">
  Space between items
</div>

<div class="d-flex flex-column">
  Vertical layout
</div>
```

### Text
```html
<p class="text-center">Centered text</p>
<p class="text-left">Left aligned</p>
<p class="text-right">Right aligned</p>

<p class="text-sm">Small text</p>
<p class="text-lg">Large text</p>

<p class="font-bold">Bold text</p>
<p class="font-semibold">Semibold text</p>

<p class="text-primary">Primary color</p>
<p class="text-success">Success color</p>
<p class="text-danger">Danger color</p>
<p class="text-muted">Muted color</p>
```

### Background
```html
<div class="bg-white">White background</div>
<div class="bg-gray-50">Light gray background</div>
<div class="bg-primary">Primary background</div>
```

### Border & Radius
```html
<div class="border">With border</div>
<div class="border-0">No border</div>

<div class="rounded">Rounded corners</div>
<div class="rounded-lg">Large rounded</div>
<div class="rounded-full">Fully rounded</div>
```

### Shadow
```html
<div class="shadow-sm">Small shadow</div>
<div class="shadow">Medium shadow</div>
<div class="shadow-lg">Large shadow</div>
```

---

## 📱 Responsive Design

### Breakpoints
- **SM:** 640px (mobile)
- **MD:** 768px (tablet)
- **LG:** 1024px (desktop)
- **XL:** 1280px (large desktop)

### Responsive Utilities
```html
<!-- Hide on mobile -->
<div class="sm:d-none">Hidden on mobile</div>

<!-- Show only on mobile -->
<div class="d-block md:d-none">Mobile only</div>

<!-- Flex column on mobile, row on desktop -->
<div class="flex-column md:flex-row">
  Responsive layout
</div>
```

---

## 🎯 Best Practices

### ✅ DO
- Use semantic button colors (primary for main actions, danger for delete)
- Use consistent spacing (multiples of 0.25rem)
- Use design system colors (var(--primary), var(--success))
- Use utility classes for simple styling
- Keep custom CSS minimal

### ❌ DON'T
- Don't use inline styles
- Don't create custom colors outside the palette
- Don't use !important unless absolutely necessary
- Don't mix old and new button styles
- Don't create duplicate components

---

## 🔧 Customization

### Override CSS Variables
```css
:root {
  --primary: #YOUR_COLOR;
  --primary-dark: #YOUR_DARK_COLOR;
  --primary-light: #YOUR_LIGHT_COLOR;
}
```

### Extend Components
```css
/* Add custom button variant */
.btn-custom {
  background: var(--primary);
  color: var(--white);
  /* ... */
}
```

---

## 📚 Examples

### Login Form
```html
<div class="card" style="max-width: 400px;">
  <div class="card-body">
    <h2 class="text-center mb-4">Login</h2>
    
    <div class="mb-3">
      <label class="form-label">Username</label>
      <input type="text" class="form-control" placeholder="Enter username">
    </div>
    
    <div class="mb-3">
      <label class="form-label">Password</label>
      <input type="password" class="form-control" placeholder="Enter password">
    </div>
    
    <button class="btn btn-primary w-full">Login</button>
  </div>
</div>
```

### Data Table
```html
<div class="card">
  <div class="card-header d-flex justify-between items-center">
    <h5 class="mb-0">Users</h5>
    <button class="btn btn-primary btn-sm">Add User</button>
  </div>
  <div class="card-body p-0">
    <table class="table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>John Doe</td>
          <td>john@example.com</td>
          <td><span class="badge badge-success">Active</span></td>
          <td>
            <button class="btn btn-sm btn-primary">Edit</button>
            <button class="btn btn-sm btn-outline-danger">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

### Status Cards
```html
<div class="row g-3">
  <div class="col-md-3">
    <div class="card">
      <div class="card-body">
        <div class="d-flex justify-between items-center">
          <div>
            <p class="text-muted text-sm mb-1">Total Users</p>
            <h3 class="mb-0">1,234</h3>
          </div>
          <i class="bi bi-people text-primary" style="font-size: 2rem;"></i>
        </div>
      </div>
    </div>
  </div>
  <!-- More cards... -->
</div>
```

---

## 🐛 Troubleshooting

### Styles not applying?
1. Check CSS file order (design-system → components → utilities)
2. Clear browser cache
3. Check for typos in class names
4. Verify CSS files are loaded (check Network tab)

### Colors not working?
1. Make sure design-system.css is loaded first
2. Use CSS variables: `var(--primary)` not `#0B41D4`
3. Check browser DevTools for CSS variable support

### Buttons look wrong?
1. Use correct class: `btn btn-primary` not just `btn-primary`
2. Don't mix old button classes with new ones
3. Check for conflicting custom CSS

---

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review REFACTOR_SUMMARY.md
3. Check browser console for errors
4. Contact development team

---

**Version:** 1.0.0  
**Last Updated:** May 6, 2026  
**Maintained by:** Dishub Development Team
