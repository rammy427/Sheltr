# Data Models

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│        user         │       │    user_task    │       │      task       │
├─────────────────────┤       ├─────────────────┤       ├─────────────────┤
│ user_id (PK)        │◄──────│ user_id (FK)    │       │ task_id (PK)    │
│ username            │       │ task_id (FK)    │──────►│ task_name       │
│ email               │       └─────────────────┘       │ shelter_id (FK) │
│ password            │                                 │ description     │
│ name                │                                 │ status          │
│ phone               │                                 │ completed_at    │
│ city                │                                 │ created_at      │
│ role                │                                 └────────┬────────┘
│ availability        │                                          │
│ skills              │       ┌─────────────────┐                │
│ preferred_shelter_id│──────►│    shelters     │◄───────────────┘
│ latitude            │       ├─────────────────┤
│ longitude           │       │ shelter_id (PK) │
│ created_at          │       │ shelter_name    │
└─────────┬───────────┘       │ shelter_location│
          │                   │ shelter_desc    │
          │                   │ created_at      │
          │                   └────────┬────────┘
          │                            │
          │                            │
          ▼                            ▼
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│      donation       │       │shelters_of_emergency│       │   emergencies   │
├─────────────────────┤       ├─────────────────────┤       ├─────────────────┤
│ donation_id (PK)    │       │ starting_date (PK)  │       │ emergency_id(PK)│
│ emergency_id (FK)   │──────►│ shelter_id (FK, PK) │◄──────│ emergency_name  │
│ user_id (FK)        │       │ emergency_id (FK)   │──────►│ emergency_status│
│ donation_date       │       │ end_date            │       │ emergency_date  │
│ donation_quantity   │       │ created_at          │       │ image_url       │
│ payment_provider    │       └─────────────────────┘       │ emergency_desc  │
│ donation_message    │                                     │ created_at      │
└─────────────────────┘                                     └─────────────────┘
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
| availability | TEXT | | Volunteer availability: full-time, part-time, weekends, flexible |
| skills | TEXT | | Volunteer skills (500 chars max) |
| preferred_shelter_id | INTEGER | FK → shelters(shelter_id) | Volunteer's preferred shelter |
| latitude | REAL | | User's location latitude (-90 to 90) |
| longitude | REAL | | User's location longitude (-180 to 180) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |

### task

Stores tasks that can be assigned to volunteers and associated with shelters.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| task_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| task_name | VARCHAR(50) | NOT NULL | Task title |
| shelter_id | INTEGER | FK → shelters(shelter_id) | Associated shelter |
| description | TEXT | NOT NULL | Task details (1000 chars max) |
| status | VARCHAR(11) | NOT NULL | pending, in_progress, finished |
| completed_at | TIMESTAMP | | When task was completed |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Task creation time |

### user_task

Junction table linking users to their assigned tasks.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | FK → user(user_id), PK | User reference |
| task_id | INTEGER | FK → task(task_id), PK, UNIQUE | Task reference (one user per task) |

**Note:** The `task_id` UNIQUE constraint ensures each task can only be assigned to one volunteer.

### emergencies

Stores emergency/disaster events.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| emergency_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| emergency_name | VARCHAR(100) | NOT NULL | Emergency title |
| emergency_status | BOOLEAN | NOT NULL | Active (1) or resolved (0) |
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
| shelter_location | VARCHAR(80) | NOT NULL | Format: "City,latitude,longitude" |
| shelter_description | TEXT | | Details about the shelter |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### shelters_of_emergency

Junction table linking shelters to emergencies with operational dates.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| starting_date | DATE | NOT NULL, PK | When shelter opened for emergency |
| shelter_id | INTEGER | FK → shelters(shelter_id), PK | Shelter reference |
| emergency_id | INTEGER | FK → emergencies(emergency_id) ON DELETE CASCADE | Emergency reference |
| end_date | DATE | | When shelter closed |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### donation

