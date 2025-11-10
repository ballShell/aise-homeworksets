#!/usr/bin/env python3
"""
测试优化后的提示词，验证是否能生成具体的地址和花费信息
"""

import requests
import json
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm_service import LLMService

def test_trip_planning():
    """测试行程规划功能"""
    llm_service = LLMService()
    
    # 测试参数
    destination = "北京"
    days = 3
    budget = "中等"
    preferences = "历史文化"
    
    print(f"正在生成 {destination} 的 {days} 天行程...")
    print(f"预算: {budget}, 偏好: {preferences}")
    print("-" * 50)
    
    try:
        # 构建用户提示词
        user_prompt = f"""
        目的地：{destination}
        天数：{days}天
        预算：{budget}
        偏好：{preferences}
        
        请生成详细的行程计划，包含具体的地址和预估花费。
        """
        
        # 调用LLM服务生成行程
        trip_plan = llm_service.generate_trip_plan(user_prompt)
        
        print("✅ 行程生成成功!")
        print("\n生成的行程计划:")
        print(json.dumps(trip_plan, ensure_ascii=False, indent=2))
        
        # 验证关键字段
        print("\n📋 验证结果:")
        
        if 'daily_plan' in trip_plan and trip_plan['daily_plan']:
            for day_plan in trip_plan['daily_plan']:
                print(f"\n第 {day_plan['day']} 天:")
                
                if 'daily_budget' in day_plan:
                    print(f"  ✅ 每日预算: ¥{day_plan['daily_budget']}")
                else:
                    print(f"  ❌ 缺少每日预算")
                
                if 'activities' in day_plan and day_plan['activities']:
                    for i, activity in enumerate(day_plan['activities']):
                        print(f"    活动 {i+1}: {activity.get('activity', 'N/A')}")
                        
                        location_name = activity.get('location_name', '')
                        if location_name and len(location_name) > 5:
                            print(f"      ✅ 具体地址: {location_name}")
                        else:
                            print(f"      ⚠️  地址不够具体: {location_name}")
                        
                        estimated_cost = activity.get('estimated_cost')
                        if estimated_cost:
                            print(f"      ✅ 预估花费: ¥{estimated_cost}")
                        else:
                            print(f"      ❌ 缺少预估花费")
        
        # 保存结果到文件
        output_file = "test_trip_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(trip_plan, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_trip_planning()