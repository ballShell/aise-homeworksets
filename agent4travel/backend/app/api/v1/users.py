from fastapi import APIRouter
from app.models.schema import UserCreate

router = APIRouter(prefix="/users", tags=["users"])

# 注意：用户注册/登录由 Supabase 前端 SDK 处理
# 这个路由文件可以保留用于未来的用户管理功能

@router.get("/me")
async def get_current_user_info():
    """获取当前用户信息（由前端 Supabase SDK 处理）"""
    return {"message": "User authentication is handled by Supabase client SDK"}

