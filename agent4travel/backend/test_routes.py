"""
测试脚本：检查后端路由是否正确注册
"""
from app.main import app

print("=" * 50)
print("后端路由列表：")
print("=" * 50)

for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(route.methods)
        print(f"{methods:20s} {route.path}")

print("=" * 50)
print("\n预期的 API 路由：")
print("GET     /api/v1/trips")
print("GET     /api/v1/trips/{trip_id}")
print("POST    /api/v1/trips/plan")
print("POST    /api/v1/trips/expense")
print("=" * 50)

