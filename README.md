# MySQL Notification Service

## About

Notification Service project is based on Publisher Subscriber design pattern. It is used to receive notifications from mysql database changes. It is lightweight, fast and scalable. 
It is written using pythons asyncio framework which handles concurrency asynchronously

## Demo

I have a project (let's call it Project X) which goes through certain states and stores the state information on a mysql database. State diagram for project X is shown below. 

### Pre-requisite

1. Mysql allows interface for users to add *'user defined functions(UDF)'"[1]. MySQL doesn't provide inbuilt functions to call python programs within mysql databse. 
So I wrote a UDF function which calls python program *'(server/sender.py)'* within mysql database. To add UDF to mysql please install libmysqlclient-dev[2] on your machine.

2. Next we need to define what states the client want the server and trigger to send. I have configured the states I mentioned above in *'(helper.py)'*. 

The project setup for this demo is shown below. When clients connect to the server they have to subscribe to the states they are interested in.
![alt_title]()

> Please make sure trigger and client can reach the server

The notification flow will work as shown below
![alt_title]()

### Mysql Setup

I going to create a database called Test with one table, udf function and a trigger to call the udf function. 

1. sudo ./path/to/project/udf/install.sh 
   If you are getting error with udf registeration
      - Make sure you have installed libmysqlclient-dev on your machine
	  - You have admin writes to delete and update /usr/lib directory
	  - Check the installation path of mysql plugin. The default path where install.sh tries to install the mysql udf library is /usr/lib/mysql/plugin/
 
2. Login to mysql & Initialize it. `source /path/to/project/udf/initialize.sql`
3. Register UDF function. `source /path/to/project/udf/register_udf.sql`
 
### Start Server

`python service/server.py --host 192.168.1.5 --port 1300 -v &`

### Starting Trigger

`python service/trigger.py --host 192.168.1.5 --port 1300 --name my_trigger -v &`

### Start Clients 

I am going to start two clients. One client running on a *'Ubuntu 18.04'* and other on a *'Windows 10'*. 

```# Client 1 on Ubuntu 18.04
python service/client.py --host 192.168.1.5 --port 1300 --name debian --sub Error Suspended &

# Client 2 on Windows 10
python service/client.py --host 192.168.1.5 --port 1300 --name windows --sub Completed Error Imaging Suspended ```

Running a background service in Windows is little different from Ubuntu. I created a task using task scheduler[3] to run it as a background process. 

## Result

## Supported Environments

Tested on Windows and Linux based Operating Systems. It won't run on Mac OS as toast notification feature is not implemented.
Requires Python 3.5+ because of async/await syntax introduced in **asyncio framework** (porting it to earlier versions of python should be trivial).  

## References

[1]: Path to mysql udf functions
[2]: How to install libmysqlclient-dev
[3]: Path to windows task scheduler setup
