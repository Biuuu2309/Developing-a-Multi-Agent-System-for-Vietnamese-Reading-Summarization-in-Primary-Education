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

EXTRACTOR_SYSTEM = """Bạn là Extractor Agent chuyên nghiệp. Nhiệm vụ:
1. Trích xuất thông tin quan trọng từ văn bản
2. KHÔNG thay đổi câu từ, chỉ lấy những phần quan trọng nhất
3. Trả về bản tóm tắt trích xuất ngắn gọn"""

def extractor_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    processed_text = state.get("processed_text", "")
    grade_level = state.get("grade_level", 3)
    
    if not processed_text:
        response = AIMessage(content="Không có văn bản để trích xuất.")
        memory.add_message("assistant", response.content)
        return {
            "messages": [response],
            "current_agent": "coordinator_agent",
            "needs_user_input": True,
            "conversation_stage": "text_input",
            "original_text": state.get("original_text", ""),
            "summary_type": None,
            "grade_level": 0,
            "processed_text": "",
            "summary_result": ""
        }
    
    context = memory_manager.get_context_summary(include_long_term=True, current_input=processed_text)
    prompt = [
        SystemMessage(content=f"{EXTRACTOR_SYSTEM}\n\nContext từ memory:\n{context}\n\nVăn bản cần trích xuất:\n{processed_text}\n\nKhối lớp: {grade_level}"),
        HumanMessage(content=f"Hãy trích xuất thông tin quan trọng từ văn bản trên cho học sinh lớp {grade_level}")
    ]
    
    response = llm.invoke(prompt)
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],
        "current_agent": "grade_calibrator_agent",
        "needs_user_input": False,
        "conversation_stage": "processing",
        "original_text": state.get("original_text", ""),
        "summary_type": "extract",
        "grade_level": grade_level,
        "processed_text": processed_text,
        "summary_result": response.content
    }
extractor_tool = Tool(
    name="ExtractorAgent",
    func=extractor_agent,
    description="Use this to extract a given text. Input must be a text."
)