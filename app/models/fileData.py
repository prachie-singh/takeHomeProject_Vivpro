from dataclasses import dataclass
from typing import Optional

@dataclass
class FileData:
    required_columns = ['id', 'title', 'danceability', 'energy', 'mode', 
                        'accousticness', 'tempo', 'duration_ms', 'num_sections', 
                        'num_segments']

    id: str
    title: str
    danceability: float
    energy: float
    mode: int
    accousticness: float
    tempo: float
    duration_ms: int
    num_sections: int
    num_segments: int
    star_rating: Optional[float] = None

    def __init__(self,
                 id: str,
                 title: str,
                 danceability: float,
                 energy: float,
                 mode: int,
                 accousticness: float,
                 tempo: float,
                 duration_ms: int,
                 num_sections: int,
                 num_segments: int,
                 star_rating: Optional[float] = None):
        self.id = id
        self.title = title
        self.danceability = danceability
        self.energy = energy
        self.mode = mode
        self.accousticness = accousticness
        self.tempo = tempo
        self.duration_ms = duration_ms
        self.num_sections = num_sections
        self.num_segments = num_segments
        self.star_rating = star_rating
