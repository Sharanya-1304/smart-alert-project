# 🌐 Smart Alert Website - Complete Documentation

## Overview

Smart Alert is a modern web application that combines AI-powered computer vision with a beautiful glassmorphism UI to provide real-time fire and fall detection monitoring.

## Architecture

### Frontend Stack
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with glassmorphism effects
- **JavaScript** - Client-side interactivity (vanilla JS, no frameworks)
- **Responsive Design** - Mobile-first approach

### Backend Stack
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database
- **SQLite** - Lightweight database
- **YOLO** - Object detection & pose estimation
- **OpenCV** - Video processing

## Page-by-Page Breakdown

### 1. Welcome Page (`welcome.html`)

**Purpose**: Landing page for unauthenticated users

**Features**:
- Navigation bar with login/register buttons
- Hero section with description
- Features showcase (6 cards)
- Statistics section
- Responsive design
- Floating circle animations

**Color Scheme**:
- Gradient: #667eea → #764ba2
- Accent: #ffd86f (yellow)

**Components**:
```html
- Navigation bar
- Welcome section (text + SVG graphic)
- Feature cards grid
- Statistics (99.9% accuracy, <100ms alerts, etc.)
- Footer
```

### 2. Registration Page (`register.html`)

**Purpose**: User account creation

**Features**:
- Username/Email/Password inputs
- Password strength indicator
- Real-time validation
- Terms & conditions checkbox
- Login link for existing users
- Loading spinner on submit

**Validation**:
- Email format check
- Password matching
- Minimum 8 characters
- Username uniqueness

**Form Fields**:
```
- Full Name (username)
- Email Address
- Password (with strength meter)
- Confirm Password
- Terms acceptance checkbox
```

### 3. Login Page (`login.html`)

**Purpose**: User authentication

**Features**:
- Username and password fields
- Remember me checkbox
- Forgot password link
- Sign up link
- Input icons
- Real-time error messages

**Validation**:
- Required fields check
- Credential verification
- Session management

### 4. Dashboard (`dashboard.html`)

**Purpose**: Main hub after login - stats and monitoring

**Key Sections**:
- User profile card
- Statistics cards (5 metrics)
- Recent alerts table
- Real-time data updates

