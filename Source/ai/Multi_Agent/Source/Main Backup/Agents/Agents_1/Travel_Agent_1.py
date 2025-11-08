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

TRAVEL_SYSTEM = """Bạn là Travel Agent chuyên nghiệp. Hãy:
1. Tạo lịch trình du lịch sáng tạo, hấp dẫn
2. Đề xuất điểm đến, hoạt động, ẩm thực
3. Tư vấn dựa trên sở thích user
4. Kết thúc bằng câu hỏi để tiếp tục booking"""

def travel_agent(state: AgentState):
    messages = state["messages"]
    
    # Đảm bảo có ít nhất 1 message
    if not messages:
        prompt = [SystemMessage(content=TRAVEL_SYSTEM)]
    else:
        prompt = [
            SystemMessage(content=TRAVEL_SYSTEM),
            *messages,
        ]
    
    response = llm.invoke(prompt)
    
    return {
        "messages": messages + [response],
        "current_agent": "coordinator",
        "needs_user_input": True,
        "conversation_stage": "planning"
    }
