# Handling AWS Spot Instance Termination Notices

EC2 spot instance is getting "two-minute warning" termination notice before it's being terminated.
This Python script sends this events to ElasticSearch.

Might be useful in some use-cases.

## Requirements and Installation
Python 2.7 runtime is required:
```
apt-get update
apt-get install -y python python-pip
```

Use python-pip to install all the dependencies:
`pip install -r requirements.txt`

## Usage
Can be added to EC2 machine user-data script
```
export SPOTFLEET_NAME=""
export ES_INDEX_NAME=""
export ES_HOST=""
export ES_PORT=""
```
