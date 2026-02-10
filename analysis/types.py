from typing import Optional, TypedDict
from pydantic import BaseModel, Field

class ModelConfig(TypedDict):
    client: object
    model: Optional[str]
    temperature: Optional[float]

class SemanticAnalysisInput(TypedDict, total=False):
    documentText: str
    modelConfig: ModelConfig

class SemanticAnalysisOutput(TypedDict):
    semanticSummary: str
    keyThemes: str
    overallSentiment: str
    error: Optional[str]
    code: Optional[int]

class PsychometricAnalysisInput(TypedDict, total=False):
    text: str
    modelConfig: ModelConfig


class PsychometricAnalysisOutput(TypedDict):
    psychologicalTraits: str
    risks: str
    trends: str
    error: Optional[str]
    code: Optional[int]

class TechnicalAnalysisInput(TypedDict, total=False):
    text: str
    modelConfig: ModelConfig
    threshold: Optional[int]
    criteria: dict
    jd_prompt: Optional[str]

class TechnicalAnalysisOutput(TypedDict):
    technicalSummary: str
    skillMatch: str
    experienceLevel: str
    overallScore: str
    error: Optional[str]
    code: Optional[int]

class ReportingInput(TypedDict):
    technical: TechnicalAnalysisOutput
    semantic: SemanticAnalysisOutput
    psychometric: PsychometricAnalysisOutput

class ReportingOutput(TypedDict):
    finalScore: int
    finalReport: str
    error: Optional[str]
    code: Optional[int]

#
class AnalysisRequest(BaseModel):
    document_text: str = Field(min_length=1, description="Raw document text to analyze")
    ai_model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
    threshold: int | None = Field(default=None, ge=0, le=100)
    criteria: dict | None = None
    jd_prompt: str | None = None

class SemanticOut(BaseModel):
    semanticSummary: str
    keyThemes: str
    overallSentiment: str


class PsychometricOut(BaseModel):
    psychologicalTraits: str
    risks: str
    trends: str


class AnalysisResponse(BaseModel):
    semantic: SemanticOut
    psychometric: PsychometricOut
