from langchain_community.chat_models import ollama, ChatOllama
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from typing import TypedDict, Annotated, List
import operator
from dotenv import load_dotenv
import requests
import os
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager

load_dotenv()

llm = ChatOllama(model="llama3:8b") # <-- Sử dụng model bạn đã kéo về, ví dụ "llama3", "mistral"
prompt = hub.pull("hwchase17/react")

class AgentState(TypedDict):
    # Thông điệp của người dùng
    input: str
    # Đầu ra của từng agent sẽ được nối vào đây
    messages: Annotated[List[str], operator.add]
    
def get_weather_llm(city: str) -> str:
    """Lấy thông tin thời tiết (mô phỏng bằng LLM) có tích hợp memory."""
    user_id = "default_user"
    context = memory_manager.get_context_summary(user_id=user_id, include_long_term=True, current_input=city)
    memory_manager.add_message(role="user", content=f"[Tool Input][WeatherLLM] {city}", user_id=user_id)
    prompt = (
        f"{context}\n\n"
        f"Hãy mô tả ngắn gọn tình hình thời tiết hiện tại ở {city}."
    )
    weather_msg = llm.invoke(prompt)
    weather = weather_msg.content.strip()
    memory_manager.add_message(role="tool:WeatherLLM", content=weather, user_id=user_id)
    return weather

weatherllm_tool = Tool(
    name="WeatherLLM",
    func=get_weather_llm,
    description="Use this to get current weather for a given city. Input must be a city name."
)

def get_current_weather(city: str) -> str:
    """Lấy thời tiết hiện tại của một thành phố từ OpenWeatherMap và lưu memory."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Thiếu OPENWEATHER_API_KEY trong môi trường."
    user_id = "default_user"
    memory_manager.add_message(role="user", content=f"[Tool Input][WeatherAPI] {city}", user_id=user_id)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=vi&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        result = f"Không tìm thấy dữ liệu thời tiết cho {city}."
        memory_manager.add_message(role="tool:WeatherAPI", content=result, user_id=user_id)
        return result

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    result = f"Thời tiết tại {city} hiện tại: {desc}, nhiệt độ {temp}°C."
    memory_manager.add_message(role="tool:WeatherAPI", content=result, user_id=user_id)
    return result

weatherapi_tool = Tool(
    name="WeatherAPI",
    func=get_current_weather,
    description="Dùng để lấy thời tiết hiện tại cho một thành phố. Input là tên thành phố."
)