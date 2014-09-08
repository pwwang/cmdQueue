cmdQueue
========

A job queue implemented in Python and sqlite3
Avaible on windows and *nix (maybe OSX, not tested)


Usage
-----

* Add a job:
	usage: cmdQueue.py add [-h] -n NAME -c CMD

	optional arguments:
	  -h, --help            show this help message and exit
	  -n NAME, --name NAME
	  -c CMD, --cmd CMD

* List workers and jobs:
	$ python cmdQueue.py list
	! Workers
	! #   PID    Paused?  StartDate
	1     8388   0        2014-09-08 08:16:52
	2     4116   0        2014-09-08 08:16:52
	3     5680   0        2014-09-08 08:16:52
	4     4328   0        2014-09-08 08:16:52
	5     6660   0        2014-09-08 08:16:52

	! Jobs
	! #   Name       Pid    Status     Priority   SubmitDate             StartDate              FinishDate             Command
	17    Test       10216  COMPLETE   0          2014-09-07 03:48:40    2014-09-08 07:50:06    2014-09-08 07:50:26    php -r "sleep(20);"
	15    Test       2468   COMPLETE   0          2014-09-07 03:48:39    2014-09-08 07:50:03    2014-09-08 07:50:23    php -r "sleep(20);"
	16    Test       5816   COMPLETE   0          2014-09-07 03:48:39    2014-09-08 07:50:05    2014-09-08 07:50:26    php -r "sleep(20);"
	14    Test       9060   COMPLETE   0          2014-09-07 03:48:38    2014-09-08 07:49:45    2014-09-08 07:50:05    php -r "sleep(20);"
	12    Test       7268   COMPLETE   0          2014-09-07 03:48:37    2014-09-08 07:49:42    2014-09-08 07:50:03    php -r "sleep(20);"
	13    Test       2072   COMPLETE   0          2014-09-07 03:48:37    2014-09-08 07:49:45    2014-09-08 07:50:05    php -r "sleep(20);"
	11    Test       7340   COMPLETE   0          2014-09-07 03:48:36    2014-09-08 07:49:25    2014-09-08 07:49:45    php -r "sleep(20);"
	10    Test       5504   COMPLETE   0          2014-09-07 03:48:35    2014-09-08 07:49:22    2014-09-08 07:49:42    php -r "sleep(20);"
	9     Test       3612   COMPLETE   0          2014-09-07 03:48:32    2014-09-08 07:49:21    2014-09-08 07:49:42    php -r "sleep(20);"
	8     Test       8288   COMPLETE   0          2014-09-07 03:45:06    2014-09-08 07:49:05    2014-09-08 07:49:25    php -r "sleep(20);"

* Start the queue:
	python cmdQueue.py start
	
* Stop the queue:
	python cmdQueue.py stop
	
* Restart the queue:
	python cmdQueue.py restart
	
* Pause a worker:
	python cmdQueue.py pause -p PID
	
* Resume a worker:
	python cmdQueue.py resume -p PID
	
* Reset the queue (remove all workers and jobs)
	python cmdQueue.py reset
	
* Reset job status (set the status of all jobs to PENDING)
	python cmdQueue.py resetjobs
	
* Setup queue (create the database and tables)
	python cmdQueue.py setup
	
* Kill jobs
	python cmdQueue.py killjob -p PID
	python cmdQueue.py killjob2 -i JOBID
	
* Kill workers
	python cmdQueue.py killworker -p PID

Start a different queue
-----------------------
Please use a differnt database file to start a different queue

* Temporary way:
	python cmdQueue.py --config db=./another.db SUBCOMMAND ...
	
* Using configuration file:
	python cmdQueue.py --config ./another.config SUBCOMMAND ...
	
* Configuration file:
	[cmdQueue]
	db=cmdQueue.db  
	; the database file    
	workercount=5
	; how many workers to run at the same time
	interval=60
	; how frequently to check new jobs if all jobs done
	logfile=cmdQueue.log
	; the log file
	loglevel=INFO
	; the log level


Plugins
-------------
plugins are put in the folder "plugins", and named like 'cqp-<PLUGINNAME>[-<PRIORITY>].py'
Less number PRIORITY is, the higher priority the plugin has (executed before other plugins). 

Check the sample plugin in the folder.


