import datetime as dt
import re
from typing import Literal, Optional

from pydantic import BaseModel, computed_field, field_validator

MAX_DAYS = 14
MAX_COMPANY_LENGTH = 80

_ALLOWED_COMPANY = re.compile(r"[\w &.,'+\-()!/]+")
_HAS_LETTER_OR_DIGIT = re.compile(r"[^\W_]")
_MANY_SPACES = re.compile(r" +")


class PlanRequest(BaseModel):
    company: str
    interview_date: dt.date

    @field_validator("company")
    @classmethod
    def clean_company(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("company must not be blank")
        if len(value) > MAX_COMPANY_LENGTH:
            raise ValueError(f"company must be at most {MAX_COMPANY_LENGTH} characters")
        # The name goes into an LLM prompt, so only plain name characters are allowed
        # (no line breaks, quotes, braces, angle brackets or other markup).
        if not _ALLOWED_COMPANY.fullmatch(value) or not _HAS_LETTER_OR_DIGIT.search(value):
            raise ValueError("company contains characters that are not allowed")
        return _MANY_SPACES.sub(" ", value)


class Task(BaseModel):
    id: str
    type: str
    text: str
    problem_id: Optional[str] = None
    done: bool = False


class Day(BaseModel):
    number: int
    date: dt.date
    title: str
    skipped: bool = False
    tasks: list[Task]


class Progress(BaseModel):
    done: int
    total: int
    percent: int


class TaskUpdate(BaseModel):
    done: bool


class DayUpdate(BaseModel):
    skipped: bool


class Plan(BaseModel):
    id: str
    company: str
    interview_date: dt.date
    source: Literal["llm", "fallback"]
    days: list[Day]

    @computed_field
    @property
    def progress(self) -> Progress:
        tasks = [t for d in self.days if not d.skipped for t in d.tasks]
        total = len(tasks)
        done = sum(1 for t in tasks if t.done)
        return Progress(done=done, total=total, percent=round(100 * done / total) if total else 0)
