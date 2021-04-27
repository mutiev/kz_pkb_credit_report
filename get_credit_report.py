# %%
import pandas as pd
import requests
import json
from zipfile import ZipFile
import shutil
from tqdm import tqdm
import os
import click
import xmltodict

requests.packages.urllib3.disable_warnings()

with open('iin_list.txt') as f:
    iin_list = f.read().splitlines()
os.makedirs('tmp/', exist_ok=True)
os.makedirs('download/', exist_ok=True)

HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

env_name = click.prompt(
    'Enter environment name (test,production):', type=str, default='test')


if os.path.exists('credentials.json'):
    credentials = json.load(open('credentials.json'))
    url = credentials[env_name]['url']
    username = credentials[env_name]['username']
    password = credentials[env_name]['password']
else:
    raise FileNotFoundError('credentials.json is missing')

# %%
params = {
    "username": username,
    "password": password,
    "doc1_type": 14,
    "doc1_number": "{iin}",
    "report_type": 6,
    "consent_confirmed": 1
}

for iin in tqdm(iin_list):
    params['doc1_number'] = iin
    if os.path.exists(f'download/{iin}.zip'):
        print(f'{iin} already downloaded. skipped')
        continue

    resp = requests.post(url, data=json.dumps(
        params), headers=HEADERS, verify=False)

    if resp.status_code != 200:
        print('\nError: status code is', resp.status_code)
        break

    with open('tmp/request.zip', 'wb') as f:
        f.write(resp.content)

    with ZipFile('tmp/request.zip') as myzip:
        with myzip.open('status.xml') as xmlfile:
            status = xmlfile.read()

    status = xmltodict.parse(status)

    if status['Status']['Error'] == 'True':
        print('\n\tIIN ', iin)
        print('\tErrorCode:', status['Status']['ErrorCode'])
        print('\tErrorMessage', status['Status']['ErrorMessage'])
        continue

    shutil.move('tmp/request.zip', f'download/{iin}.zip')

print('Done.')


# %%
