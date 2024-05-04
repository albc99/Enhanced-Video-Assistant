from typing import List, Optional, Tuple
from pydantic import BaseModel
from typing import Dict

"""
File: schemas.py
Description: This file contains the schemas for the EVA Project.
Functionality: This file is used to define the schemas for the EVA Project.
"""

class Project(BaseModel):
    id: int
    name: str

class User(BaseModel):
    id: int
    email: str
    current_project: Optional[Project]

class ClipTone(BaseModel):
    start: float
    end: float
    sentiment_label: str
    sentiment_score: float

class SentimentPercentages(BaseModel):
    positive: float
    negative: float
    neutral: float

class SentimentScore(BaseModel):
    positive: float
    negative: float
    neutral: float

class Feedback(BaseModel):
    sentiment_percentages: SentimentPercentages
    sentiment_score: SentimentScore
    dominant_sentiment: str
    Clarity_Score: str
    Clarity_Feedback: str
    Engagement_Score: str
    Engagement_Feedback: str

class Segment(BaseModel):
    clip_id: int
    start: float
    end: float
    text: str

class Transcript(BaseModel):
    text: Optional[str] = None
    segments: Optional[List[Segment]] = None

class StreamlinerData(BaseModel):
    deleted_clip_timestamps: Optional[List[Tuple[float, float]]] = None
    important_clip_timestamps: Optional[List[Tuple[float, float]]] = None

class NarrationImproverData(BaseModel):
    edits: Optional[List] = None

class FocusGroupData(BaseModel):
    # feedback: Optional[Feedback] = None
    # clip_tones: Optional[List[ClipTone]] = None
    feedback: Optional[List] = None
    clip_tones: Optional[List] = None
    
class ProjectJsonData(BaseModel):
    streamlinerData: StreamlinerData
    narrationImproverData: NarrationImproverData
    focusGroupData: FocusGroupData
    # transcript: Optional[Transcript] = None
    transcript: Optional[Dict] = None
    indexer_result: Optional[Dict] = None
    audio: Optional[bool] = None
    scrubber_timestamps: Optional[List] = None
    language: Optional[str] = None
    summary: Optional[str] = None

class ScrubberTimestamp(BaseModel):
    start: float = None
    end: float = None
    source: str = None

class SaveProjectData(BaseModel):
    scrubber_timestamps: Optional[List[ScrubberTimestamp]] = None