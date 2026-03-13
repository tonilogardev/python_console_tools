from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Region(BaseModel):
    id: str
    bbox: Optional[list[float]] = Field(default=None, description="xmin,ymin,xmax,ymax")


class CopernicusRequest(BaseModel):
    region: Region
    from_date: str
    to_date: str
    product: str
