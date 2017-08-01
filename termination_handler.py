# AWS Spot Instance
# Termination Notices Handler
#
# Copyright (c) Alexey Baikov <sysboss[@]mail.ru>

import os
import boto3
import requests
from time import sleep
from datetime import datetime
from elasticsearch import Elasticsearch

# Required environment variables
spotfleet = os.getenv('SPOTFLEET_NAME', None)
ec_index  = os.getenv('EC_INDEX_NAME', 'spotfleet_events')
es_host   = os.getenv('ES_HOST', 'elk.fqdn.com')
es_port   = os.getenv('ES_PORT', 9200)

# Basic settings
send_retries  = 3
poll_interval = 6
poll_loops    = 9

def get_spotfleet_id(fid):
    ec2 = boto3.resource('ec2', region_name=ec2_region)
    ec2instance = ec2.Instance(fid)
    spotfleet_id = ''

    for tags in ec2instance.tags:
        if tags["Key"] == 'aws:ec2spot:fleet-request-id':
            spotfleet_id = tags["Value"]
    return spotfleet_id

def notify_elastic(retries):
    es  = Elasticsearch([{'host': es_host, 'port': es_port}])
    doc = {
        'event'        : 'Termination',
        'instance_id'  : instance_id,
        'instance_type': instance_type,
        'spotfleet'    : spotfleet,
        'spotfleet_id' : spotfleet_id,
        '@timestamp'   : datetime.now()
    }

    while retries > 0:
        res = es.index(index=ec_index, doc_type='notices', body=doc)

        if res['created']:
            retries = 0
            print('Sent to Elasticsearch')
        else:
            print('RETRY')
            retries -= 1

# gather information
ec2_identity  = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document').json()
ec2_is_marked = requests.get('http://169.254.169.254/latest/meta-data/spot/termination-time')
instance_id   = ec2_identity['instanceId']
instance_type = ec2_identity['instanceType']
ec2_region    = ec2_identity['region']
spotfleet_id  = get_spotfleet_id(instance_id)

# Check if instance is marked for termination
while poll_loops > 0:
    if ec2_is_marked.status_code == 404:
        # Spot instance not yet marked for termination
        sleep(poll_interval)

        # check again
        ec2_is_marked = requests.get('http://169.254.169.254/latest/meta-data/spot/termination-time')
        poll_loops -= 1
    else:
        notify_elastic(retries)

        sleep(300)
        poll_loops = 0
