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
INSERT INTO perf_machines(state, name) VALUES('Pending', 'As203');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH16');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH17');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH18');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH19');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH20');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH21');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH5');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'HIGH6');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'MID4');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'MID5');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'MID32');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'MID33');
