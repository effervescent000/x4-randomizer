from pydantic import BaseModel


class Config(BaseModel):
    sector_count: int
