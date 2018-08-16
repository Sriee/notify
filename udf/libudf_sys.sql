DROP FUNCTION IF EXISTS sys_call;

CREATE FUNCTION sys_call RETURNS string SONAME 'libudf_sys.so';