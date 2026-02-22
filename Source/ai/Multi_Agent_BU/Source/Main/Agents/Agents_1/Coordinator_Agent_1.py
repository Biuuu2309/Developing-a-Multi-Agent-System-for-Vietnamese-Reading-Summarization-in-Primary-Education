from dotenv import load_dotenv
load_dotenv()

# from langchain_openai import ChatOpenAI # <-- Dòng cũ, comment lại
from langchain_community.chat_models import ChatOllama # <-- Dòng mới
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import Tool
from langgraph.graph import END, StateGraph
from typing import TypedDict, Annotated, List, Any, Dict, Literal
import operator
import requests
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Khởi tạo model LLM Local từ Ollama
llm = ChatOllama(model="llama3") # <-- Sử dụng model bạn đã kéo về, ví dụ "llama3", "mistral"
class AgentState(TypedDict):
    messages: List[Any]
    current_agent: str
    needs_user_input: bool
    conversation_stage: Literal["greeting", "planning", "booking", "confirmation", "completed"]

COORDINATOR_SYSTEM = """Bạn là Coordinator Agent thông minh. Nhiệm vụ:
1. Phân tích yêu cầu user và chuyển cho agent phù hợp
2. Travel: du lịch, lịch trình, điểm đến
3. Hotel: khách sạn, phòng, resort  
4. Flight: máy bay, vé, chuyến bay
5. Luôn trả lời tự nhiên và hỏi user để xác nhận"""

def coordinator_agent(state: AgentState):
    messages = state["messages"]
    
    # Khởi tạo nếu chưa có message
    if not messages:
        response = AIMessage(content="Xin chào! Tôi là trợ lý du lịch đa nhiệm. Tôi có thể giúp gì cho chuyến đi của bạn?")
        return {
            "messages": [response],
            "current_agent": "END",  # Chờ user nhập
            "needs_user_input": True,
            "conversation_stage": "greeting"
        }
    
    last_message = messages[-1]
    
    # Nếu đang cần user input thì đừng xử lý thêm
    if state.get("needs_user_input", False):
        return {
            **state,
            "current_agent": "END"  # Chặn vòng lặp vô hạn
        }
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content
        
        prompt = [
            SystemMessage(content=COORDINATOR_SYSTEM),
            *messages[:-1],
            HumanMessage(content=user_input)
        ]
        
        response = llm.invoke(prompt)
        content = response.content.lower()
        
        if any(x in content for x in ["khách sạn", "phòng", "nghỉ", "hotel", "resort"]):
            next_agent = "hotel_agent"
        elif any(x in content for x in ["máy bay", "chuyến bay", "vé", "flight", "bay"]):
            next_agent = "flight_agent"
        elif any(x in content for x in ["du lịch", "lịch trình", "thăm quan", "travel", "điểm đến"]):
            next_agent = "travel_agent"
        else:
            # Hỏi lại thay vì lặp
            return {
                "messages": messages + [AIMessage(content="Bạn muốn hỏi về du lịch, khách sạn hay vé máy bay?")],
                "current_agent": "END",
                "needs_user_input": True
            }

        return {
            "messages": messages + [response],
            "current_agent": next_agent,
            "needs_user_input": False,  # Cho phép agent kế tiếp xử lý
            "conversation_stage": state.get("conversation_stage", "planning")
        }
    
    return {
        "messages": messages,
        "current_agent": "END",
        "needs_user_input": True
    }
