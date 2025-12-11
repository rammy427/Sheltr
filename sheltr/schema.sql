DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS emergencies; 
DROP TABLE IF EXISTS shelters; 
DROP TABLE IF EXISTS shelters_of_emergency;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS user_task;
DROP TABLE IF EXISTS donation;

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    city TEXT,
    role TEXT NOT NULL DEFAULT 'volunteer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE emergencies (
    emergency_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emergency_name VARCHAR(100) NOT NULL,
    emergency_status BOOLEAN NOT NULL,
    emergency_date date NOT NULL,
    image_url VARCHAR(500),
    emergency_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shelters (
    shelter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shelter_name VARCHAR(80) NOT NULL,
    shelter_location VARCHAR(80) NOT NULL,
    shelter_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shelters_of_emergency (
    starting_date DATE NOT NULL,
    shelter_id INTEGER,
    emergency_id INTEGER,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (starting_date, shelter_id),
    FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id),
    FOREIGN KEY (emergency_id) REFERENCES emergencies(emergency_id)
);
CREATE TABLE task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name VARCHAR(50) NOT NULL,
    shelter_id INTEGER,
    description TEXT NOT NULL,
    status VARCHAR(11) NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id)
);

CREATE TABLE user_task (
    user_id INTEGER,
    task_id INTEGER UNIQUE,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (task_id) REFERENCES task(id),
    PRIMARY KEY (user_id, task_id)
);

CREATE TABLE donation (
    donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emergency_id INTEGER,
    user_id INTEGER,
    donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    donation_quantity DECIMAL(19,2), 
    payment_process_provider TEXT,
    donation_message VARCHAR(400),
    FOREIGN KEY (emergency_id) REFERENCES emergencies(emergency_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);
