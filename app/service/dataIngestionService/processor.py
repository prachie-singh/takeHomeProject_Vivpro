from config.logger_config import logger
from app.service.dataIngestionService.json_reader import JSONReader
from app.service.dataIngestionService.normalizeData import NormalizeData
from app.service.dataIngestionService.insert_data import InsertData

class Processor:
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def process(self):
        try:
            self.json_reader = JSONReader(self.file_path)
            data = self.json_reader.read_json()
            logger.info("JSON data processed successfully")
            self.normalized_data = NormalizeData(data)
            normalized_data = self.normalized_data.normalize_json_to_filedata()
            logger.info("Data normalized successfully")
            inserter = InsertData()
            pgsql_conn = inserter.get_pgsql_connection()
            inserter.create_table(pgsql_conn)
            inserter.insert_file_data(pgsql_conn, normalized_data)
            logger.info("Data inserted into PostgreSQL successfully")

        except Exception as e:
            logger.error(f"Error processing JSON data: {e}")
            raise