# API Reference

All routes return HTML pages unless otherwise noted. Protected routes require authentication via JWT cookie.

## Authentication

### POST /auth/register

Register a new user account.

**Request Body (form data):**
```
username: string (required, unique)
email: string (required, unique, valid email format)
password: string (required, min 8 chars, uppercase, number, special char)
confirm_password: string (required, must match password)
name: string (required, max 100 chars)
phone: string (optional, max 10 digits)
city: string (optional, max 12 chars)
```

**Response:**
- Success: Redirect to `/auth/login`
- Error: Re-render form with validation errors

**Validation Rules:**
- Username must be unique
- Email must be valid format and unique
- Password: 8+ characters, 1 uppercase, 1 number, 1 special character
- Phone: digits only, max 10

---

### POST /auth/login

Authenticate user and create session.

**Request Body (form data):**
```
username: string (required)
password: string (required)
```

**Response:**
- Success: Redirect to `/` with JWT cookie set
- Error: Re-render form with error message

**Cookie Set:**
```
auth_token: JWT (HttpOnly, SameSite=Lax, 24h expiry)
```

**JWT Payload:**
```json
{
  "user_id": 1,
  "exp": 1234567890
}
```

---

### GET /auth/logout

Clear authentication and redirect to login.

**Response:** Redirect to `/auth/login`

**Actions:**
- Clears `auth_token` cookie
- Clears Flask session

---

### POST /auth/refresh

Refresh JWT token if expiring soon (within 2 hours).

**Request:** JWT cookie required

**Response:**
```json
{
  "success": true,
  "message": "Token refreshed"
}
```
or
```json
{
  "success": false,
  "message": "Token not expiring soon"
}
```

---

## Tasks

All task routes require authentication (`@login_required`).

### GET /tasks/

View tasks assigned to current user.

**Query Parameters:**
```
status: string (optional) - Filter by: pending, in_progress, finished
```

**Response:** HTML page with task list

**Template Data:**
```python
{
  "tasks": [Task],
  "current_status": str | None
}
```

---

### POST /tasks/update_status

Update task status via AJAX.

**Request Body (JSON):**
```json
{
  "task_id": 1,
  "status": "in_progress"
}
```

**Valid Status Values:**
- `pending`
- `in_progress`
- `finished`

**Response:**
```json
{
  "success": true
}
```
or
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Profile

All profile routes require authentication (`@login_required`).

### GET /profile/

View current user's profile.

**Response:** HTML page with user info

**Template Data:**
```python
{
  "user": User
}
```

---

### GET /profile/edit

Display profile edit form.

### POST /profile/edit

Update profile information.

**Request Body (form data):**
```
name: string (required, max 100 chars)
phone: string (optional, max 10 digits)
city: string (optional, max 12 chars)
```

**Response:**
- Success: Redirect to `/profile/`
- Error: Re-render form with validation errors

---

### GET /profile/password

Display password change form.

### POST /profile/password

Change user password.

**Request Body (form data):**
```
current_password: string (required)
new_password: string (required, same rules as registration)
confirm_password: string (required, must match new_password)
```

**Response:**
- Success: Redirect to `/profile/` with success message
- Error: Re-render form with validation errors

---

## Emergency

Emergency routes require authentication (`@login_required`).

### GET /emergency/

List all emergencies.

**Response:** HTML page with emergency list

**Template Data:**
```python
{
  "emergencies": [Emergency]
}
```

---

### GET /emergency/<id>

View specific emergency details.

**Parameters:**
- `id`: Emergency ID (integer)

**Response:** HTML page with emergency details (partially implemented)

---

## Content Pages

### GET /

Dashboard / home page.

**Auth:** Required (`@login_required`)

**Response:** HTML page with:
- Welcome message
- Navigation cards
- Manager section (if role is manager)

---

### GET /donations/

Donations page.

**Auth:** Required (`@login_required`)

**Response:** HTML page (placeholder)

---

### GET /disasters/

Disasters page.

**Auth:** Required (`@login_required`)

**Response:** HTML page (placeholder)

---

## Authentication Flow

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │      │   Server    │      │  Database   │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │  POST /auth/login  │                    │
       │ ─────────────────► │                    │
       │                    │  Query user        │
       │                    │ ─────────────────► │
       │                    │                    │
       │                    │  User data         │
       │                    │ ◄───────────────── │
       │                    │                    │
       │                    │  Verify password   │
       │                    │  Generate JWT      │
       │                    │                    │
       │  Set-Cookie: JWT   │                    │
       │ ◄───────────────── │                    │
       │                    │                    │
       │  GET /tasks/       │                    │
       │  Cookie: JWT       │                    │
       │ ─────────────────► │                    │
       │                    │  Decode JWT        │
       │                    │  Load user to g    │
       │                    │                    │
       │  HTML Response     │                    │
       │ ◄───────────────── │                    │
```

---

## Error Handling

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 302 | Redirect (after form submission) |
| 400 | Bad request (invalid form data) |
| 401 | Unauthorized (not logged in) |
| 403 | Forbidden (not a manager) |
| 404 | Not found |
| 500 | Server error |

### Flash Messages

Used for user feedback via Flask's `flash()`:

```python
flash("Success message", "success")
flash("Error message", "error")
flash("Warning message", "warning")
```

Displayed in templates via Bootstrap alerts.

---

## Rate Limiting

Currently not implemented. Recommended for production:
- Login: 5 attempts per minute
- Registration: 3 per hour
- API calls: 100 per minute
