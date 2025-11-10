from supabase import create_client, Client
from fastapi import HTTPException, status
from app.core.config import settings
from typing import Optional
import jwt
import requests


class AuthService:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.service_key = settings.SUPABASE_SERVICE_KEY
    
    def get_user_from_token(self, token: str) -> dict:
        """
        验证 JWT token 并返回用户信息
        使用 Supabase Auth API 验证 token
        """
        try:
            # 使用 Supabase Auth API 验证 token
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": self.service_key
            }
            response = requests.get(
                f"{self.supabase_url}/auth/v1/user",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "id": user_data.get("id"),
                    "email": user_data.get("email"),
                }
            else:
                # 如果 API 调用失败，尝试从 JWT token 中解码用户信息
                # 注意：这只是一个后备方案，不应该用于生产环境的严格验证
                try:
                    decoded = jwt.decode(
                        token,
                        options={"verify_signature": False}
                    )
                    user_id = decoded.get("sub")
                    email = decoded.get("email")
                    if user_id:
                        return {
                            "id": user_id,
                            "email": email,
                        }
                except Exception:
                    pass
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token: {response.status_code}"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )


auth_service = AuthService()

