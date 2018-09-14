import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

WAITSTATUSES = ['Permit approved to issue',

 'Inspection(s) in Progress', 'Erroneous process(es) corrected',

 'Plans review in progress', 'Working', 'Start',

 'Printed Building Permit Application',

 'Agency routing determined',

 'Model review only - no BP issued', 'Routing determined', 'Fees paid',

 'Automatic approval route determined', 'One Time review process',

 'BPA reviewed at counter', 'Called for pick-up']


QUARTER_BEGINNINGS = pd.date_range(start=datetime(2008, 1, 1), periods=43, freq='3MS').date


QUARTERS = [pd.date_range(start=QUARTER_BEGINNINGS[i], end=QUARTER_BEGINNINGS[i+1] - timedelta(days=1), freq='D').to_pydatetime() for i in range(42)]


class Forecast(object):

    def __init__(
            self,
            dataframe,
            occupancy_group,
            regression_algorithm=None,
            lower_value_limit=3000,
            start_date=datetime(2008, 1, 1)
    ):

        self.data = dataframe[dataframe['permit.occupancyGroup'] == occupancy_group]
        self.data = self.data[self.data['permit.estimatedValue'] > lower_value_limit]
        self.data = self.data[(self.data['permit.createdDate'] >= start_date) | (self.data['permit.issuedDate'] >= start_date)]
        self.data['quarter'] = self.data.apply(lambda row: str(row['permit.createdDate'].year) + str(row['permit.createdDate'].quarter), axis=1)
        self.predictor = regression_algorithm()

    def get_current_pending(self):
        return sum(self.data['permit.status'].isin(WAITSTATUSES))

    def get_pending_value(self):
        return sum(self.data[self.data['permit.status'].isin(WAITSTATUSES)]['permit.estimatedValue'])

    def _get_daily_pending(self, day):
        return len(self.data[((self.data['permit.createdDate'] <= day) & (self.data['permit.issuedDate'] >= day))
                                # | ((self.data['permit.createdDate'] <= day) & (self.data['permit.status'].isin(WAITSTATUSES)))
                            ])

    def _get_daily_pending_value(self, day):
        return sum(self.data[
                       ((self.data['permit.createdDate'] <= day) & (self.data['permit.issuedDate'] >= day))
                         # | ((self.data['permit.createdDate'] <= day) & (self.data['permit.status'].isin(WAITSTATUSES)))
                            ]['permit.estimatedValue'])

    def _get_quarter_pending(self, quarter):
        return sum([self._get_daily_pending(day) for day in quarter]) / float(len(quarter))

    def _get_quarter_pending_value(self, quarter):
        return sum([self._get_daily_pending_value(day) for day in quarter]) / float(len(quarter))

    def get_quarterly_pending(self, quarters):
        return pd.Series([self._get_quarter_pending(quarter) for quarter in quarters])

    def get_quarterly_pending_value(self, quarters):
        return pd.Series([self._get_quarter_pending_value(quarter) for quarter in quarters])

    def get_quarterly_wait_time(self):
        return self.data.groupby(['quarter'])['waitTime'].mean().values

    def get_wait_time(self):
        return self.data['waitTime'].mean()

    def train_predictor(self):
        self.predictor.fit(X=np.array(self.data[self.data['permit.issuedDate'].notnull()]['permit.estimatedValue']).reshape(-1, 1),
                           y=np.array(self.data[self.data['permit.issuedDate'].notnull()]['waitTime']))

    def expected_date_fill(self, row):
        return row['permit.issuedDate'] if row['permit.issuedDate'] == row['permit.issuedDate'] else \
            row['permit.createdDate'] + timedelta(days=self.predictor.predict(row['permit.estimatedValue'])[0])

    def _forecast_approval_dates(self):
        self.train_predictor()
        self.data['expectedIssuedDate'] = self.data.apply(self.expected_date_fill, axis=1)

    def predict_number(self, start, end):
        self._forecast_approval_dates()
        return len(self.data[(self.data['permit.status'].isin(WAITSTATUSES))
                             & (self.data['expectedIssuedDate'] >= start)
                             & (self.data['expectedIssuedDate'] <= end)])

    def predict_value(self, start, end):
        self._forecast_approval_dates()
        return sum(self.data[(self.data['permit.status'].isin(WAITSTATUSES))
                             & (self.data['expectedIssuedDate'] >= start)
                             & (self.data['expectedIssuedDate'] <= end)]['permit.estimatedValue'])

if __name__ == '__main__':
    import preprocessPermitData as prep

    df = prep.read_permits('currentPermits.csv')
    test = Forecast(df, occupancy_group='03 - Apartment', regression_algorithm=RandomForestRegressor)
    test._forecast_approval_dates()
    test.data