Stores monetary donations for emergencies.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| donation_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| emergency_id | INTEGER | FK → emergencies(emergency_id) ON DELETE CASCADE | Target emergency |
| user_id | INTEGER | FK → user(user_id) | Donor reference |
| donation_date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When donation was made |
| donation_quantity | DECIMAL(19,2) | | Amount donated (min $1.00) |
| payment_process_provider | TEXT | | Paypal, Venmo, Apple Pay, Credit Card |
| donation_message | VARCHAR(400) | | Optional message (alphanumeric) |

---

## Model Classes

### User (`sheltr/models/user.py`)

Base model for all users.

```python
class User:
    # Instance attributes
    id: int
    username: str
    email: str
    password: str           # Hashed
    name: str
    phone: str | None
    city: str | None
    role: str               # 'volunteer' or 'manager'
    availability: str | None  # full-time, part-time, weekends, flexible
    skills: str | None
    preferred_shelter_id: int | None
    latitude: float | None
    longitude: float | None
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create()` | username, email, password, name, phone, city, role, availability, skills, preferred_shelter_id, latitude, longitude | (User, error) | Factory with full validation |
| `get_by_id()` | user_id | User \| None | Find by primary key |
| `get_by_username()` | username | User \| None | Find by username |
| `get_by_email()` | email | User \| None | Find by email |

**Instance Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `verify_password()` | password | bool | Check password hash |
| `update()` | name, phone, city | (bool, error) | Update profile fields |
| `update_password()` | old_password, new_password | (bool, error) | Change password |
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
| `validate_availability()` | One of: full-time, part-time, weekends, flexible |
| `validate_skills()` | Optional, max 500 chars |
| `validate_coordinates()` | Both lat/lon required if one provided, valid ranges |

---

### Volunteer (`sheltr/models/volunteer.py`)

Extends User for volunteer-specific functionality.

```python
class Volunteer(User):
    # Inherited from User
    role = 'volunteer'

    # Additional
    tasks: list[Task]  # Lazy-loaded
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create()` | username, email, password, name, phone, city | (User, error) | Create volunteer user |
| `get_all()` | | list[Volunteer] | Get all volunteers |

**Instance Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_tasks()` | | list[Task] | Get all assigned tasks |
| `assign_task()` | task_id | (bool, error) | Assign task to volunteer |

---

### Manager (`sheltr/models/manager.py`)

Extends User for manager-specific functionality.

```python
class Manager(User):
    role = 'manager'
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create()` | username, email, password, name, phone, city | (User, error) | Create manager user |

---

### Task (`sheltr/models/task.py`)

Represents an assignable task associated with a shelter.

```python
class Task:
    id: int
    name: str
    description: str
    status: str              # 'pending', 'in_progress', 'finished'
    completed_at: datetime | None
    volunteer: Volunteer | None  # Lazy-loaded
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_by_id()` | task_id | Task \| None | Find by primary key |
| `create()` | name, description, status, volunteer_id, shelter_id | (Task, error) | Create new task with validation |

**Instance Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `update()` | name, description, volunteer_id | (bool, error) | Update task fields |
| `update_status()` | status | (bool, error) | Change status (sets completed_at if finished) |
| `delete()` | | None | Delete task from database |
| `get_volunteer()` | | Volunteer \| None | Get assigned volunteer |
| `set_shelter()` | db, shelter_id | None | Update shelter assignment |
| `set_volunteer()` | db, volunteer_id | None | Update volunteer assignment |

**Validation Methods:**

| Method | Rules |
|--------|-------|
| `validate_name()` | Required, max 50 chars |
| `validate_description()` | Required, max 1000 chars |
| `validate_status()` | Must be pending, in_progress, or finished |
| `validate_shelter()` | Shelter must exist |
| `validate_volunteer()` | Volunteer must exist (or '-1' to remove) |
| `validate_completion_date()` | Valid timestamp format (YYYY-MM-DD HH:MM:SS) |

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
    status: bool             # True = active
    date: date
    img_url: str | None
    description: str | None
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `new_emergency()` | name, status, date, img_url, description | (bool, error) | Create new emergency |
| `get_one_by_id()` | e_id | Emergency \| None | Find by primary key |
| `get_all()` | | list[Emergency] | Get all emergencies |
| `get_all_by_status()` | status | list[Emergency] | Get emergencies by status |
| `assigned_shelters()` | e_id | list[Shelter] | Get shelters for emergency |
| `remove_em()` | e_id | None | Delete emergency |

**Instance Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `edit_em()` | name, date, img_url, description, status | (bool, error) | Update emergency |
| `assign_shelter()` | shelter_id | (bool, error) | Link shelter to emergency |
| `remove_shelter()` | shelter_id | (bool, error) | Unlink shelter from emergency |
| `isActive()` | | bool | Check if emergency is active |
| `to_dict()` | | dict | Convert to dictionary |

---

### Shelter (`sheltr/models/shelter.py`)

Represents a shelter location where tasks are performed.

```python
class Shelter:
    id: int
    name: str
    location: str            # Format: "City,latitude,longitude"
    description: str | None
    tasks: list[Task]        # Lazy-loaded
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_all()` | | list[Shelter] | Get all shelters |
| `get_by_id()` | shelter_id | Shelter \| None | Find by primary key |

**Instance Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_tasks()` | list[Task] | Get all tasks assigned to this shelter |

