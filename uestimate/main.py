import preprocessPermitData as prep
import forecast
import pandas as pd
from datetime import datetime, timedelta


OCCUPANCY_GROUPS = ['01 - Single Family', '02 - Two Family', '03 - Apartment', '04 - Hotel']

QUARTER_BEGINNINGS = pd.date_range(start=datetime(2008, 1, 1), periods=43, freq='3MS').date

QUARTERS = [pd.date_range(start=QUARTER_BEGINNINGS[i], end=QUARTER_BEGINNINGS[i+1] - timedelta(days=1), freq='D').to_pydatetime() for i in range(42)]

PREDICTION_QUARTER_BOUNDARIES = [(datetime(2018, 4, 1), datetime(2018, 7, 1)),
                                 (datetime(2018, 7, 1), datetime(2018, 10, 1)),
                                 (datetime(2018, 10, 1), datetime(2019, 1, 1))]

df = prep.read_permits('300kPermits.csv')

for occupancy in OCCUPANCY_GROUPS:
    predictor = forecast.Forecast(df, occupancy_group=occupancy)
    current_data = pd.DataFrame(data={'numberPending': predictor.get_quarterly_pending(quarters=QUARTERS),
                              'valuePending': predictor.get_quarterly_pending_value(quarters=QUARTERS), 'waitTime': predictor.get_wait_time()})
    current_data.to_csv(occupancy + ' from ' + datetime.now().strftime('%d-%m-%y'))
    current_values = pd.DataFrame({'currentPending': [predictor.get_current_pending()], 'currentPendingValue': [predictor.get_pending_value()]})
    current_values.to_csv(occupancy + ' currentNumbers' + datetime.now().strftime('%d-%m-%y'))
    predicted_numbers = [
        predictor.predict_number(PREDICTION_QUARTER_BOUNDARIES[i][0], PREDICTION_QUARTER_BOUNDARIES[i][1]) for i in range(3)]
    predicted_values = [
        predictor.predict_value(PREDICTION_QUARTER_BOUNDARIES[i][0], PREDICTION_QUARTER_BOUNDARIES[i][1]) for i in range(3)]
    prediction = pd.DataFrame({'predictedNumbers': predicted_numbers, 'predictedValues': predicted_values})
    prediction.to_csv(occupancy + ' predictions ' + datetime.now().strftime('%d-%m-%y'))