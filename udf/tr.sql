DROP FUNCTION IF EXISTS sys_call;
DROP TRIGGER IF EXISTS after_machine_state_update;

CREATE FUNCTION sys_call RETURNS string SONAME 'libudf_sys.so';
 
DELIMITER %%
CREATE TRIGGER after_machine_state_update AFTER UPDATE
ON perf_machines
FOR EACH ROW
BEGIN
 DECLARE cmd CHAR(255);
 DECLARE res int(10);
 SET cmd = CONCAT('/home/sriee/Git/query/venv/bin/python ', '/home/sriee/Git/query/service/temp.py ', '--state ', NEW.state, ' --machine ', NEW.name);
 SET res = sys_call(cmd);	
END;
%%

DELIMITER ;
