-- Create database call perf 
DROP DATABASE IF EXISTS Test;
CREATE DATABASE Test;
USE Test;

-- Create required tables
DROP TABLE IF EXISTS test_machines;

CREATE TABLE test_machines (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    state VARCHAR(25) NOT NULL,
    name VARCHAR(30) NOT NULL
);

-- Insert initial values into the table
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine1');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine2');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine3');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine4');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine5');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine6');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine7');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine8');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine9');
INSERT INTO test_machines(state, name) VALUES('Pending', 'Machine10');
