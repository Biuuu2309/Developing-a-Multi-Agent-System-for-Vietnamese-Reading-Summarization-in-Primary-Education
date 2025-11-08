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
    messages: Annotated[List[Any], operator.add]
    current_agent: str
    needs_user_input: bool
    conversation_stage: Literal["greeting", "text_input", "summary_type", "processing", "completed"]
    original_text: str
    summary_type: Literal["extract", "abstract", None]
    grade_level: int
    processed_text: str
    summary_result: str

AGGREGATOR_SYSTEM = """Bạn là Aggregator Agent chuyên nghiệp. Nhiệm vụ:
1. Tổng hợp bản tóm tắt cuối cùng
2. Đưa ra kết quả hoàn chỉnh cho user
3. Hỏi user đánh giá về hệ thống"""

def aggregator_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    summary_result = state.get("summary_result", "")
    summary_type = state.get("summary_type", "extract")
    grade_level = state.get("grade_level", 3)
    original_text = state.get("original_text", "")
    
    if not summary_result:
        response = AIMessage(content="Không có bản tóm tắt để tổng hợp.")
        memory.add_message("assistant", response.content)
        return {
            "messages": [response],
            "current_agent": "coordinator_agent",
            "needs_user_input": True,
            "conversation_stage": "text_input",
            "original_text": "",
            "summary_type": None,
            "grade_level": 0,
            "processed_text": "",
            "summary_result": "",
            "final_result": ""
        }
    
    # Tạo bản tóm tắt cuối cùng
    final_summary = f"""📝 **BẢN TÓM TẮT CUỐI CÙNG**

**Loại tóm tắt:** {summary_type.upper()}
**Khối lớp:** {grade_level}

**Nội dung:**
{summary_result}

---

Bản tóm tắt đã hoàn thành! Bạn có hài lòng với kết quả này không? Hãy đánh giá hệ thống từ 1-10 điểm."""
    
    response = AIMessage(content=final_summary)
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],
        "current_agent": "coordinator_agent",
        "needs_user_input": False,  # Không cần user input, sẽ chuyển về coordinator
        "conversation_stage": "processing",
        "original_text": original_text,
        "summary_type": summary_type,
        "grade_level": grade_level,
        "processed_text": state.get("processed_text", ""),
        "summary_result": summary_result,
        "final_result": final_summary  # Truyền kết quả cuối cùng
    }
aggregator_tool = Tool(
    name="AggregatorAgent",
    func=aggregator_agent,
    description="Use this to aggregate a given text. Input must be a text."
)