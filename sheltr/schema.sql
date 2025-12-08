DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS emergencies; 
DROP TABLE IF EXISTS shelters; 
DROP TABLE IF EXISTS shelters_of_emergency;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS user_task;

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
    end_date date NOT NULL,
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
    task_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (task_id) REFERENCES task(id),
    PRIMARY KEY (user_id, task_id)
);

-- TEMPORARY INSERTIONS.
-- INSERT INTO user (username, email, password, name, phone, city) VALUES ('TestUser', 'test@test.test', 'password', 'TestUser', '1111111111', 'City');
INSERT INTO task (task_name, description, status, shelter_id) VALUES ('Task 1', 'Pending task for shelter 1.', 'pending', 1);
INSERT INTO task (task_name, description, status, shelter_id) VALUES ('Task 2', 'Current task for shelter 2.', 'in_progress', 2);
INSERT INTO task (task_name, description, status, shelter_id) VALUES ('Task 3', 'Finished task for shelter 3.', 'finished', 3);
INSERT INTO task (task_name, description, status, shelter_id) VALUES ('Task 4', 'Pending task for shelter 1.', 'pending', 1);
INSERT INTO task (task_name, description, status, shelter_id) VALUES ('Task 5', 'Current task for shelter 2.', 'in_progress', 2);
INSERT INTO task (task_name, description, status, shelter_id) VALUES ('Task 6', 'Finished task for shelter 3.', 'finished', 3);
INSERT INTO user_task (user_id, task_id) VALUES (1, 1);
INSERT INTO user_task (user_id, task_id) VALUES (1, 2);
INSERT INTO user_task (user_id, task_id) VALUES (1, 3);
INSERT INTO user_task (user_id, task_id) VALUES (1, 4);
INSERT INTO user_task (user_id, task_id) VALUES (1, 5);
INSERT INTO user_task (user_id, task_id) VALUES (1, 6);

INSERT INTO shelters (shelter_name, shelter_location, shelter_description) VALUES ('Looky', 'Bayamon', 'Headquarters of Looky');
INSERT INTO shelters (shelter_name, shelter_location, shelter_description) VALUES ('Sheltr', 'San Francisco', 'Headquarters of Sheltr');
INSERT INTO shelters (shelter_name, shelter_location, shelter_description) VALUES ('Lajas', 'Lajas', 'Lajas');