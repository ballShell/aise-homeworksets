from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.models.schema import (
    PlanRequest,
    TripPlanResponse,
    TripListItem,
    TripDetailResponse,
    ExpenseCreate,
    ExpenseResponse,
    DailyItinerary,
    Activity
)
from app.services.llm_service import llm_service
from app.services.map_service import map_service
from app.core.config import settings
from supabase import create_client, Client
from datetime import datetime
import json
from geopy.distance import great_circle


router = APIRouter(prefix="/trips", tags=["trips"])

# Supabase 客户端
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)


@router.post("/plan", response_model=TripPlanResponse)
async def create_trip_plan(request: PlanRequest):
    """创建旅行计划（公开访问，无需登录）"""
    try:
        # 1. 调用 LLM 生成行程
        plan_data = llm_service.generate_trip_plan(request.prompt)
        
        # 2. 为每个活动获取坐标
        for day_plan in plan_data["daily_plan"]:
            for activity in day_plan["activities"]:
                if activity.get("location_name"):
                    coords = map_service.get_coordinates(activity["location_name"])
                    activity["lat"] = coords["lat"]
                    activity["lng"] = coords["lng"]
        
        # 3. 提取行程基本信息
        destination = plan_data.get("destination", "未知目的地")
        budget_analysis = plan_data.get("budget_analysis", "")
        
        # 4. 保存到数据库（无需 user_id）
        trip_data = {
            "destination": destination,
            "raw_prompt": request.prompt,
            "preferences": None,  # 可以从 prompt 中提取，这里简化处理
            "budget": None,  # 可以从 prompt 中提取
            "start_date": None,
            "end_date": None
        }
        
        trip_response = supabase.table("trips").insert(trip_data).execute()
        trip_id = trip_response.data[0]["id"]
        
        # 创建 itineraries 记录
        for day_plan in plan_data["daily_plan"]:
            itinerary_data = {
                "trip_id": trip_id,
                "day_number": day_plan["day"],
                "title": day_plan.get("title", f"第{day_plan['day']}天"),
                "summary": day_plan.get("summary", ""),
                "activities": json.dumps(day_plan["activities"], ensure_ascii=False)
            }
            supabase.table("itineraries").insert(itinerary_data).execute()
        
        # 5. 构建响应
        daily_plans = [
            DailyItinerary(
                day=dp["day"],
                title=dp.get("title", f"第{dp['day']}天"),
                summary=dp.get("summary", ""),
                activities=[
                    Activity(
                        time=a.get("time", ""),
                        activity=a.get("activity", ""),
                        description=a.get("description"),
                        location_name=a.get("location_name", ""),
                        lat=a.get("lat"),
                        lng=a.get("lng")
                    )
                    for a in dp.get("activities", [])
                ]
            )
            for dp in plan_data["daily_plan"]
        ]
        
        return TripPlanResponse(
            trip_id=trip_id,
            destination=destination,
            daily_plan=daily_plans,
            budget_analysis=budget_analysis
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trip plan: {str(e)}"
        )


@router.get("", response_model=List[TripListItem])
async def get_trips():
    """获取所有旅行计划（公开访问，无需登录）"""
    try:
        response = supabase.table("trips")\
            .select("*")\
            .execute()
        
        # 按创建时间排序（最新的在前）
        sorted_trips = sorted(
            response.data,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        trips = []
        for trip in sorted_trips:
            trips.append(TripListItem(
                id=trip["id"],
                destination=trip["destination"],
                start_date=trip.get("start_date"),
                end_date=trip.get("end_date"),
                budget=trip.get("budget"),
                created_at=trip["created_at"]
            ))
        
        return trips
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trips: {str(e)}"
        )


# Helper function to calculate distance between two coordinates
def get_distance(coord1, coord2):
    return great_circle(coord1, coord2).kilometers

