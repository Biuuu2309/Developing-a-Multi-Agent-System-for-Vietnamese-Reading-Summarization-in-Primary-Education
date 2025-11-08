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

SPELLCHECKER_SYSTEM = """Bạn là Spell Checker Agent chuyên nghiệp. Hãy:
Kiểm tra từ viết sai và sửa lại cho đúng hoàn cảnh ngữ nghĩa so với văn bản gốc. KHÔNG ĐƯỢC THÊM BỚT CÂU TỪ, NỘI DUNG.
Sau đó trả về văn bản đã sửa lại.
"""

def spellchecker_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    
    if not messages:
        query = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        context = memory_manager.get_context_summary(include_long_term=True, current_input=query)
        prompt = [SystemMessage(content=f"{SPELLCHECKER_SYSTEM}\n\nContext từ memory:\n{context}")]
    else:
        query = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        context = memory_manager.get_context_summary(include_long_term=True, current_input=query)
        prompt = [
            SystemMessage(content=f"{SPELLCHECKER_SYSTEM}\n\nContext từ memory:\n{context}"),
            *messages,
        ]
    
    response = llm.invoke(prompt)
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],  # Chỉ trả về message mới
        "current_agent": "coordinator_agent",
        "needs_user_input": False,
        "conversation_stage": "checking",
        "check": "exactly"  # Mặc định chấp nhận văn bản đã sửa
    }
spellchecker_tool = Tool(
    name="SpellCheckerAgent",
    func=spellchecker_agent,
    description="Use this to check the spelling of a given text. Input must be a text."
)