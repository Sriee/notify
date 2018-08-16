-- sed -i 's/\r//g'

USE perf;
DROP TABLE IF EXISTS perf_machines;

CREATE TABLE perf_machines (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    state VARCHAR(25) NOT NULL,
    name VARCHAR(30) NOT NULL
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

DELIMITER @@

-- Should set the length of char dynamically 

CREATE TRIGGER after_machine_state_update AFTER UPDATE
ON perf_machines
FOR EACH ROW
BEGIN
	DECLARE cmd CHAR(255);
	SET cmd=CONCAT('/path/to/venv/python.exe ', '/path/to/trigger.py ', '--state ', NEW.state, ' --machine ', NEW.name);
	sys_exec(cmd);	
END;
@@

DELIMITER;
