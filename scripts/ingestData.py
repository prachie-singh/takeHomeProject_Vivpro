import os
from app.service.dataIngestionService.processor import Processor

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "sample.json")
    
    processor = Processor(file_path)
    processor.process()