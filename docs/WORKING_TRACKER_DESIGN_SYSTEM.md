# 🎨 WORKING TRACKER — COMPLETE DESIGN SYSTEM

## 🧠 Brand DNA
**Personality:** Professional · Intelligent · Calm & Confident · High-Trust Enterprise · "Quietly Powerful"

**Visual Philosophy:** Modern, not flashy · Minimal but not cold · Ultra-clean with subtle depth

---

## 🎨 COLOR SYSTEM

### Primary Palette
```css
/* Core Brand Colors */
--wt-charcoal: #1F2933;        /* Text, headers, dark elements */
--wt-cloud-white: #F7F8FA;     /* App background */
--wt-mist-gray: #E6E8EB;       /* Secondary backgrounds */

/* Accent Colors */
--wt-electric-blue: #2563EB;   /* Primary actions, CTAs */
--wt-soft-indigo: #4F46E5;     /* Secondary accent */
--wt-teal-glow: #14B8A6;       /* Success, highlights */

/* Background System */
--wt-bg-app: #F7F8FA;          /* Main app background */
--wt-bg-card: #FFFFFF;         /* Cards, panels, modals */
--wt-border: #E5E7EB;          /* All borders */
--wt-hover: #F0F3F7;           /* Hover states */

/* Text Colors */
--wt-text-primary: #1F2933;    /* Main text */
--wt-text-secondary: #616E7C;  /* Supporting text */
--wt-text-tertiary: #9AA5B1;   /* Muted text */

/* Semantic Colors */
--wt-success: #10B981;         /* Success states */
--wt-warning: #F59E0B;         /* Warnings */
--wt-error: #EF4444;           /* Errors */
--wt-info: #3B82F6;            /* Info messages */
```

### Gradients (Subtle, Never Loud)
```css
/* Primary Gradient */
--wt-gradient-primary: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%);

/* Hover Gradient */
--wt-gradient-hover: linear-gradient(135deg, #1D4ED8 0%, #4338CA 100%);

/* Subtle Background Gradient */
--wt-gradient-bg: linear-gradient(180deg, #F7F8FA 0%, #FFFFFF 100%);

/* Card Gradient (very subtle) */
--wt-gradient-card: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
```

---

## 🧱 DESIGN TOKENS

### Spacing Scale
```css
--wt-space-xs: 4px;
--wt-space-sm: 8px;
--wt-space-md: 16px;
--wt-space-lg: 24px;
--wt-space-xl: 32px;
--wt-space-2xl: 48px;
--wt-space-3xl: 64px;
```

### Border Radius
```css
--wt-radius-sm: 8px;           /* Small elements */
--wt-radius-md: 12px;          /* Buttons, inputs */
--wt-radius-lg: 16px;          /* Cards */
--wt-radius-xl: 20px;          /* Large cards */
--wt-radius-2xl: 24px;         /* Modals, dialogs */
--wt-radius-full: 9999px;      /* Pills, avatars */
```

### Shadows (Soft & Layered)
```css
/* Elevation System */
--wt-shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
--wt-shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.04);
--wt-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.04);
--wt-shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.06);
--wt-shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.08);

/* Hover Shadows */
--wt-shadow-hover: 0 12px 28px rgba(37, 99, 235, 0.12);

/* Focus Glow */
--wt-shadow-focus: 0 0 0 4px rgba(37, 99, 235, 0.1);
```

### Typography
```css
/* Font Families */
--wt-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--wt-font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font Sizes */
--wt-text-xs: 12px;
--wt-text-sm: 14px;
--wt-text-base: 16px;
--wt-text-lg: 18px;
--wt-text-xl: 20px;
--wt-text-2xl: 24px;
--wt-text-3xl: 30px;
--wt-text-4xl: 36px;

/* Font Weights */
--wt-weight-normal: 400;
--wt-weight-medium: 500;
--wt-weight-semibold: 600;
--wt-weight-bold: 700;

/* Line Heights */
--wt-leading-tight: 1.25;
--wt-leading-normal: 1.5;
--wt-leading-relaxed: 1.75;
```

### Motion System
```css
/* Timing Functions */
--wt-ease-in: cubic-bezier(0.4, 0, 1, 1);
--wt-ease-out: cubic-bezier(0, 0, 0.2, 1);
--wt-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--wt-ease-smooth: cubic-bezier(0.25, 0.1, 0.25, 1);

/* Durations */
--wt-duration-fast: 150ms;
--wt-duration-base: 200ms;
--wt-duration-slow: 300ms;
--wt-duration-slower: 500ms;
```

