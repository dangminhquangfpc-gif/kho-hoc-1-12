from typing import Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AIUnavailable(RuntimeError):
    pass


class AIGrade(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    score: float = Field(ge=0)
    max_score: float = Field(gt=0)
    feedback: str = Field(max_length=10000)
    strengths: list[str] = Field(default_factory=list, max_length=50)
    mistakes: list[str] = Field(default_factory=list, max_length=50)
    missing_points: list[str] = Field(default_factory=list, max_length=50)
    suggestions: list[str] = Field(default_factory=list, max_length=50)
    confidence: float = Field(ge=0, le=1)
    model_version: str
    grading_status: str = "provisional"

    @model_validator(mode="after")
    def bounded(self):
        if self.score > self.max_score or self.grading_status != "provisional":
            raise ValueError("AI result must be provisional and within score bounds")
        return self


class AIProvider(Protocol):
    async def grade_essay(
        self, *, question: str, answer: str, rubric: list[dict]
    ) -> AIGrade: ...


class UnconfiguredProvider:
    async def grade_essay(self, **kwargs) -> AIGrade:
        raise AIUnavailable("AI provider is not configured; request human review")
