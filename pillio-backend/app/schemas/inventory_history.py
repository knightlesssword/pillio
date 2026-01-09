from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import StockChangeType


# Base inventory history schema
class InventoryHistoryBase(BaseModel):
    change_amount: int
    change_type: StockChangeType
    previous_stock: int
    new_stock: int
    reference_id: Optional[int] = None
    notes: Optional[str] = None


# Inventory history creation schema
class InventoryHistoryCreate(InventoryHistoryBase):
    medicine_id: int


# Inventory history response schema
class InventoryHistory(InventoryHistoryBase):
    id: int
    medicine_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventory history with medicine details
class InventoryHistoryWithMedicine(InventoryHistory):
    medicine_name: str
    
    class Config:
        from_attributes = True


# Stock adjustment request
class StockAdjustmentRequest(BaseModel):
    medicine_id: int
    adjustment: int = Field(..., description="Positive for add, negative for remove")
    change_type: StockChangeType
    reason: Optional[str] = None
    notes: Optional[str] = None


# Bulk stock adjustment
class BulkStockAdjustment(BaseModel):
    adjustments: list[StockAdjustmentRequest]


# Stock report
class StockReport(BaseModel):
    medicine_id: int
    medicine_name: str
    current_stock: int
    min_stock_alert: int
    total_consumed_this_month: int
    total_added_this_month: int
    average_monthly_consumption: float
    estimated_days_remaining: Optional[int]

