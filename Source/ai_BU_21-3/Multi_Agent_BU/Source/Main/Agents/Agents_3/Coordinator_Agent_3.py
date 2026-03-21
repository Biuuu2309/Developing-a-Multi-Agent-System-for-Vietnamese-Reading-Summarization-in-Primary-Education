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
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager

# Khởi tạo model LLM Local từ Ollama
llm = ChatOllama(model="llama3:8b") # <-- Sử dụng model bạn đã kéo về, ví dụ "llama3", "mistral"
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
    memory = memory_manager.get_memory()
    
    # Xử lý trường hợp messages rỗng
    if not messages:
        response = AIMessage(content="Xin chào! Tôi là trợ lý du lịch đa nhiệm. Tôi có thể giúp gì cho chuyến đi của bạn?")
        memory.add_message("assistant", response.content)
        return {
            "messages": [response],
            "current_agent": "travel_agent",
            "needs_user_input": True,
            "conversation_stage": "greeting"
        }
    
    last_message = messages[-1]
    
    if state.get("needs_user_input", False):
        return state
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content
        memory.add_message("user", user_input)
        
        context = memory_manager.get_context_summary(include_long_term=True, current_input=user_input)
        prompt = [
            SystemMessage(content=f"{COORDINATOR_SYSTEM}\n\nContext từ memory:\n{context}"),
            *messages[:-1],
            HumanMessage(content=user_input)
        ]
        
        response = llm.invoke(prompt)
        memory.add_message("assistant", response.content)
        
        # Xác định agent tiếp theo
        content = response.content.lower()
        if any(x in content for x in ["khách sạn", "phòng", "nghỉ", "hotel", "resort"]):
            next_agent = "hotel_agent"
        elif any(x in content for x in ["máy bay", "chuyến bay", "vé", "flight", "bay"]):
            next_agent = "flight_agent"
        elif any(x in content for x in ["du lịch", "lịch trình", "thăm quan", "travel", "điểm đến"]):
            next_agent = "travel_agent"
        else:
            next_agent = "coordinator"
            
        return {
            "messages": messages + [response],
            "current_agent": next_agent,
            "needs_user_input": True,
            "conversation_stage": state.get("conversation_stage", "planning")
        }
    
    # Trường hợp không phải HumanMessage
    return {
        "messages": messages,
        "current_agent": "coordinator",
        "needs_user_input": True,
        "conversation_stage": state.get("conversation_stage", "greeting")
    }