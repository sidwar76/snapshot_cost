from glob import glob1
from http import client
import boto3
# import csv
import datetime
import operator
import datetime as dt
import mysql.connector
import colorama
from colorama import Fore
from datetime import datetime, timedelta, timezone
# from csv import DictWriter



'''
Taking all the volumes in a list 
'''
AWS_REGION = "us-east-2"
ec2 = boto3.resource('ec2',
                     aws_access_key_id='',
                     aws_secret_access_key = '',
                     region_name=AWS_REGION)
volumes = ec2.volumes.all()
volume_ids = [v.id for v in volumes]

""" 
Iterating over volumes list to extract the snapshot details using boto3 client
"""
for j in volume_ids:
    EC2_RESOURCE = boto3.client('ec2', 
                                aws_access_key_id='',
                                aws_secret_access_key = '',    
                                region_name=AWS_REGION)
    snapshots = EC2_RESOURCE.describe_snapshots(
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [
                    j
                ]
            }
        ]
    )
    snapshot_info={}
    
    """
    storing snapshotid as key and its AGE as a value in a dictionary
    """
    # print(snapshots)
    for i in snapshots['Snapshots']:
        age= datetime.now(timezone.utc) - i['StartTime']

        snapshot_info[i['SnapshotId']] = age.total_seconds()
        # age= datetime.now(timezone.utc) - i['StartTime']
        #print(age.total_seconds())
    sorted_d = dict( sorted(snapshot_info.items(), key=operator.itemgetter(1),reverse=True))
    # print('Dictionary in descending order by value : ',sorted_d)
    #print(snapshot_info)

    if snapshot_info=={}:
        continue
    print( Fore.GREEN + "Below are the snapshots of VOLUME_ID "+j)
    print(end='\n')
    # print(snapshot_info)


    """
    Printing the size of first snapshot
    """

    keysList = list(sorted_d.keys())
    client = boto3.client('ebs',
                            aws_access_key_id='',
                            aws_secret_access_key = '',
                            region_name=AWS_REGION)
    keysList[0]
    response1 = client.list_snapshot_blocks(SnapshotId=keysList[0])
    block_l = response1["Blocks"]

    while "NextToken" in response1:
            response1 = client.list_snapshot_blocks(SnapshotId=keysList[0], NextToken=response1["NextToken"])
            block_l.extend(response1["Blocks"])
    # print(len(block_l))
    f = len(block_l)*524288         
    GB1 =  f / (1024 * 1024 * 1024)
    print(Fore.BLUE+"size of first snapshot " +Fore.YELLOW+keysList[0]+" is "+ Fore.RED+str(GB1) +" GBs")
    print(end='\n')


    """
    Printing the changed in clearsize of rest of the snapshot
    """

    for k in range(len(keysList)-1):

        client = boto3.client('ebs',
                            aws_access_key_id='',
                            aws_secret_access_key = '',
                            region_name=AWS_REGION)
        response = client.list_changed_blocks(FirstSnapshotId=keysList[k],SecondSnapshotId=keysList[k+1])
        block_list = response["ChangedBlocks"]

        while "NextToken" in response:
            response = client.list_changed_blocks(FirstSnapshotId=keysList[k],SecondSnapshotId=keysList[k+1],NextToken=response["NextToken"])
            block_list.extend(response["ChangedBlocks"])
        g = len(block_list)*524288
        GB =  g / (1024 * 1024 * 1024)
        print(Fore.BLUE+"Change in size from "+Fore.YELLOW+keysList[k]+" to "+ keysList[k+1]+" is "+Fore.RED+ str(GB)+ " GBs")
        print(end='\n')
