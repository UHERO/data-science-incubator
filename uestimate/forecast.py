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


class Forecast(object):

    def __init__(
            self,
            dataframe,
            occupancyGroup,
            lowerValueLimit = 30000,
            historyLen = 10
            ):

        self.data = dataframe[dataframe['permit.occupancyGroup'] == occupancyGroup]
        self.data = self.data[self.data['permit.estimatedValue'] > lowerValueLimit]
        self.data = self.data[self.data['permit.createdDate'] > datetime.now() - timedelta(days=365 * historyLen)]
        self.data['quarter'] = self.data.apply(lambda row: row['permit.createdDate'].quarter, axis=1)

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

