cmdQueue
========

A job queue implemented in Python


Usage
-----

#### Add a job:
```bash
usage: cqsub [-h] [--config CONFIG] [--noworker] [-n NAME] [-p PRI] [-c CMD]
             [cqfile]

Submit a job to cmdQueue.

positional arguments:
  cqfile                The cmdQueue job file.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       The configuration file.
  --noworker            Don't try to start the worker.
  -n NAME, --name NAME  The name of the job.
  -p PRI, --pri PRI     The priority of the job.
  -c CMD, --cmd CMD     The command of the job
```

#### List jobs:

```bash
cqstat 

  ID    NAME     STATUS   PRI                 CMD     PID   RC             STARTTIME            SUBMITTIME          COMPLETETIME 
----+-------+----------+-----+-------------------+-------+----+---------------------+---------------------+---------------------
   1   Job-1   COMPLETE     0   bash -c "sleep 3"   66448    0   2017-08-29 14:44:46   2017-08-29 14:44:41   2017-08-29 14:44:49
   2   Job-2   COMPLETE     0   bash -c "sleep 3"   66554    0   2017-08-29 14:45:36   2017-08-29 14:45:31   2017-08-29 14:45:39
   3   Job-3   COMPLETE     0   bash -c "sleep 3"   66594    0   2017-08-29 14:46:06   2017-08-29 14:45:56   2017-08-29 14:46:09
   4   Job-4   COMPLETE     0   bash -c "sleep 3"   66783    0   2017-08-29 14:46:46   2017-08-29 14:46:37   2017-08-29 14:46:49
   5   Job-5   COMPLETE     0   bash -c "sleep 3"   66814    0   2017-08-29 14:47:26   2017-08-29 14:47:17   2017-08-29 14:47:29
   6   Job-6   COMPLETE     0            sleep 10   15282    0   2017-08-29 16:08:24   2017-08-29 16:08:19   2017-08-29 16:08:34

Jobs: COMPLETE: 6
Worker is not running.
Number of subworkers: 10.
Jobs are pulled every 10 seconds.

```

#### Start the queue:
```bash
cqctl start
```
	
#### Stop the queue:
```bash
cqctl stop
```
	
#### Restart the queue:
```bash
cqctl restart
```

#### Reset the queue (remove all workers and jobs)
```bash
cqctl reset
```

Start a different queue
-----------------------

#### Using configuration file:
```bash
cqctl --config <anotherConfigFile> start
```
	
#### Configuration file:
```ini

[general]
nworkers  = 10 
interval = 10
database = sqlite
workerlock = ~/.cmdQueue/cmdQueue.worker.lock
plugins = sample

[log] 
file = ~/.cmdQueue/cmdQueue.log
level = info

[dbconfig]
file = ~/.cmdQueue/cmdQueue.db
lock = ~/.cmdQueue/cmdQueue.db.lock
```


Plugins
-------------
To enable a built-in plugin in `cmdQueue/plugins`, just put the name in config file under:
```
[general]
plugins:
  plugin1
  plugin2
```

To develop a plugin, write a class extends `cmdQueue.plugin.Plugin`.
In the config file, specify the directory of the plugin file:
```
[general]
plugins:
	myplugin
	
[mypluginPlugin]
dir: /path/to/myplugin
```
There should be a `myplugin.py` under `/path/to/myplugin`
The class name should be `mypluginPlugin`

The `priority` argument determines the order of multiple plugins. Smaller number means higher priority.