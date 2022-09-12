from yagmail import SMTP
from numpy import round as rounder
import Processor
import Connector
from datetime import timedelta
from pandas import DataFrame


class ExportResult:
    processor: Processor
    connector: Connector

    def __init__(self, processor, connector, trade_table):
        self.processor = processor
        self.connector = connector
        self.trade_table = trade_table
        self.postgres_insert_query = f""" 
                INSERT INTO public.{self.trade_table} (prediction, to_trade, date_inserted) VALUES (%s,%s,CURRENT_TIMESTAMP)
                """
        # Setting variables to None
        self.recording_data = None
        self.mail_html = None
        
    def send_email(self) -> None:
        if self.processor.to_trade == 1:
            subject_of_mail = f"{self.processor.current_dt} tarihli Trade"
            yag = SMTP(self.connector.sender_email, self.connector.sender_password)
            contents = ['Merhaba Muhammed, Ben Trading Bot. BTC/USDT paritesinde Trade sinyali elde ettim',
                        f'{rounder(self.processor.prediction, 4)} ihtimalli bir trade. Bilgin olsun.']
            yag.send(self.connector.receiver_email, subject_of_mail, contents)

    def insert_record_to_db(self) -> None:
        # Inserting
        record_to_insert = (self.processor.prediction, self.processor.to_trade)
        self.connector.cursor.execute(self.postgres_insert_query, record_to_insert)
        # Committing
        self.connector.connection.commit()

    def read_data_from_db(self) -> None:
        self.connector.cursor.execute(f"SELECT * FROM {self.trade_table} order by date_inserted desc LIMIT 6")
        self.recording_data = self.connector.cursor.fetchall()
        self.recording_data = DataFrame(self.recording_data)
        print(self.recording_data)
        self.recording_data.columns = ['prediction', 'to_trade', 'date_inserted']

    def create_html_table(self) -> None:
        self.mail_html = """\
        <html>
          <head></head>
          <body>
            {0}
          </body>
        </html>
        """.format(self.recording_data.to_html())

    def send_daily_results(self) -> None:
        if self.processor.current_dt.hour == 0:
            subject_of_mail = f"{(self.processor.current_dt - timedelta(days=1)).date()} günü için Rapor"
            self.read_data_from_db()
            self.create_html_table()
            yag = SMTP(self.connector.sender_email, self.connector.sender_password)
            yag.send(self.connector.receiver_email, subject_of_mail, self.mail_html)

