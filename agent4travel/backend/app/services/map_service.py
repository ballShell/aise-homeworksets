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
                
                # 检查响应状态和结果数量
                status = data.get("status")
                count = data.get("count", 0)
                
                # 确保 count 是数字类型
                if isinstance(count, str):
                    try:
                        count = int(count)
                    except (ValueError, TypeError):
                        count = 0
                
                if status == "1" and count > 0 and "geocodes" in data and len(data["geocodes"]) > 0:
                    # 获取第一个结果
                    location = data["geocodes"][0].get("location", "")
                    if location:
                        try:
                            lng, lat = map(float, location.split(","))
                            return {"lat": lat, "lng": lng}
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing location '{location}' for {location_name}: {str(e)}")
                            return {"lat": None, "lng": None}
                    else:
                        return {"lat": None, "lng": None}
                else:
                    # 未找到位置，返回 None
                    print(f"No location found for {location_name}, status: {status}, count: {count}")
                    return {"lat": None, "lng": None}
        except Exception as e:
            # 发生错误时返回 None
            print(f"Error getting coordinates for {location_name}: {str(e)}")
            return {"lat": None, "lng": None}


map_service = MapService()