---

## 🧩 COMPONENT LIBRARY

### Buttons
```css
/* Primary Button */
.wt-btn-primary {
  height: 44px;
  padding: 0 24px;
  background: var(--wt-gradient-primary);
  color: white;
  border: none;
  border-radius: var(--wt-radius-md);
  font-size: var(--wt-text-base);
  font-weight: var(--wt-weight-medium);
  box-shadow: var(--wt-shadow-sm);
  transition: all var(--wt-duration-base) var(--wt-ease-out);
  cursor: pointer;
}

.wt-btn-primary:hover {
  background: var(--wt-gradient-hover);
  box-shadow: var(--wt-shadow-hover);
  transform: translateY(-1px);
}

.wt-btn-primary:active {
  transform: translateY(0);
}

/* Secondary Button */
.wt-btn-secondary {
  height: 44px;
  padding: 0 24px;
  background: transparent;
  color: var(--wt-electric-blue);
  border: 1.5px solid var(--wt-border);
  border-radius: var(--wt-radius-md);
  font-size: var(--wt-text-base);
  font-weight: var(--wt-weight-medium);
  transition: all var(--wt-duration-base) var(--wt-ease-out);
  cursor: pointer;
}

.wt-btn-secondary:hover {
  background: var(--wt-hover);
  border-color: var(--wt-electric-blue);
}

/* Ghost Button */
.wt-btn-ghost {
  height: 44px;
  padding: 0 24px;
  background: transparent;
  color: var(--wt-text-secondary);
  border: none;
  border-radius: var(--wt-radius-md);
  transition: all var(--wt-duration-base) var(--wt-ease-out);
  cursor: pointer;
}

.wt-btn-ghost:hover {
  background: var(--wt-hover);
  color: var(--wt-text-primary);
}
```

### Cards
```css
.wt-card {
  background: var(--wt-bg-card);
  border: 1px solid var(--wt-border);
  border-radius: var(--wt-radius-lg);
  padding: var(--wt-space-lg);
  box-shadow: var(--wt-shadow-md);
  transition: all var(--wt-duration-base) var(--wt-ease-out);
}

.wt-card:hover {
  box-shadow: var(--wt-shadow-lg);
  transform: translateY(-2px);
}

.wt-card-header {
  margin-bottom: var(--wt-space-lg);
  padding-bottom: var(--wt-space-md);
  border-bottom: 1px solid var(--wt-border);
}

.wt-card-title {
  font-size: var(--wt-text-xl);
  font-weight: var(--wt-weight-semibold);
  color: var(--wt-text-primary);
  margin: 0;
}
```

### Inputs & Forms
```css
.wt-input {
  height: 44px;
  padding: 0 16px;
  background: var(--wt-bg-card);
  border: 1.5px solid var(--wt-border);
  border-radius: var(--wt-radius-md);
  font-size: var(--wt-text-base);
  color: var(--wt-text-primary);
  transition: all var(--wt-duration-base) var(--wt-ease-out);
}

.wt-input:focus {
  outline: none;
  border-color: var(--wt-electric-blue);
  box-shadow: var(--wt-shadow-focus);
}

.wt-input::placeholder {
  color: var(--wt-text-tertiary);
}

.wt-label {
  display: block;
  margin-bottom: var(--wt-space-sm);
  font-size: var(--wt-text-sm);
  font-weight: var(--wt-weight-medium);
  color: var(--wt-text-secondary);
}
```

### Navigation
```css
.wt-nav {
  background: var(--wt-bg-card);
  border-right: 1px solid var(--wt-border);
  padding: var(--wt-space-lg);
}

.wt-nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: var(--wt-space-sm);
  color: var(--wt-text-secondary);
  border-radius: var(--wt-radius-md);
  transition: all var(--wt-duration-fast) var(--wt-ease-out);
  cursor: pointer;
}

.wt-nav-item:hover {
  background: var(--wt-hover);
  color: var(--wt-text-primary);
}

.wt-nav-item.active {
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.1) 0%, transparent 100%);
  color: var(--wt-electric-blue);
  font-weight: var(--wt-weight-medium);
  border-left: 3px solid var(--wt-electric-blue);
}

.wt-nav-icon {
  margin-right: var(--wt-space-md);
  font-size: 20px;
}
```

