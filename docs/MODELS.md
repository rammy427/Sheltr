# Data Models

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      user       │       │    user_task    │       │      task       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ user_id (PK)    │◄──────│ user_id (FK)    │       │ task_id (PK)    │
│ username        │       │ task_id (FK)    │──────►│ task_name       │
│ email           │       └─────────────────┘       │ description     │
│ password        │                                 │ status          │
│ name            │                                 │ completed_at    │
│ phone           │                                 │ created_at      │
│ city            │                                 └─────────────────┘
│ role            │
│ created_at      │
└─────────────────┘

┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│   emergencies   │       │shelters_of_emergency│       │    shelters     │
├─────────────────┤       ├─────────────────────┤       ├─────────────────┤
│ emergency_id(PK)│◄──────│ emergency_id (FK)   │       │ shelter_id (PK) │
│ emergency_name  │       │ shelter_id (FK)     │──────►│ shelter_name    │
│ emergency_status│       │ starting_date (PK)  │       │ shelter_location│
│ emergency_date  │       │ end_date            │       │ shelter_desc    │
│ image_url       │       │ created_at          │       │ created_at      │
│ emergency_desc  │       └─────────────────────┘       └─────────────────┘
│ created_at      │
└─────────────────┘
```

---

## Table Definitions

### user

Stores all user accounts (volunteers and managers).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| username | TEXT | UNIQUE, NOT NULL | Login username |
| email | TEXT | UNIQUE, NOT NULL | User email |
| password | TEXT | NOT NULL | PBKDF2 hashed password |
| name | TEXT | NOT NULL | Display name |
| phone | TEXT | | Phone number (10 digits max) |
| city | TEXT | | User's city (12 chars max) |
| role | TEXT | NOT NULL, DEFAULT 'volunteer' | 'volunteer' or 'manager' |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |

### task

Stores tasks that can be assigned to volunteers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| task_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| task_name | VARCHAR(50) | NOT NULL | Task title |
| description | TEXT | NOT NULL | Task details |
| status | VARCHAR(11) | NOT NULL | pending, in_progress, finished |
| completed_at | TIMESTAMP | | When task was completed |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Task creation time |

### user_task

Junction table linking users to their assigned tasks (many-to-many).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | FK → user(user_id), PK | User reference |
| task_id | INTEGER | FK → task(task_id), PK | Task reference |

### emergencies

Stores emergency/disaster events.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| emergency_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| emergency_name | VARCHAR(100) | NOT NULL | Emergency title |
| emergency_status | BOOLEAN | NOT NULL | Active (true) or resolved (false) |
| emergency_date | DATE | NOT NULL | When emergency occurred |
| image_url | VARCHAR(500) | | URL to emergency image |
| emergency_description | TEXT | | Detailed description |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### shelters

Stores shelter locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| shelter_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| shelter_name | VARCHAR(80) | NOT NULL | Shelter name |
| shelter_location | VARCHAR(80) | NOT NULL | Physical address/location |
| shelter_description | TEXT | | Details about the shelter |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### shelters_of_emergency

Junction table linking shelters to emergencies with operational dates.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| starting_date | DATE | NOT NULL, PK | When shelter opened for emergency |
| shelter_id | INTEGER | FK → shelters(shelter_id), PK | Shelter reference |
| emergency_id | INTEGER | FK → emergencies(emergency_id) | Emergency reference |
| end_date | DATE | NOT NULL | When shelter closed |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

---

## Model Classes

### User (`sheltr/models/user.py`)

Base model for all users.

```python
class User:
    # Class attributes
    id: int
    username: str
    email: str
    password: str  # Hashed
    name: str
    phone: str | None
    city: str | None
    role: str  # 'volunteer' or 'manager'
    created_at: datetime
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create()` | username, email, password, name, phone, city | User | Factory with validation |
| `get_by_id()` | user_id | User \| None | Find by primary key |
| `get_by_username()` | username | User \| None | Find by username |
| `get_by_email()` | email | User \| None | Find by email |

**Instance Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `verify_password()` | password | bool | Check password hash |
| `update()` | name, phone, city | bool | Update profile fields |
| `update_password()` | current, new | bool | Change password |
| `is_volunteer()` | | bool | Check if volunteer role |
| `is_manager()` | | bool | Check if manager role |
| `to_dict()` | | dict | Serialize (no password) |

**Validation Methods:**

| Method | Rules |
|--------|-------|
| `validate_password()` | 8+ chars, 1 uppercase, 1 number, 1 special char |
| `validate_email()` | RFC-compliant email format |
| `validate_phone()` | Digits only, max 10 |
| `validate_name()` | Required, max 100 chars |
| `validate_city()` | Optional, max 12 chars |

---

### Volunteer (`sheltr/models/volunteer.py`)

Extends User for volunteer-specific functionality.

```python
class Volunteer(User):
    # Inherited from User
    role = 'volunteer'

    # Additional
    _tasks: list[Task] | None  # Lazy-loaded
```

**Instance Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_tasks()` | list[Task] | Get all assigned tasks |

---

### Manager (`sheltr/models/manager.py`)

Extends User for manager-specific functionality.

```python
class Manager(User):
    role = 'manager'
```

Currently minimal; extensible for future features.

---

### Task (`sheltr/models/task.py`)

Represents an assignable task.

```python
class Task:
    id: int
    name: str
    description: str
    status: str  # 'pending', 'in_progress', 'finished'
    completed_at: datetime | None
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_by_id()` | task_id | Task \| None | Find by primary key |

**Instance Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `update_status()` | new_status | bool | Change status |

**Status Values:**

```python
VALID_STATUSES = ['pending', 'in_progress', 'finished']
```

---

### Emergency (`sheltr/models/emergency.py`)

Represents an emergency/disaster event.

```python
class Emergency:
    id: int
    name: str
    status: bool  # True = active
    date: date
    img_url: str | None
    description: str | None
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `new_emergency()` | name, status, date, img, desc | Emergency | Create new |
| `edit_em()` | id, name, status, date, img, desc | bool | Update existing |

**Instance Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `isActive()` | bool | Check if emergency is active |

---

## Database Connection

### Getting a Connection

```python
from sheltr.db import get_db

db = get_db()
cursor = db.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
row = cursor.fetchone()
```

### Row Factory

The database is configured with `sqlite3.Row` as the row factory, allowing column access by name:

```python
row = db.execute("SELECT * FROM user WHERE user_id = ?", (1,)).fetchone()
print(row['username'])  # Access by column name
print(row[1])           # Access by index
```

### Transactions

Changes require explicit commit:

```python
db = get_db()
db.execute("INSERT INTO user (...) VALUES (...)", (...))
db.commit()  # Save changes
```

Connection is automatically closed at end of request via Flask teardown.

---

## Indexes

Default indexes (created automatically):

- `user.user_id` - PRIMARY KEY
- `user.username` - UNIQUE
- `user.email` - UNIQUE
- `task.task_id` - PRIMARY KEY
- `emergencies.emergency_id` - PRIMARY KEY
- `shelters.shelter_id` - PRIMARY KEY

**Recommended Additional Indexes:**

```sql
-- For task filtering by status
CREATE INDEX idx_task_status ON task(status);

-- For user lookup by role
CREATE INDEX idx_user_role ON user(role);

-- For emergency lookup by status
CREATE INDEX idx_emergency_status ON emergencies(emergency_status);
```
