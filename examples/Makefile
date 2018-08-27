CC=gcc

CFLAGS=-Wall -fPIC

LDIR=/usr/lib/mysql/plugin

IDIR=-I/usr/include/mysql

all:
	$(CC) $(CFLAGS) $(IDIR) -shared udf_sys.c -o $(LDIR)/libudf.so

clean:
	rm $(LDIR)/libudf.so
