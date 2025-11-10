from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date
from uuid import UUID


# --- 用户/认证 ---
class UserCreate(BaseModel):
    email: str
    password: str


# --- 核心：行程规划 ---
class PlanRequest(BaseModel):
    prompt: str  # "我想去日本，5 天，预算 1 万元，喜欢美食和动漫"


class Activity(BaseModel):
    time: str     # "09:00"
    activity: str # "参观秋叶原"
    description: Optional[str] = None
    location_name: str # "秋叶原电器街"
    lat: Optional[float] = None
    lng: Optional[float] = None


class DailyItinerary(BaseModel):
    day: int
    title: str    # "第一天：动漫圣地巡礼"
    summary: str
    activities: List[Activity]


class TripPlanResponse(BaseModel):
    trip_id: Any  # UUID
    destination: str
    daily_plan: List[DailyItinerary]
    budget_analysis: str


# --- 费用 ---
class ExpenseCreate(BaseModel):
    trip_id: Any  # UUID
    description: str  # 可以是 "拉面 50 元"
    amount: Optional[float] = None
    category: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: Any
    trip_id: Any
    description: str
    amount: float
    category: Optional[str]
    created_at: str


# --- 行程列表响应 ---
class TripListItem(BaseModel):
    id: Any
    destination: str
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[float]
    created_at: str


class TripDetailResponse(BaseModel):
    id: Any
    destination: str
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[float]
    preferences: Optional[str]
    raw_prompt: Optional[str]
    created_at: str
    daily_plan: List[DailyItinerary]
    expenses: List[ExpenseResponse]

