from config.logger_config import logger
import pandas as pd
from app.models.fileData import FileData

class NormalizeData:
    def __init__(self, data):
        self.data = data

    def normalize_json_to_filedata(self):
        """
        Normalize JSON data to a dictionary of FileData objects
        """
        try:
            df = pd.DataFrame(self.data)
            print(df.head())
            file_data_list = []
            for _, row in df.iterrows():
                file_data = FileData(
                    id = str(row['id']),
                    title = str(row['title']),
                    danceability = float(row['danceability']),
                    energy = float(row['energy']),
                    mode = int(row['mode']),
                    accousticness = float(row['acousticness']),
                    tempo = float(row['tempo']),
                    duration_ms = int(row['duration_ms']),
                    num_sections = int(row['num_sections']),
                    num_segments = int(row['num_segments'])
                )
                file_data_list.append(file_data)
            logger.info("Normalized JSON data to FileData objects successfully")
            return file_data_list
        except KeyError as e:
            logger.error(f"Missing expected key in JSON data: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while normalizing JSON data: {e}")
            raise
