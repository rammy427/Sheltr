DROP TABLE IF EXISTS user;
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

CREATE TABLE task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name VARCHAR(50),
    description TEXT,
    status VARCHAR(11),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
INSERT INTO task (task_name, description, status) VALUES ('Task 1', 'Pending task.', 'pending');
INSERT INTO task (task_name, description, status) VALUES ('Task 2', 'Current task.', 'in_progress');
INSERT INTO task (task_name, description, status) VALUES ('Task 3', 'Finished task.', 'finished');
INSERT INTO user_task (user_id, task_id) VALUES (1, 1);
INSERT INTO user_task (user_id, task_id) VALUES (1, 2);
INSERT INTO user_task (user_id, task_id) VALUES (1, 3);