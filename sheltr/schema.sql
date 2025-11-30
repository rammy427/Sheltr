DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS emergencies; 
DROP TABLE IF EXISTS shelters; 
DROP TABLE IF EXISTS shelters_of_emergency;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    end_date date NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (starting_date, shelter_id),
    FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id),
    FOREIGN KEY (emergency_id) REFERENCES emergencies(emergency_id)
);