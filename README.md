# Setup
```
# Python 3.x required
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

# Usage

## failover_timer.py

This script will start executing a 'heartbeat' query to the given MySQL database, roughly once every second.
When there is a connection disruption, it will continue to try connections every sec.
When connectivity returns, it will stop and report the total time the db was not accessible.
This can be used measure the amount of time required for Failover in Db clusters with such capability

### Workflow
1. Execute this script
2. Take the action on you Db to initiate fail over workflow.

```
# ./failover_timer.py --help

$ ./failover_timer.py
RDS Endpoint: [localhost]

# answer a seriers of user prompts, then test will start
```

### Notes

#### SSL connections
SSL connections to MySql is supported.  Simple answer `y` when prompted then supply the path the the cert file.
For instance if you are connection to AWS RDS.
```
$ wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem
$ ./failover_timer.py
# provide ./rds-combined-ca-bundle.pem for the SSL cert path
```

#### Setting up on amazon linux2
```
$ sudo yum install -y python3-pip python3 python3-setuptools git -y

$ python3 --version
Python 3.7.4

$ git clone https://github.com/samkeen/db_test_meter.git

$ cd db_test_meter
```
Now simply follow ***Setup*** instructions above

## failover_sync.py

This script simply inserts *hearbeat* records into a database until the connection fails.

<<<<TODO>>>>>
It then continues to check the connection until it comes back (db failover finishes)
At that point it checks that the last record inserted to the previous primary exists in this new primary.

### Usage

```
# run create_failover_sync_db.py if needed (see notes below)
./failover_sync.py --test_run_id=bob2
```
`test_run_id` is a unique identifier use to segregate differing test runs in the  `db_sync` db table

### Notes
`create_failover_sync_db.py` is run to create the db and table to support `failover_sync.py`.
Each time this is run it drops the DB and recreates.