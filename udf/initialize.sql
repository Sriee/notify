-- Create database call perf

DROP DATABASE IF EXISTS perf;
CREATE DATABASE perf;
USE perf;

-- Create required tables
DROP TABLE IF EXISTS perf_machines;
DROP TABLE IF EXISTS watch;

CREATE TABLE perf_machines (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    state VARCHAR(25) NOT NULL,
    name VARCHAR(30) NOT NULL
);

CREATE TABLE watch (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    old_state VARCHAR(25) NOT NULL,
    new_state VARCHAR(25) NOT NULL,
    py_call VARCHAR(255)
);

-- Insert initial values into the table
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High11');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High12');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High13');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High14');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High15');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High16');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High17');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High18');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High19');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High20');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High21');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High22');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High23');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High24');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'High25');