### Modals & Dialogs
```css
.wt-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(31, 41, 51, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.wt-modal {
  background: var(--wt-bg-card);
  border-radius: var(--wt-radius-2xl);
  padding: var(--wt-space-2xl);
  max-width: 600px;
  width: 90%;
  box-shadow: var(--wt-shadow-xl);
  animation: modalSlideIn var(--wt-duration-slow) var(--wt-ease-smooth);
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
```

### Badges & Tags
```css
.wt-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--wt-radius-full);
  font-size: var(--wt-text-xs);
  font-weight: var(--wt-weight-medium);
}

.wt-badge-primary {
  background: rgba(37, 99, 235, 0.1);
  color: var(--wt-electric-blue);
}

.wt-badge-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--wt-success);
}

.wt-badge-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--wt-warning);
}
```

---

## 🧭 LAYOUT SYSTEM

### App Container
```css
.wt-app {
  display: flex;
  min-height: 100vh;
  background: var(--wt-bg-app);
  font-family: var(--wt-font-sans);
  color: var(--wt-text-primary);
}

.wt-sidebar {
  width: 260px;
  background: var(--wt-bg-card);
  border-right: 1px solid var(--wt-border);
}

.wt-main {
  flex: 1;
  padding: var(--wt-space-2xl);
  overflow-y: auto;
}
```

### Grid System
```css
.wt-grid {
  display: grid;
  gap: var(--wt-space-lg);
}

.wt-grid-2 { grid-template-columns: repeat(2, 1fr); }
.wt-grid-3 { grid-template-columns: repeat(3, 1fr); }
.wt-grid-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .wt-grid-2,
  .wt-grid-3,
  .wt-grid-4 {
    grid-template-columns: 1fr;
  }
}
```

---

## 🎬 ANIMATIONS & TRANSITIONS

### Page Transitions
```css
.wt-page-enter {
  opacity: 0;
  transform: translateY(10px);
}

.wt-page-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: all var(--wt-duration-slow) var(--wt-ease-smooth);
}

.wt-page-exit {
  opacity: 1;
}

.wt-page-exit-active {
  opacity: 0;
  transition: opacity var(--wt-duration-base) var(--wt-ease-out);
}
```

### Micro-interactions
```css
.wt-hover-lift {
  transition: transform var(--wt-duration-base) var(--wt-ease-out);
}

.wt-hover-lift:hover {
  transform: translateY(-2px);
}

.wt-hover-scale {
  transition: transform var(--wt-duration-base) var(--wt-ease-out);
}

.wt-hover-scale:hover {
  transform: scale(1.02);
}
```

---

## 📱 RESPONSIVE BREAKPOINTS

```css
/* Mobile First */
--wt-breakpoint-sm: 640px;   /* Small tablets */
--wt-breakpoint-md: 768px;   /* Tablets */
--wt-breakpoint-lg: 1024px;  /* Small desktops */
--wt-breakpoint-xl: 1280px;  /* Large desktops */
--wt-breakpoint-2xl: 1536px; /* Extra large screens */
```

---

## 🎯 USAGE GUIDELINES

### Do's ✅
- Use soft shadows, never harsh
- Maintain generous whitespace
- Keep transitions smooth (180-250ms)
- Use the gradient sparingly (CTAs only)
- Hover states should lift slightly
- Focus states should glow subtly

### Don'ts ❌
- No pure black (#000000)
- No pure white (#FFFFFF) for backgrounds
- No sharp corners (minimum 8px radius)
- No jarring animations
- No loud gradients
- No heavy shadows

---

## 🎨 ACCESSIBILITY

```css
/* Focus Visible */
*:focus-visible {
  outline: 2px solid var(--wt-electric-blue);
  outline-offset: 2px;
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 🌙 DARK MODE (Optional)

```css
[data-theme="dark"] {
  --wt-charcoal: #E6E8EB;
  --wt-cloud-white: #1A1D23;
  --wt-mist-gray: #252932;
  --wt-bg-app: #1A1D23;
  --wt-bg-card: #252932;
  --wt-border: #373B46;
  --wt-hover: #2D313C;
  --wt-text-primary: #E6E8EB;
  --wt-text-secondary: #9AA5B1;
}
```

---

## 🎊 BRAND KEYWORDS

**Minimal · Premium · Calm · Modern · Intelligent · Trustworthy · Enterprise · AI-grade · Clean · Soft-tech**

---

**This design system ensures consistent, premium branding across:**
- Web Application
- Desktop Application
- Mobile Application
- Marketing Website
- Documentation
- All UI Components

**Apply these styles universally for a cohesive, professional experience.**
