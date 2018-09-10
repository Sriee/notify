-- Create database call perf 
DROP DATABASE IF EXISTS perf;
CREATE DATABASE perf;
USE perf;

-- Create required tables
DROP TABLE IF EXISTS perf_machines;

CREATE TABLE perf_machines (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    state VARCHAR(25) NOT NULL,
    name VARCHAR(30) NOT NULL
);

-- Insert initial values into the table
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine1');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine2');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine3');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine4');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine5');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine6');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine7');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine8');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine9');
INSERT INTO perf_machines(state, name) VALUES('Pending', 'Machine10');
