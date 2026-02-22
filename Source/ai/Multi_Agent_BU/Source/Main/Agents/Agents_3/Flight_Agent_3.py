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

FLIGHT_SYSTEM = """Bạn là Flight Agent chuyên nghiệp. Hãy:
1. Tìm chuyến bay tốt nhất về giá và giờ
2. So sánh các hãng bay
3. Đề xuất options linh hoạt
4. Hỏi user muốn chọn chuyến nào"""

def flight_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    
    if not messages:
        query = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        context = memory_manager.get_context_summary(include_long_term=True, current_input=query)
        prompt = [SystemMessage(content=f"{FLIGHT_SYSTEM}\n\nContext từ memory:\n{context}")]
    else:
        query = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        context = memory_manager.get_context_summary(include_long_term=True, current_input=query)
        prompt = [
            SystemMessage(content=f"{FLIGHT_SYSTEM}\n\nContext từ memory:\n{context}"),
            *messages,
        ]
    
    response = llm.invoke(prompt)
    memory.add_message("assistant", response.content)
    
    return {
        "messages": messages + [response],
        "current_agent": "coordinator",
        "needs_user_input": True,
        "conversation_stage": "booking"
    }