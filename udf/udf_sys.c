
typedef unsigned long long ulonglong;

#include <mysql.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#ifdef	__cplusplus
extern "C" {
#endif

/**
 * sys_call
 * 
 * executes the argument commandstring and returns its exit status.
 */
bool sys_call_init(UDF_INIT *initid, UDF_ARGS *args, char *message);

void sys_call_deinit(UDF_INIT *initid);

ulonglong sys_call(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error);

#ifdef	__cplusplus
}
#endif

bool sys_call_init(UDF_INIT *initid,	UDF_ARGS *args,	char *message) {
	if(args->arg_count == 1 && args->arg_type[0] == STRING_RESULT){
		return 0;
	} else {
		strcpy(message, "Expected exactly one string type parameter");		
		return 1;
	}
}

void sys_call_deinit(UDF_INIT *initid) {}

ulonglong sys_call(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error) {
	return system(args->args[0]);
}

