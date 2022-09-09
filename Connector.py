import psycopg2
from dotenv import load_dotenv
import os


class Connector:
    def __init__(self):
        load_dotenv()
        # db parameters
        self.database_username = os.getenv('DATABASE_USERNAME')
        self.database_password = os.getenv('DATABASE_PASSWORD')
        self.database_host = os.getenv('DATABASE_HOST')
        self.database_port = os.getenv('DATABASE_PORT')
        self.database_name = os.getenv('DATABASE_NAME')
        # model parameters
        self.time_step = int(os.getenv('time_step'))
        self.next_period = int(os.getenv('next_period'))
        self.n_features = int(os.getenv('n_features'))
        self.positive_ratio = float(os.getenv('positive_ratio'))
        # Email parameters
        self.sender_email = os.getenv('sender_email')
        self.sender_password = os.getenv('sender_password')
        self.receiver_email = os.getenv('receiver_email')
        # Table parameters
        self.input_table = os.getenv('input_table')
        self.trade_table = os.getenv('trade_table')
        self.trade_threshold = float(os.getenv('TRADE_THRESHOLD'))
        # Connection and Cursor
        self.connection = psycopg2.connect(user=self.database_username,
                                           password=self.database_password,
                                           host=self.database_host,
                                           port=self.database_port,
                                           database=self.database_name)
        self.cursor = self.connection.cursor()
