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
role: string (optional, 'volunteer' or 'manager', default: 'volunteer')
availability: string (optional, one of: full-time, part-time, weekends, flexible)
skills: string (optional, max 500 chars)
preferred_shelter_id: integer (optional, must reference existing shelter)
latitude: float (optional, -90 to 90)
longitude: float (optional, -180 to 180)
```

**Response:**
- Success: Redirect to `/auth/login`
- Error: Re-render form with validation errors

**Validation Rules:**
- Username must be unique
- Email must be valid format and unique
- Password: 8+ characters, 1 uppercase, 1 number, 1 special character
- Phone: digits only, max 10
- If latitude provided, longitude required (and vice versa)

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
auth_token: JWT (HttpOnly, SameSite=Strict, 24h expiry)
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

**Response:** Redirect to `/`

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
  "message": "Token refreshed"
}
```
or
```json
{
  "message": "Token still valid"
}
```

**Error Response (401):**
```json
{
  "error": "No token provided"
}
```

---

### GET/POST /auth/forgot

Display and handle password reset request.

**POST Request Body (form data):**
```
identifier: string (username or email)
```

**Response:**
- Success: Redirect to `/auth/login` with flash message
- Error: Re-render form with validation error

---

## Admin (Manager Only)

All admin routes require manager role (`@manager_required`).

### GET /admin/

Admin dashboard main page.

**Response:** HTML page with admin navigation

---

### GET /admin/shelters

View all shelters.

**Response:** HTML page with shelter list

**Template Data:**
```python
{
  "shelters": [Shelter]
}
```

---

### GET /admin/shelters/<shelter_id>

View specific shelter with tasks.

**Parameters:**
- `shelter_id`: Shelter ID (integer)

**Query Parameters:**
```
status: string[] (optional) - Filter tasks by status: pending, in_progress, finished
```

**Response:** HTML page with shelter details and tasks

**Template Data:**
```python
{
  "shelter": Shelter,
  "tasks": [Task],
  "status": [str]
}
```

---

### GET/POST /admin/shelters/<shelter_id>/<task_id>

View and update a specific task.

**Parameters:**
- `shelter_id`: Shelter ID (integer)
- `task_id`: Task ID (integer)

**POST Request Body (form data):**
```
name: string (required, max 50 chars)
description: string (required, max 1000 chars)
volunteer: string (volunteer ID or '-1' to unassign)
```

**Response:**
- GET: HTML form with task details
- POST Success: Redirect to `/admin/shelters/<shelter_id>`
- POST Error: Re-render form with validation errors

---

### GET/POST /admin/shelters/<shelter_id>/add

Create a new task for a shelter.

**Parameters:**
- `shelter_id`: Shelter ID (integer)

**POST Request Body (form data):**
```
name: string (required, max 50 chars)
description: string (required, max 1000 chars)
volunteer: string (optional, volunteer ID or '-1')
```

**Response:**
- GET: HTML form for new task
- POST Success: Redirect to `/admin/shelters/<shelter_id>`
- POST Error: Re-render form with validation errors

---

### GET /admin/emergencies

View all emergencies.

**Response:** HTML page with emergency list

**Template Data:**
```python
{
  "emergencies": [Emergency]
}
```

---

### GET/POST /admin/emergencies/<e_id>

View and update a specific emergency.

**Parameters:**
- `e_id`: Emergency ID (integer)

**POST Request Body (form data):**
```
name: string (required)
description: string (optional)
status: string (active status)
```

**Response:**
- GET: HTML form with emergency details, assigned shelters, and all shelters
- POST Success: Redirect to `/admin/emergencies`
- POST Error: Re-render form with validation errors

**Template Data (GET):**
```python
{
  "emergency": Emergency,
  "assigned_shelters": [Shelter],
  "shelters": [Shelter]
}
```

---

### GET/POST /admin/shelters/add

Create a new emergency.

**POST Request Body (form data):**
```
name: string (required)
description: string (optional)
status: string (active status)
```

**Response:**
- GET: HTML form for new emergency
- POST Success: Redirect to `/admin/emergencies`
- POST Error: Re-render form with validation errors

---

### GET /admin/reports

View analytics dashboard with statistics.

**Response:** HTML page with comprehensive statistics

**Template Data:**
```python
{
  "total_emergencies": int,
  "active_emergencies": int,
  "inactive_emergencies": int,
  "total_shelters": int,
  "total_volunteers": int,
  "total_managers": int,
  "total_tasks": int,
  "completed_tasks": int,
  "pending_tasks": int,
  "in_progress_tasks": int,
  "total_donations": int,
  "total_donation_amount": float,
  "recent_donations": [Row],  # Last 5 donations with username and emergency name
  "top_emergencies": [Row]    # Top 5 emergencies by donation amount
}
```

---

## Tasks

All task routes require authentication (`@login_required`).

### GET /tasks/

View tasks assigned to current user.

**Query Parameters:**
```
status: string[] (optional) - Filter by: pending, in_progress, finished
```

**Response:** HTML page with task list

**Template Data:**
```python
{
  "tasks": [Task],
  "status": [str]
}
```

---

### POST /tasks/update_status

Update task status via AJAX.

**Request Body (JSON):**
```json
{
  "id": 1,
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
  "error": "Task not found"
}
```

---

### DELETE /tasks/<task_id>

Delete a task (manager only).

**Auth:** `@manager_required`

**Parameters:**
- `task_id`: Task ID (integer)

**Response:** 204 No Content

---

### POST /tasks/<task_id>/<user_id>

Assign a volunteer to a task.