@router.get("/{trip_id}", response_model=TripDetailResponse)
async def get_trip_detail(trip_id: str):
    """获取旅行计划详情（公开访问，无需登录）"""
    try:
        # 获取 trip（无需用户验证）
        trip_response = supabase.table("trips")\
            .select("*")\
            .eq("id", trip_id)\
            .execute()
        
        if not trip_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        trip = trip_response.data[0]
        
        # 获取 itineraries
        itineraries_response = supabase.table("itineraries")\
            .select("*")\
            .eq("trip_id", trip_id)\
            .execute()
        
        # 按天数排序
        sorted_itineraries = sorted(
            itineraries_response.data,
            key=lambda x: x.get("day_number", 0)
        )
        
        daily_plans = []
        for itin in sorted_itineraries:
            activities_data = json.loads(itin.get("activities", "[]"))

            # Get the destination coordinates (you might need a geocoding service for this)
            # For now, let's assume the first valid coordinate is the destination's center
            destination_coord = None
            for activity in activities_data:
                if activity.get("lat") is not None and activity.get("lng") is not None:
                    destination_coord = (activity["lat"], activity["lng"])
                    break
            
            # Filter out activities with None lat or lng and those too far from the destination
            if destination_coord:
                activities_data = [
                    activity for activity in activities_data
                    if activity.get("lat") is not None and activity.get("lng") is not None and
                       get_distance(destination_coord, (activity["lat"], activity["lng"])) < 200  # 200km radius
                ]
            else:
                activities_data = []
            
            # Get trip expenses
            activities = [
                Activity(
                    time=a.get("time", ""),
                    activity=a.get("activity", ""),
                    description=a.get("description"),
                    location_name=a.get("location_name", ""),
                    lat=a.get("lat"),
                    lng=a.get("lng")
                )
                for a in activities_data
            ]
            daily_plans.append(DailyItinerary(
                day=itin["day_number"],
                title=itin.get("title", f"第{itin['day_number']}天"),
                summary=itin.get("summary", ""),
                activities=activities
            ))
        
        # 获取 expenses
        expenses_response = supabase.table("expenses")\
            .select("*")\
            .eq("trip_id", trip_id)\
            .execute()
        
        # 按创建时间排序（最新的在前）
        sorted_expenses = sorted(
            expenses_response.data,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        expenses = [
            ExpenseResponse(
                id=exp["id"],
                trip_id=exp["trip_id"],
                description=exp["description"],
                amount=float(exp["amount"]),
                category=exp.get("category"),
                created_at=exp["created_at"]
            )
            for exp in sorted_expenses
        ]
        
        return TripDetailResponse(
            id=trip["id"],
            destination=trip["destination"],
            start_date=trip.get("start_date"),
            end_date=trip.get("end_date"),
            budget=trip.get("budget"),
            preferences=trip.get("preferences"),
            raw_prompt=trip.get("raw_prompt"),
            created_at=trip["created_at"],
            daily_plan=daily_plans,
            expenses=expenses
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trip detail: {str(e)}"
        )


@router.post("/expense", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate):
    """创建费用记录（公开访问，无需登录）"""
    try:
        # 如果未提供 amount，使用 LLM 提取
        amount = expense.amount
        category = expense.category
        description = expense.description
        
        if amount is None:
            expense_data = llm_service.extract_expense(expense.description)
            amount = expense_data.get("amount", 0)
            category = expense_data.get("category", "其他")
            description = expense_data.get("description", expense.description)
        
        # 保存到数据库（无需 user_id）
        expense_record = {
            "trip_id": str(expense.trip_id),
            "description": description,
            "amount": amount,
            "category": category
        }
        
        response = supabase.table("expenses").insert(expense_record).execute()
        expense_data = response.data[0]
        
        return ExpenseResponse(
            id=expense_data["id"],
            trip_id=expense_data["trip_id"],
            description=expense_data["description"],
            amount=float(expense_data["amount"]),
            category=expense_data.get("category"),
            created_at=expense_data["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expense: {str(e)}"
        )

