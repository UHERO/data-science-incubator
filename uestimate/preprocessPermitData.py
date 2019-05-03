import pandas as pd
import numpy as np
from datetime import datetime

NUMERIC_FEATURES = ['permit.acceptedValue',
                    'permit.estimatedValue',
                    'permit.existingFloorArea',
                    'permit.newFloorArea',
                    'permit.totalFloorArea']

DATES = ['permit.createdDate',
         'permit.dateConstructionCompleted',
         'permit.issuedDate',
         'permit.jobCompletedDate']

DUMMIES = ['permit.buildingInspectionRequired',
           'permit.certifOfOccupancyNeeded',
           'permit.cityProject',
           'permit.commercialOrResidential',
           'permit.curbingTypes',
           'permit.developmentPlanAreas',
           'permit.drivewayExisting',
           'permit.drivewayNew',
           'permit.drivewayPrivate',
           'permit.drivewayRepair',
           'permit.drivewayTypes',
           'permit.electricalInspectionRequired',
           'permit.floodHazardComplied',
           'permit.floodHazardDistrict',
           'permit.floodZones',
           'permit.heightLimit',
           'permit.locationPermitCreated',
           'permit.occupancyCommercial',
           'permit.occupancyGroupCategory',
           'permit.ownership',
           'permit.proposedUse',
           'permit.stateLandUse',
           'permit.workAC',
           'permit.workADU',
           'permit.workAddition',
           'permit.workAlteration',
           'permit.workAntenna',
           'permit.workDemolition',
           'permit.workEVCharger',
           'permit.workElectrical',
           'permit.workElectricalMeter',
           'permit.workFence',
           'permit.workFireAlarm',
           'permit.workFireSprinkler',
           'permit.workFoundationOnly',
           'permit.workHeatPump',
           'permit.workNewBuilding',
           'permit.workOhana',
           'permit.workPVInstallWBattery',
           'permit.workPlumbing',
           'permit.workPool',
           'permit.workRelocationFrom',
           'permit.workRelocationTo',
           'permit.workRepair',
           'permit.workRetainingWall',
           'permit.workShellOnly',
           'permit.workSolar',
           'permit.workSolarPVInstall',
           'permit.workTemporary',
           'permit.zoning']

NANS = []


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

def str_preprocess(s):
  if type(s) != str:
    return s

  chars = ['\\', '`', '*', '_', '{',
           '}', '[', ']', '(', ')',
           '>', '#', '+', '-', ' ',
           '.', '!', '$', '\'', ',',
           '&', ';', ':', '/']

  for c in chars:
    s = s.replace(c, '')

  return s

def dummify(df):
    for dummy in DUMMIES:
        df[dummy] = df[dummy].apply(str_preprocess)
        df = pd.concat([df, pd.get_dummies(df[dummy], prefix=dummy, prefix_sep='', dummy_na=True, drop_first=True)], axis=1)
        df.drop(dummy, axis=1, inplace=True)
    return df


def process_nans(df):
    for nan in NANS:
        df[nan + 'isna'] = pd.isna(df[nan])
        df[nan + 'isna'] = df[nan + 'isna'].apply(lambda x: 1 if x else -1)
    df.fillna(0, inplace=True)
    return df




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

    df = dummify(df)

    df = process_nans(df)

    return df


if __name__ == '__main__':

    df = read_permits('currentPermits.csv')
    print(df.shape)