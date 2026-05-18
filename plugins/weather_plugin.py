#!/usr/bin/env python3
"""天气插件 - 使用 OpenWeatherMap API 获取天气预报"""

import os
import requests
from typing import Dict, Optional, List
from . import ToolPlugin

class WeatherPlugin(ToolPlugin):
    """天气预报插件类"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("OPENWEATHER_API_KEY", "demo_key")
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_name(self) -> str:
        """返回插件名称"""
        return "weather"
    
    def get_description(self) -> str:
        """返回插件描述"""
        return "获取指定城市的天气预报信息"
    
    def get_usage(self) -> str:
        """返回使用说明"""
        return """
使用方法:
1. 获取当前天气: weather get_weather --city <城市名> [--units metric/imperial]
2. 获取5天预报: weather get_forecast --city <城市名> [--units metric/imperial]

示例:
weather get_weather --city 北京
weather get_forecast --city Shanghai --units metric
        """.strip()
    
    def get_parameters(self) -> List[str]:
        """返回参数列表"""
        return ["city", "units"]
    
    def _get_city_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """获取城市的经纬度坐标"""
        try:
            url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&lang=zh_cn"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"],
                    "name": data["name"]
                }
            return None
        except Exception as e:
            print(f"获取城市坐标失败: {e}")
            return None
    
    def get_weather(self, city: str, units: str = "metric") -> str:
        """获取当前天气"""
        coords = self._get_city_coordinates(city)
        if not coords:
            return f"无法获取城市 {city} 的天气信息"
        
        try:
            url = f"{self.base_url}/weather?lat={coords['lat']}&lon={coords['lon']}&appid={self.api_key}&units={units}&lang=zh_cn"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp_unit = "°C" if units == "metric" else "°F"
                wind_unit = "m/s" if units == "metric" else "mph"
                
                result = f"""
📍 {coords['name']} 当前天气

🌡️ 温度: {data['main']['temp']}{temp_unit}
💧 体感温度: {data['main']['feels_like']}{temp_unit}
💦 湿度: {data['main']['humidity']}%
🌬️ 风速: {data['wind']['speed']} {wind_unit}
☁️ 天气: {data['weather'][0]['description']}
🌅 能见度: {data['visibility']/1000} km
📊 气压: {data['main']['pressure']} hPa
                """.strip()
                return result
            else:
                return f"获取天气失败: {response.status_code}"
        except Exception as e:
            return f"获取天气异常: {str(e)}"
    
    def get_forecast(self, city: str, units: str = "metric") -> str:
        """获取未来5天天气预报"""
        coords = self._get_city_coordinates(city)
        if not coords:
            return f"无法获取城市 {city} 的天气预报信息"
        
        try:
            url = f"{self.base_url}/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={self.api_key}&units={units}&lang=zh_cn"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp_unit = "°C" if units == "metric" else "°F"
                
                forecast_by_date = {}
                for item in data["list"]:
                    date = item["dt_txt"].split(" ")[0]
                    if date not in forecast_by_date:
                        forecast_by_date[date] = []
                    forecast_by_date[date].append(item)
                
                result = f"📍 {coords['name']} 未来5天天气预报\n\n"
                for i, (date, items) in enumerate(sorted(forecast_by_date.items())[:5]):
                    temps = [item["main"]["temp"] for item in items]
                    weather_desc = items[0]["weather"][0]["description"]
                    avg_temp = sum(temps) / len(temps)
                    result += f"📅 第{i+1}天 ({date}): {weather_desc}，温度 {round(avg_temp)}{temp_unit}\n"
                
                return result.strip()
            else:
                return f"获取预报失败: {response.status_code}"
        except Exception as e:
            return f"获取预报异常: {str(e)}"
    
    def execute(self, *args, **kwargs) -> str:
        """执行工具调用"""
        if args:
            command = args[0]
            if command == "get_weather":
                city = kwargs.get("city", "") or (args[1] if len(args) > 1 else "")
                units = kwargs.get("units", "metric")
                return self.get_weather(city, units)
            elif command == "get_forecast":
                city = kwargs.get("city", "") or (args[1] if len(args) > 1 else "")
                units = kwargs.get("units", "metric")
                return self.get_forecast(city, units)
            else:
                return f"未知命令: {command}"
        return "请提供命令参数"
