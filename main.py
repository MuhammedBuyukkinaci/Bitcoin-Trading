import gc
from Processor import Processor
from Connector import Connector
from ExportResult import ExportResult

# Setting up Connector object
connector = Connector()
# Model_path
model_path = 'model.h5'
# Processor
processor = Processor(connector, model_path)


def main():
    processor.read_data_from_db()
    processor.filter_data()

    if len(processor.data) == connector.time_step + 1:
        processor.create_train_data()
        processor.convert_to_pandas_df()
        processor.expand_dims()
        # Load the model
        processor.load_model()
        # Get predictions
        processor.get_prediction(trade_threshold=connector.trade_threshold)
        print(processor.to_trade, processor.prediction)
        # Exporting Result
        export_result = ExportResult(processor=processor, connector=connector, trade_table=connector.trade_table)
        # Whether to send email or not
        export_result.send_email()
        # Always inserting the record to DB
        export_result.insert_record_to_db()
        # Send Daily E-mail on latest results
        export_result.send_daily_results()
    else:
        print("data quality problem")
    # Garbage Collector
    gc.collect()


if __name__ == '__main__':
    main()