**Parameters:**
- `task_id`: Task ID (integer)
- `user_id`: User/Volunteer ID (integer)

**Response:**
- Success: 204 No Content with flash message
- Error (404): Volunteer or Task not found
- Error (500): Task already taken

---

## Shelters

All shelter routes require authentication (`@login_required`).

### GET /shelters/

View all shelters.

**Response:** HTML page with shelter list

**Template Data:**
```python
{
  "shelters": [Shelter]
}
```

---

### GET /shelters/<shelter_id>

View specific shelter with tasks.

**Parameters:**
- `shelter_id`: Shelter ID (integer)

**Response:** HTML page with shelter details and available tasks

**Template Data:**
```python
{
  "user": User,
  "shelter": Shelter,
  "tasks": [Task]
}
```

---

## Emergency

Emergency routes require authentication (`@login_required`) unless otherwise noted.

### GET /emergency/

List all emergencies.

**Response:** HTML page with emergency list

**Template Data:**
```python
{
  "emergency": [Emergency]
}
```

---

### GET /emergency/<e_id>

View specific emergency details with map.

**Parameters:**
- `e_id`: Emergency ID (integer)

**Response:** HTML page with emergency details, assigned shelters, and interactive map

**Template Data:**
```python
{
  "emergency": Emergency,
  "shelters": [Shelter],
  "map": str  # Rendered Folium map HTML
}
```

---

### DELETE /emergency/<e_id>

Delete an emergency (manager only).

**Auth:** `@manager_required`

**Parameters:**
- `e_id`: Emergency ID (integer)

**Response:** 204 No Content

---

### POST /emergency/<e_id>/<s_id>

Link a shelter to an emergency (manager only).

**Auth:** `@manager_required`

**Parameters:**
- `e_id`: Emergency ID (integer)
- `s_id`: Shelter ID (integer)

**Response:**
- Success: 204 No Content
- Error (404): Emergency or Shelter not found
- Error (500): Database error

---

### DELETE /emergency/<e_id>/<s_id>

Unlink a shelter from an emergency (manager only).

**Auth:** `@manager_required`

**Parameters:**
- `e_id`: Emergency ID (integer)
- `s_id`: Shelter ID (integer)

**Response:**
- Success: 204 No Content
- Error (404): Emergency or Shelter not found
- Error (500): Database error

---

## Donations

All donation routes require authentication (`@login_required`).

### GET /donations/

View the 10 most recent donations.

**Response:** HTML page with donation list

**Template Data:**
```python
{
  "donations": [Row]  # username, emergency_name, donation_date, donation_quantity, donation_message
}
```

---

### GET/POST /donations/make-donation

Create a new donation.

**POST Request Body (form data):**
```
emergency_id: integer (required, must be active emergency)
amount: decimal (required, minimum $1.00)
provider: string (required, one of: Paypal, Venmo, Apple Pay, Credit Card)
msg: string (optional, max 400 chars, alphanumeric only)
```

**Response:**
- GET: HTML form with active emergencies dropdown
- POST Success: Redirect to `/donations/payment-mockup`
- POST Error: Re-render form with validation errors

**Template Data (GET):**
```python
{
  "emergencies": [Row]  # emergency_id, emergency_name (active only)
}
```

---

### GET /donations/user-donation-history.html

View current user's donation history (50 most recent).

**Response:** HTML page with user's donations and statistics

**Template Data:**
```python
{
  "donations": [dict],      # emergency_name, donation_date, donation_quantity, donation_message
  "total_donations": int,   # Count of user's donations
  "sum": Decimal           # Total amount donated by user
}
```

---

### GET /donations/payment-mockup

Display payment mockup page.

**Query Parameters:**
```
provider: string (payment provider name)
amount: string (donation amount)
donation_id: integer (created donation ID)
```

**Response:** HTML page with payment mockup interface

---

### POST /donations/complete-payment

Complete the payment mockup.

**Response:** Redirect to `/donations/` with success flash message

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

## Content Pages

### GET /

Dashboard / home page.

**Auth:** Required (`@login_required`)

**Response:**
- If not authenticated: Redirect to `/auth/login`
- If authenticated: HTML page with welcome message and navigation

---

## Authentication Flow

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│     Client      │      │     Server      │      │    Database     │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         │  POST /auth/login      │                        │
         │ ─────────────────────► │                        │
         │                        │  Query user            │
         │                        │ ─────────────────────► │
         │                        │                        │
         │                        │  User data             │
         │                        │ ◄───────────────────── │
         │                        │                        │
         │                        │  Verify password       │
         │                        │  Generate JWT          │
         │                        │                        │
         │  Set-Cookie: JWT       │                        │
         │ ◄───────────────────── │                        │
         │                        │                        │
         │  GET /tasks/           │                        │
         │  Cookie: JWT           │                        │
         │ ─────────────────────► │                        │
         │                        │  Decode JWT            │
         │                        │  Load user to g        │
         │                        │                        │
         │  HTML Response         │                        │
         │ ◄───────────────────── │                        │
```

---

## Authorization Decorators

### @login_required

Requires valid JWT token or session. Redirects to `/auth/login` if not authenticated.

### @manager_required

Requires valid authentication AND `role == 'manager'`. Redirects to:
- `/auth/login` if not authenticated
- `/` with error flash if not a manager

---

## Error Handling

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 204 | Success (no content, used for DELETE) |
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
flash("Info message", "danger")
```

Displayed in templates via Bootstrap alerts.

---

## Rate Limiting

Currently not implemented. Recommended for production:
- Login: 5 attempts per minute
- Registration: 3 per hour
- API calls: 100 per minute
