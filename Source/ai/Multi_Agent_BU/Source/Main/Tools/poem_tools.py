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

llm = ChatOllama(model="llama3:8b") # <-- Sử dụng model bạn đã kéo về, ví dụ "llama3", "mistral"
prompt = hub.pull("hwchase17/react")

class AgentState(TypedDict):
    # Thông điệp của người dùng
    input: str
    # Đầu ra của từng agent sẽ được nối vào đây
    messages: Annotated[List[str], operator.add]
    
# Tool cho Agent Nhà Thơ
def write_poem(theme: str) -> str:
    """Viết một bài thơ ngắn về chủ đề được cho.

    Tích hợp memory: dùng context, lưu input/output.
    """
    user_id = "default_user"
    context = memory_manager.get_context_summary(user_id=user_id, include_long_term=True, current_input=theme)
    memory_manager.add_message(role="user", content=f"[Tool Input][PoemWriter] {theme}", user_id=user_id)
    prompt = (
        f"{context}\n\n"
        f"Hãy viết một bài thơ ngắn 4 câu, mạch lạc, về chủ đề: {theme}."
    )
    poem_msg = llm.invoke(prompt)
    poem = poem_msg.content.strip()
    memory_manager.add_message(role="tool:PoemWriter", content=poem, user_id=user_id)
    return poem

poem_tool = Tool(
    name="PoemWriter",
    func=write_poem,
    description="Useful for writing a short poem about a given theme. Input should be the theme."
)