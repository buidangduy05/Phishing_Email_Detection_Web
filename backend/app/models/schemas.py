from pydantic import BaseModel, Field


class EmailFeature(BaseModel):
    title: str
    description: str


class AnalysisResponse(BaseModel):
    isPhishing: bool
    summary: str
    features: list[EmailFeature] = Field(default_factory=list)
    model: str


class HealthResponse(BaseModel):
    status: str
