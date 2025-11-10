import httpx
from typing import Optional, Dict
from app.core.config import settings


class MapService:
    def __init__(self):
        self.api_key = settings.GAODE_WEB_API_KEY
        self.base_url = "https://restapi.amap.com/v3/geocode/geo"
    
    def get_coordinates(self, location_name: str) -> Dict[str, Optional[float]]:
        """
        调用高德地图地理编码 API 获取坐标
        返回: {"lat": float, "lng": float} 或 {"lat": None, "lng": None}
        """
        try:
            params = {
                "key": self.api_key,
                "address": location_name,
                "output": "json"
            }
            
            with httpx.Client() as client:
                response = client.get(self.base_url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1" and data.get("count") > 0:
                    # 获取第一个结果
                    location = data["geocodes"][0]["location"]
                    lng, lat = map(float, location.split(","))
                    return {"lat": lat, "lng": lng}
                else:
                    # 未找到位置，返回 None
                    return {"lat": None, "lng": None}
        except Exception as e:
            # 发生错误时返回 None
            print(f"Error getting coordinates for {location_name}: {str(e)}")
            return {"lat": None, "lng": None}


map_service = MapService()

