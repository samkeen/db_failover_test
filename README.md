

## Setup
```
# Pyython 3.x required
$ python -m venv venv
$ ./venv/bin/activate
$ pip install -r requirements.txt
```

## Usage

### failover_timer.py

This script will start executing a 'heartbeat' query to the given MySQL database, roughly once every second.
When there is a connection disruption, it will continue to try connections every sec.
When connectivity returns, it will stop and report the total time the db was not accessible.
This can be used measure the amount of time required for Failover in Db clusters with such capability

**Workflow:**
1. Execute this script
2. Take the action on you Db to initiate fail over workflow.

```
# ./failover_timer.py --help

$ ./failover_timer.py
RDS Endpoint: [localhost]

# answer a seriers of user prompts, then test will start
```



**Notes:**

SSL connections to MySql is supported.  Simple answer `y` when prompted then supply the path the the cert file.
For instance if you are connection to AWS RDS.
```
$ wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem
$ ./failover_timer.py
# provide ./rds-combined-ca-bundle.pem for the SSL cert path
```

# setting up python on amazon linux2
```
$ sudo yum install -y python3-pip python3 python3-setuptools -y

$ python3 --version
Python 3.7.4

$ sudo pip3 install PyMySQL
```