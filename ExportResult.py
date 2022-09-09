from yagmail import SMTP
from numpy import round as rounder
import Processor
import Connector


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

