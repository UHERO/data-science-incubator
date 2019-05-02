import preprocessPermitData as prep
import forecast
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from datetime import datetime, timedelta


OCCUPANCY_GROUPS = [('01 - Single Family', 2000),
                    ('02 - Two Family', 2000),
                    ('03 - Apartment', 20000),
                    ('04 - Hotel', 20000)]

QUARTER_BEGINNINGS = pd.date_range(start=datetime(2008, 1, 1), periods=44, freq='3MS').date

QUARTERS = [pd.date_range(start=QUARTER_BEGINNINGS[i], end=QUARTER_BEGINNINGS[i+1] - timedelta(days=1), freq='D').to_pydatetime() for i in range(43)]

PREDICTION_QUARTER_BOUNDARIES = [(datetime(2018, 7, 1), datetime(2018, 10, 1)),
                                 (datetime(2018, 10, 1), datetime(2019, 1, 1)),
                                 (datetime(2019, 1, 1), datetime(2019, 4, 1)),
                                 (datetime(2019, 4, 1), datetime(2019, 7, 1)),
                                 (datetime(2019, 7, 1), datetime(2019, 10, 1)),
                                 (datetime(2019, 10, 1), datetime(2020, 1, 1)),
                                 (datetime(2020, 1, 1), datetime(2020, 4, 1))]

df = prep.read_permits('currentPermits.csv')

writer = pd.ExcelWriter(datetime.now().strftime('%d %m %y') + 'forecast.xls', datetime_format='mmm d yyyy')
for occupancy in OCCUPANCY_GROUPS:
    predictor = forecast.Forecast(df, occupancy_group=occupancy[0], lower_value_limit=occupancy[1], regression_algorithm=RandomForestRegressor)
    current_data = pd.DataFrame(data={'numberPending': predictor.get_quarterly_pending(quarters=QUARTERS),
                                      'valuePending': predictor.get_quarterly_pending_value(quarters=QUARTERS),
                                      'waitTime': predictor.get_wait_time(),
                                      'quarter': QUARTER_BEGINNINGS[:-1]})
    current_data.to_excel(writer, sheet_name=occupancy[0][:2] + ' timeseries at ' + datetime.now().strftime('%d %m %y'))
    current_values = pd.DataFrame({'currentPending': [predictor.get_current_pending()],
                                   'currentPendingValue': [predictor.get_pending_value()]})
    current_values.to_excel(writer, sheet_name=occupancy[0][:2] + ' current numbers at ' + datetime.now().strftime('%d %m %y'))
    predicted_numbers = [
        predictor.predict_number(PREDICTION_QUARTER_BOUNDARIES[i][0], PREDICTION_QUARTER_BOUNDARIES[i][1]) for i in range(len(PREDICTION_QUARTER_BOUNDARIES))]
    predicted_values = [
        predictor.predict_value(PREDICTION_QUARTER_BOUNDARIES[i][0], PREDICTION_QUARTER_BOUNDARIES[i][1]) for i in range(len(PREDICTION_QUARTER_BOUNDARIES))]
    prediction = pd.DataFrame({'quarter': PREDICTION_QUARTER_BOUNDARIES, 'predictedNumbers': predicted_numbers, 'predictedValues': predicted_values})
    prediction.to_excel(writer, sheet_name=occupancy[0][:2] + ' predictions at ' + datetime.now().strftime('%d %m %y'))

writer.save()
