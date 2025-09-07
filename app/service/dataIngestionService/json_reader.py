import json
import pandas as pd
from typing import List, Dict
from config.logger_config import logger
from app.service.dataIngestionService.normalizeData import NormalizeData
from app.models.fileData import FileData

class JSONReader:
    """
    A class to read and parse JSON files
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def read_json(self) -> Dict:
        """
        Read JSON file from disk
        """
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            logger.info(f"Loaded JSON file successfully: {self.file_path}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file: {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
