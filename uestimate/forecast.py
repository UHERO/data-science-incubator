import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta

WAITSTATUSES = ['Permit approved to issue',

 'Inspection(s) in Progress', 'Erroneous process(es) corrected',

 'Plans review in progress', 'Working', 'Start',

 'Printed Building Permit Application',

 'Agency routing determined',

 'Model review only - no BP issued', 'Routing determined', 'Fees paid',

 'Automatic approval route determined', 'One Time review process',

 'BPA reviewed at counter', 'Called for pick-up']


QUARTER_BEGINNINGS = pd.date_range(start=datetime(2008, 1, 1), periods=43, freq='3MS').date


QUARTERS = [pd.date_range(start=QUARTER_BEGINNINGS[i], end=QUARTER_BEGINNINGS[i+1] - timedelta(days=1), freq='D').date for i in range(42)]

class Forecast(object):

    def __init__(
            self,
            dataframe,
            occupancyGroup,
            lowerValueLimit = 30000,
            ):

        self.data = dataframe[dataframe['permit.occupancyGroup'] == occupancyGroup]
        self.data = self.data[self.data['permit.estimatedValue'] > lowerValueLimit]
        self.data = self.data[self.data['permit.createdDate'] > datetime.now() - timedelta(days=365 * historyLen)]
        self.data['quarter'] = self.data.apply(lambda row: str(row['permit.createdDate'].year) + str(row['permit.createdDate'].quarter), axis=1)


    def getCurrentPending(self):
        return len(self.data[self.data['permit.status'] in WAITSTATUSES])

    def getPendingValue(self):
        return sum(self.data[self.data['permit.status'] in WAITSTATUSES]['permit.estimatedValue'])

    def getDailyPending(self, day):
        return len(self.data[(self.data['permit.createdDate'] < day)
                             & (self.data['permit.issuedDate'] > day)])

    def getDailyPendingValue(self, day):
        return sum(self.data[(self.data['permit.createdDate'] < day)
                             & (self.data['permit.issuedDate'] > day)]['permit.estimatedValue'])

    def getQuarterPending(self, quarter):
        return sum([self.getDailyPending(day) for day in quarter]) / float(len(quarter))

    def getQuarterPendingValue(self, quarter):
        return sum([self.getDailyPendingValue(day) for day in quarter]) / float(len(quarter))

    def getQPendings(self):
        return [self.getQuarterPending(quarter) for quarter in self.quarters]

    def getVPendings(self):
        return [self.getQuarterPendingValue(quarter) for quarter in QUARTERS]

    def getWaittime(self):
        self.data.groupby(['quarter'])