---

### Donation (`sheltr/models/donation.py`)

Represents a monetary donation for an emergency.

```python
class Donation:
    id: int
    emergency_id: int
    emergency_name: str | None  # For display purposes
    user_id: int
    date: datetime
    quantity: Decimal
    message: str | None
    provider: str            # Paypal, Venmo, Apple Pay, Credit Card
```

**Class Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create()` | emergency_id, user_id, amount, message, date, provider | (Donation, error) | Create with validation |
| `get_by_id()` | donation_id | Donation \| None | Find by primary key |
| `list_recent()` | limit=10 | list[Donation] | Get recent donations |
| `user_donation_history()` | user_id, limit=50 | list[dict] | Get user's donation history |
| `emergency_donation_history()` | emergency_id, limit=50 | list[Donation] | Get emergency donations |
| `sum_by_emergency()` | emergency_id | Decimal | Total donations for emergency |
| `sum_by_user_donation()` | user_id | Decimal | Total donations by user |
| `count_by_emergency()` | emergency_id | int | Count donations for emergency |
| `count_by_donations()` | user_id | int | Count donations by user |

**Instance Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `to_dict()` | dict | Convert to dictionary |

**Validation Methods:**

| Method | Rules |
|--------|-------|
| `validate_quantity()` | Required, minimum $1.00, decimal precision |
| `validate_msg()` | Optional, max 400 chars, alphanumeric only |
| `validate_provider()` | Required, one of: Paypal, Venmo, Apple Pay, Credit Card |
| `validate_ids()` | Both emergency_id and user_id required, positive integers |

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

## Foreign Key Relationships

| Table | Foreign Key | References | On Delete |
|-------|-------------|------------|-----------|
| user | preferred_shelter_id | shelters(shelter_id) | - |
| task | shelter_id | shelters(shelter_id) | - |
| user_task | user_id | user(user_id) | - |
| user_task | task_id | task(task_id) | CASCADE |
| shelters_of_emergency | shelter_id | shelters(shelter_id) | - |
| shelters_of_emergency | emergency_id | emergencies(emergency_id) | CASCADE |
| donation | emergency_id | emergencies(emergency_id) | CASCADE |
| donation | user_id | user(user_id) | - |

---

## Indexes

Default indexes (created automatically):

- `user.user_id` - PRIMARY KEY
- `user.username` - UNIQUE
- `user.email` - UNIQUE
- `task.task_id` - PRIMARY KEY
- `user_task.task_id` - UNIQUE
- `emergencies.emergency_id` - PRIMARY KEY
- `shelters.shelter_id` - PRIMARY KEY
- `donation.donation_id` - PRIMARY KEY

**Recommended Additional Indexes:**

```sql
-- For task filtering by status
CREATE INDEX idx_task_status ON task(status);

-- For user lookup by role
CREATE INDEX idx_user_role ON user(role);

-- For emergency lookup by status
CREATE INDEX idx_emergency_status ON emergencies(emergency_status);

-- For donation queries
CREATE INDEX idx_donation_user ON donation(user_id);
CREATE INDEX idx_donation_emergency ON donation(emergency_id);
CREATE INDEX idx_donation_date ON donation(donation_date);
```
