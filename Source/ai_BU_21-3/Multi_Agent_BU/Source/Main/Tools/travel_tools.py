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

llm = ChatOllama(model="llama3:8b")
prompt = hub.pull("hwchase17/react")

class AgentState(TypedDict):
    input: str
    message: Annotated[List[str], operator.add]
    
def analyze_travel(text: str) -> str:
    user_id = "default_user"
    context = memory_manager.get_context_summary(user_id=user_id, include_long_term=True, current_input=text)
    memory_manager.add_message(role="user", content=f"[Tool Input][TravelAnalyzer] {text}", user_id=user_id)
    prompt = (
        f"{context}\n\n"
        f"Nhiệm vụ: Tạo lịch trình du lịch, đề xuất địa điểm du lịch, hoạt động, ẩm thực.\n"
        f"Lịch trình du lịch: {text}\n"
        f"Trả về dưới dạng JSON với các key: destination, activity, food, accommodation."
    )
    analysis_msg = llm.invoke(prompt)
    analysis = analysis_msg.content.strip()
    memory_manager.add_message(role="tool:TravelAnalyzer", content=analysis, user_id=user_id)
    return analysis

travel_tool = Tool(
    name="TravelAnalyzer",
    func=analyze_travel,
    description="Useful for creating a travel plan of a given text. Input should be a string. Return in Vietnamese."
)