from app.service.dataIngestionService.processor import Processor

if __name__ == "__main__":
    file_path = "/Users/prachisingh/Downloads/playlist[76][36][48][6][49][41][28][85][7][90][20][31][56][54].json"
    processor = Processor(file_path)
    processor.process()