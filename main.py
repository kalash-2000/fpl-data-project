""" 
Python module to upload data to S3 bucket 

Created by 
Author 1: Kalash Gandhi <kalashgandhi.kg10@gmail.com>
Author 2: Anoushka Rao <anoushka410@gmail.com>
"""
##### Imports
from data_ingestion import create_master_data
import boto3
from tqdm.auto import tqdm
import pandas as pd

###### Constants
S3 = boto3.client('s3')

# check how muck time create_master_data() takes to run
tqdm.pandas()

# create_master_data will return a df. convert it to csv and upload to s3
create_master_data().to_csv('master_data.csv')

# upload file to s3
S3.upload_file('master_data.csv', 'fpl-data-project', 'master_data.csv')

# S3.download_file('fpl-data-project','master_data.csv','master_data_123.csv')
