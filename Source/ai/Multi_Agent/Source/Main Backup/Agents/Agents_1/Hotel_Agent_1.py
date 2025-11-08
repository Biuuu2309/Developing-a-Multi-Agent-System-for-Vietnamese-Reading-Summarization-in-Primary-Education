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

HOTEL_SYSTEM = """Bạn là Hotel Agent chuyên nghiệp. Hãy:
1. Đề xuất khách sạn phù hợp ngân sách và vị trí
2. So sánh ưu nhược điểm từng option
3. Mô tả tiện nghi, view, dịch vụ
4. Hỏi user muốn chọn khách sạn nào"""

def hotel_agent(state: AgentState):
    messages = state["messages"]
    
    if not messages:
        prompt = [SystemMessage(content=HOTEL_SYSTEM)]
    else:
        prompt = [
            SystemMessage(content=HOTEL_SYSTEM),
            *messages,
        ]
    
    response = llm.invoke(prompt)
    
    return {
        "messages": messages + [response],
        "current_agent": "coordinator",
        "needs_user_input": True,
        "conversation_stage": "booking"
    }