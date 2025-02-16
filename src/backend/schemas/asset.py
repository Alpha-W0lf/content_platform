from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4


class AssetBase(BaseModel):
    asset_type: str
    path: str
    approved: Optional[bool] = False


class AssetCreate(AssetBase):
    project_id: UUID4


class Asset(AssetBase):
    id: UUID4
    project_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
