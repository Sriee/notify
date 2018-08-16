
#if defined(_WIN32) || defined(_WIN64) || defined(__WIN32__) || defined(WIN32)
#define DLLEXP __declspec(dllexport) 
#else
#define DLLEXP
#endif

#ifdef STANDARD
#include <string.h>
#include <stdlib.h>
#include <time.h>
#ifdef __WIN__
typedef unsigned __int64 ulonglong;
typedef __int64 longlong;
#else
typedef unsigned long long ulonglong;
typedef long long longlong;
#endif /*__WIN__*/
#else
#include <my_global.h>
#include <my_sys.h>
#endif
#include <mysql.h>
#include <m_ctype.h>
#include <m_string.h>
#include <stdlib.h>

#include <ctype.h>

#ifdef HAVE_DLOPEN
#ifdef	__cplusplus
extern "C" {
#endif

#define LIBVERSION "libudf_sys version 0.1"

/**
 * sys_call
 * 
 * executes the argument commandstring and returns its exit status.
 */
DLLEXP my_bool sys_call_init(UDF_INIT *initid, UDF_ARGS *args, char *message);

DLLEXP void sys_call_deinit(UDF_INIT *initid);

DLLEXP my_ulonglong sys_call(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error);

#ifdef	__cplusplus
}
#endif

my_bool sys_call_init(UDF_INIT *initid,	UDF_ARGS *args,	char *message) {
	if(args->arg_count == 1 && args->arg_type[0] == STRING_RESULT){
		return 0;
	} else {
		strncpy(message, "Expected exactly one string type parameter", 43);		
		return 1;
	}
}

void sys_call_deinit(UDF_INIT *initid) {}

my_ulonglong sys_call(UDF_INIT *initid,	UDF_ARGS *args,	char *is_null,	char *error) {
	return system(args->args[0]);
}

#endif /* HAVE_DLOPEN */
