# Logo Setup Instructions

## Adding Your Company Logo

To add the Enertherm Engineering logo to the Temperature Data Logger dashboard:

1. **Place your logo file** in this `static` directory
2. **Name the file** `logo.png` (or update the path in dashboard.html if using a different name/format)
3. **Recommended specifications:**
   - Format: PNG with transparent background (preferred) or JPG
   - Size: 200x200 pixels minimum
   - File size: Under 500KB for optimal loading

## File Structure
```
data-logger-project/
├── static/
│   ├── logo.png          <-- Place your logo here
│   └── README_LOGO.md    <-- This file
├── templates/
│   └── dashboard.html    <-- Dashboard that displays the logo
└── app_enhanced.py       <-- Flask app serving static files
```

## Fallback Icon
If no logo file is found, the system will display a temperature icon as a fallback.

## Supported Formats
- PNG (recommended)
- JPG/JPEG
- SVG
- WebP

## Updating Logo Path
If you need to use a different filename or format, update line 508 in `templates/dashboard.html`:
```html
<img src="/static/your-logo-name.png" alt="Enertherm Logo" ...>
```