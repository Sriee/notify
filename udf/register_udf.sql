DROP FUNCTION IF EXISTS sys_call;
DROP TRIGGER IF EXISTS after_machine_state_update;

CREATE FUNCTION sys_call RETURNS int SONAME 'libudf.so';
 
DELIMITER %%
CREATE TRIGGER after_machine_state_update AFTER UPDATE
ON test_machines
FOR EACH ROW
BEGIN
 DECLARE cmd CHAR(255);
 DECLARE res int(10);
 SET cmd = CONCAT('/path/to/notify/venv/bin/python ', '/path/to/notify/service/sender.py ', '--state ', NEW.state, ' --machine ', NEW.name);
 SET res = sys_call(cmd);	
END;
%%

DELIMITER ;
