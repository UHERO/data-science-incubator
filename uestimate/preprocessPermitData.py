import pandas as pd
import numpy as np
from datetime import datetime, date

NUMERIC_FEATURES = ['permit.acceptedValue',
                    'permit.estimatedValue',
                    'permit.existingFloorArea',
                    'permit.newFloorArea',
                    'permit.totalFloorArea']

DATES = ['permit.createdDate',
         'permit.dateConstructionCompleted',
         'permit.issuedDate',
         'permit.jobCompletedDate']


def str_to_float(s):
    if type(s) == float or type(s) == int:
        return s
    return float(s.replace('$', '').replace(',', ''))


def parse_date(s):
    if s == 'mmm dd, yyyy' or s == 'nan':
        return np.nan
    return datetime.strptime(s, '%b %d, %Y')


def wait_time(row):
    if row['permit.createdDate'] != row['permit.createdDate'] or row['permit.issuedDate'] != row['permit.issuedDate']:
        return np.nan
    return (row['permit.issuedDate'] - row['permit.createdDate']).days


def dataprep(row):
    for feature in NUMERIC_FEATURES:
        row[feature] = str_to_float(row[feature])

    for date in DATES:
        row[date] = parse_date(str(row[date]))

    return row


def read_permits(filename):
    df = pd.read_csv(filename)

    df = df.apply(dataprep, axis=1)

    df['waitTime'] = df.apply(lambda row: wait_time(row), axis=1)

    return df
