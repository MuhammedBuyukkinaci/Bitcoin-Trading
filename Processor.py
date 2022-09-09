from datetime import datetime, timedelta
from pandas import DataFrame
from numpy import array
from tqdm import tqdm
from tensorflow.keras.models import load_model
from Connector import Connector


class Processor:
    connector: Connector
    model_path: str
    
    def __init__(self, connector, model_path):
        self.time_step = connector.time_step
        self.input_table = connector.input_table
        self.cursor = connector.cursor
        self.next_period = connector.next_period
        self.positive_ratio = connector.positive_ratio
        self.n_features = connector.n_features
        self.model_path = model_path
        # Default attributes
        self.data_columns = ['btc_usdt', 'eth_usdt', 'eth_btc', 'date_inserted']
        self.hours_used = [0, 4, 8, 12, 16, 20]
        # Setting date attributes
        self.current_dt = datetime.now()
        self.seconds_before = (self.time_step + 1)*4*3600
        self.limit_dt = self.current_dt - timedelta(seconds=self.seconds_before)
        # LSTM Input
        self.data = None
        self.arr = None
        self.train_data = None
        self.reshaped_data = None
        self.final_input = None
        self.model = None
        self.prediction = None
        self.to_trade = None

    def read_data_from_db(self) -> None:
        self.cursor.execute(
            f"SELECT * from {self.input_table} WHERE date_inserted > (current_timestamp - make_interval(secs := %s))",
            [self.seconds_before])
        self.data = self.cursor.fetchall()
        self.data = DataFrame(self.data)
        self.data.columns = self.data_columns

    def filter_data(self) -> None:
        self.data['hour_info'] = self.data['date_inserted'].dt.hour
        self.data = self.data[(self.data['hour_info'].isin(self.hours_used)) & (self.data['date_inserted'].dt.minute == 0)].reset_index(drop=True)

    def compute_binary(self, base_value, next_value) -> None:
        lower_threshold = base_value * (1 - self.positive_ratio * 0.01)
        upper_threshold = base_value * (1 + self.positive_ratio * 0.01)
        if (next_value < lower_threshold) | (next_value > upper_threshold):
            self.train_data.append(1)
        else:
            self.train_data.append(0)

    def create_train_data(self) -> None:
        self.arr = array(self.data['btc_usdt'])
        self.train_data = []
        for element in tqdm(range(len(self.arr) - self.next_period)):
            base_value = self.arr[element]
            next_value = self.arr[element + 1]
            self.compute_binary(base_value=base_value,next_value=next_value)

    def convert_to_pandas_df(self) -> None:
        self.reshaped_data = DataFrame(self.train_data).T
        self.reshaped_data.columns = [f'T{i}' for i in range(1, self.time_step + 1, 1)]

    def expand_dims(self) -> None:
        self.final_input = self.reshaped_data.values.reshape(( self.reshaped_data.shape[0], self.reshaped_data.shape[1], self.n_features))

    def get_final_input(self) -> DataFrame:
        return self.final_input

    def load_model(self):
        self.model = load_model(self.model_path)

    def get_prediction(self, trade_threshold):
        self.prediction = float(self.model.predict(self.final_input)[0][0])
        self.to_trade = int((self.prediction > trade_threshold) * 1)

