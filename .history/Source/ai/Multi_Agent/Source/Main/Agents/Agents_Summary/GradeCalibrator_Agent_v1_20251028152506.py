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
    conversation_stage: Literal["greeting", "planning", "checking", "processing", "aggregator", "completed"]

GRADE_CALIBRATOR_SYSTEM = """Bạn là Grade Calibrator Agent chuyên nghiệp. Hãy:
Điều chỉnh độ dài và từ vựng phù hợp theo khối lớp (1-5) nếu yêu cầu của user là bản tóm tắt diễn giải. Nếu là bản tóm tắt trích xuất, chỉ được điều chỉnh độ dài mà KHÔNG THAY ĐỔI CÂU TỪ, NỘI DUNG.
"""

def grade_calibrator_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    
    if not messages:
        query = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        context = memory_manager.get_context_summary(include_long_term=True, current_input=query)
        prompt = [SystemMessage(content=f"{GRADE_CALIBRATOR_SYSTEM}\n\nContext từ memory:\n{context}")]
    else:
        query = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        context = memory_manager.get_context_summary(include_long_term=True, current_input=query)
        prompt = [
            SystemMessage(content=f"{GRADE_CALIBRATOR_SYSTEM}\n\nContext từ memory:\n{context}"),
            *messages,
        ]
    
    response = llm.invoke(prompt)
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],  # Chỉ trả về message mới
        "current_agent": "evaluator_agent",
        "needs_user_input": False,
        "conversation_stage": "processing"
    }
grade_calibrator_tool = Tool(
    name="GradeCalibratorAgent",
    func=grade_calibrator_agent,
    description="Use this to calibrate a given text. Input must be a text."
)