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
    end_date date NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (starting_date, shelter_id),
    FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id),
    FOREIGN KEY (emergency_id) REFERENCES emergencies(emergency_id)
);
CREATE TABLE task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(11) NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_task (
    user_id INTEGER,
    task_id INTEGER,
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
    donation_message VARCHAR(400),
    FOREIGN KEY (emergency_id) REFERENCES emergencies(emergency_id)
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- TEMPORARY INSERTIONS.
INSERT INTO user (username, email, password, name, phone, city) VALUES ('testuser', 'test@test.test', 'Password1@', 'TestUser', '1111111111', 'City');
INSERT INTO task (task_name, description, status) VALUES ('Task 1', 'Pending task.', 'pending');
INSERT INTO task (task_name, description, status) VALUES ('Task 2', 'Current task.', 'in_progress');
INSERT INTO task (task_name, description, status) VALUES ('Task 3', 'Finished task.', 'finished');
INSERT INTO user_task (user_id, task_id) VALUES (1, 1);
INSERT INTO user_task (user_id, task_id) VALUES (1, 2);
INSERT INTO user_task (user_id, task_id) VALUES (1, 3);
INSERT INTO emergencies(emergency_name, emergency_status, emergency_date, image_url, emergency_description) VALUES ("Fuego en Ponce", True, "2020-05-10", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Large_bonfire.jpg/500px-Large_bonfire.jpg", "Fire is the rapid oxidation of a fuel in the exothermic chemical process of combustion, releasing heat, light, and various reaction products. Flames, the most visible portion of the fire, are produced in the combustion reaction when the fuel reaches its ignition point temperature. Flames from hydrocarbon fuels consist primarily of carbon dioxide, water vapor, oxygen, and nitrogen. If hot enough, the gases may become ionized to produce plasma. The color and intensity of the flame depend on the type of fuel and composition of the surrounding gases.");
INSERT INTO emergencies(emergency_name, emergency_status, emergency_date, image_url, emergency_description) VALUES ("Inundacion en Condado", False, "2025-07-11", "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/13/40/51/e0/aerial-images.jpg?w=900&h=500&s=1", "Condado es una comunidad frente al mar, bordeada de árboles, orientada a los peatones en San Juan, Puerto Rico. Es una zona de clase media a alta, está situado al este del centro histórico del Viejo San Juan. Es uno de los 40 «sub-barrios» de Santurce. La superficie de tierra es de 0,82 km² (824 791 m²), con una población de 6170 residentes según el censo de los Estados Unidos de 2000. La frontera oriental se caracteriza por la Avenida de Diego y de su extensión recta hacia la costa atlántica. En el sur, el distrito está delimitado por Calle Wilson, Calle Aldea, Expreso Baldorioty de Castro, Calle Piccioni y calle Delcasse, y por la Laguna del Condado (de este a oeste). El punto más occidental es el «Puente Dos Hermanos», donde termina la Avenida Ashford y comienza el San Juan Antiguo. En el norte están las playas del Océano Atlántico.");
INSERT INTO donation (emergency_id, user_id, donation_quantity, donation_message)
VALUES
    (1, 3, 50.00, 'Sending basic supplies to support affected families.'),
    (2, 5, 120.50, 'Cash donation to help with medical expenses.'),
    (1, 2, 75.25, 'Food and water for shelters.'),
    (3, 1, 300.00, 'Supporting long-term recovery and rebuilding efforts.'),
    (2, 4, 25.00, 'Small contribution, hope it helps a bit.');