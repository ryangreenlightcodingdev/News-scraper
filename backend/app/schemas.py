from datetime import datetime

from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    source: str
    category: str
    url: str
    timestamp: datetime
    summary: str = ""


class ArticleRead(ArticleBase):
    id: int

    model_config = {"from_attributes": True}


class FiltersResponse(BaseModel):
    categories: list[str]
    sources: list[str]


class RefreshResponse(BaseModel):
    inserted: int
    total: int