**Statistics Displayed**:
1. Total Alerts - Green badge
2. Fire Detected - Red badge (#ff6b6b)
3. Falls Detected - Yellow badge (#ffc400)
4. Proximity Events - Orange badge
5. Critical Alerts - Dark red badge

**Features**:
- Auto-refresh every 30 seconds
- Click alerts to view details
- Sort by type/severity
- Real-time counter updates

### 5. Detection Interface (`detection.html`)

**Purpose**: Start fire and fall detection

**Two Detection Cards**:

#### Fire Detection Card
- Color: Red gradient (#ff6b6b → #ff8e7b)
- Features listed:
  - Flame color detection
  - Person tracking
  - Proximity alerts
  - Real-time monitoring
- File upload option
- Start button

#### Fall Detection Card
- Color: Yellow gradient (#ffc400 → #ffb300)
- Features listed:
  - Pose estimation
  - Tilt detection
  - Fall alerts
  - Instant notifications
- File upload option
- Start button

**Functionality**:
- Async API call on button click
- Status message display
- Loading state with spinner
- Error handling

### 6. Alert History (`history.html`)

**Purpose**: Complete log of all detected events

**Table Columns**:
- Type (Fire/Fall/Proximity) - Color-coded badge
- Time - Formatted timestamp
- Severity - Color-coded badge (Critical/Warning/Info)
- Description - Alert details

**Features**:
- Pagination (shows 100 most recent)
- Color-coded type badges
- Severity indicators
- Searchable/sortable

### 7. Settings (`settings.html`)

**Purpose**: User account management

**Two Sections**:

#### Profile Information
- Username (read-only)
- Email (read-only)
- Account Type (role)
- Member Since date

#### Change Password
- Current Password field
- New Password field
- Confirm Password field
- Update button
- Cancel button

**Security**:
- Server-side password validation
- Minimum length requirement
- Confirmation matching

## Design System

### Color Palette
```css
Primary Gradient: #667eea → #764ba2
Accent Yellow:   #ffd86f
Text Dark:       #333333
Text Light:      white
Borders:         rgba(0,0,0,0.1)
Background:      rgba(255,255,255,0.1)
```

### Glassmorphism Effect
```css
background: rgba(255,255,255,0.1);
backdrop-filter: blur(15px);
border: 1px solid rgba(255,255,255,0.2);
box-shadow: 0 15px 35px rgba(0,0,0,0.3);
```

### Animations
- **Float**: Continuous Y-axis movement
- **Slide Down**: Message appearance
- **Spin**: Loading spinner
- **Shake**: Error animation
- **Fade**: General transitions

### Typography
- Font Family: Poppins (Google Fonts)
- Weights: 300, 400, 500, 600, 700
- Sizes: 12px - 52px responsive

### Spacing System
- Small: 8px, 12px
- Medium: 15px, 20px, 25px
- Large: 30px, 40px, 60px
- Extra: 80px+

## API Reference

### Authentication Endpoints

#### POST /register
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "confirm_password": "string"
}
```
Response: 201 Created or 400 Bad Request

#### POST /login
```json
{
  "username": "string",
  "password": "string"
}
```
Response: 200 OK with session or 401 Unauthorized

#### GET /logout
Clears session and redirects to welcome

### Dashboard API

#### GET /api/stats
Returns alert statistics
```json
{
  "total_alerts": 42,
  "fire_alerts": 5,
  "fall_alerts": 3,
  "proximity_alerts": 8,
  "critical_alerts": 12
}
```

#### GET /api/alerts?limit=10
Returns recent alerts
```json
[
  {
    "id": 1,
    "type": "fire",
    "timestamp": "2026-03-21 10:30:45",
    "severity": "CRITICAL",
    "description": "Fire detected near entrance"
  }
]
```

#### GET /api/user/profile
Returns user information
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "joined": "2026-03-21"
}
```

### Detection API

#### POST /api/start-detection
```json
{
  "type": "fire",
  "video_path": "optional_path.mp4"
}
```
Response: 200 OK with message

#### POST /api/user/update-password
```json
{
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

## Database Schema

### Users Table
```sql
CREATE TABLE user (
  id INTEGER PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password VARCHAR(200) NOT NULL,
  role VARCHAR(20) DEFAULT 'user',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Alerts Table
```sql
CREATE TABLE alert (
  id INTEGER PRIMARY KEY,
  alert_type VARCHAR(50) NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  severity VARCHAR(20),
  evidence_path VARCHAR(300),
  description TEXT,
  user_id INTEGER FOREIGN KEY
)
```

## Security Features

1. **Authentication**
   - Session-based with Flask
   - Password hashing with Werkzeug
   - Login required decorator

2. **Input Validation**
   - Server-side validation
   - Email format checking
   - Password strength requirements

3. **Database Security**
   - SQL Injection prevention (SQLAlchemy ORM)
   - CSRF protection ready
   - Parameterized queries

4. **Recommendations for Production**
   - Enable HTTPS/SSL
   - Implement rate limiting
   - Add CAPTCHA to registration
   - Use environment variables for secrets
   - Implement 2FA
   - Add audit logging

## Responsive Breakpoints

```css
Mobile (≤480px):
- Single column layouts
- Stacked navigation
- Touch-friendly buttons

Tablet (481px - 768px):
- 2 column grids
- Sidebar adjustments
- Optimized spacing

Desktop (≥769px):
- Multi-column grids
- Full navigation
- Enhanced spacing
```

## Performance Optimization

1. **Frontend**
   - Vanilla JS (no framework overhead)
   - Minimal animations
   - Efficient CSS selectors
   - Lazy loading ready

2. **Backend**
   - Database indexing on frequently queried fields
   - Connection pooling
   - Caching suggestions

3. **General**
   - CDN for icons (Font Awesome)
   - Google Fonts via CDN
   - Minified CSS/JS in production
   - Image optimization

## Customization Guide

### Change Primary Color
```css
Find: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Replace with your gradient
```

### Change Accent Color
```css
Find: #ffd86f
Replace with your accent color
```

### Modify Alert Types
Edit `app.py` database queries to include new types

### Add New Pages
1. Create HTML template in `templates/`
2. Add route in `app.py`
3. Update navigation links
4. Add styles if needed

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS 14+, Android 10+)

## Accessibility Features

- Semantic HTML structure
- ARIA labels on inputs
- Color contrast ratios meet WCAG AA
- Keyboard navigation support
- Focus visible states
- Form validation messages

## Future Enhancements

1. Dark mode theme
2. Multi-language support
3. Advanced filtering/search
4. Export reports as PDF
5. Real-time WebSocket alerts
6. Mobile app version
7. Advanced analytics
8. Custom alert rules
9. Integration with emergency services
10. Machine learning improvements

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: Production Ready
