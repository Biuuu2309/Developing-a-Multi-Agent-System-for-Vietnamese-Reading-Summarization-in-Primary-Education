
# Ensure repository root (with 'Source/ai') is on sys.path
from pathlib import Path
import sys

project_root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Source' / 'ai').exists()), None)
if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import Tool
from langgraph.graph import END, StateGraph
import operator
import requests
from Source.ai.Multi_Agent.Source.Main.Tools import poem_tools, sentiment_tools, travel_tools, weather_tools
from Source.ai.Multi_Agent.Source.Main.Agents.Agents_1 import Coordinator_Agent_1, Flight_Agent_1, Hotel_Agent_1, Travel_Agent_1
from Source.ai.Multi_Agent.Source.Main.Agents.Agents_2 import Coordinator_Agent_2, Flight_Agent_2, Hotel_Agent_2, Travel_Agent_2
from Source.ai.Multi_Agent.Source.Main.Agents.Agents_3 import Coordinator_Agent_3, Flight_Agent_3, Hotel_Agent_3, Travel_Agent_3, Aggregator_Agent_3
from Source.ai.Multi_Agent.Source.Main.Agents.Agents_Summary import Abstracter_Agent, Aggregator_Agent, Coordinator_Agent, Evaluator_Agent, Extractor_Agent, GradeCalibrator_Agent, OCR_Agent, SpellChecker_Agent, InputClassifier_Agent
from typing import TypedDict, Annotated, List, Any, Dict, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager
from Source.ai.Multi_Agent.Source.Main.Memory.memory.long_term_memory import long_term_memory
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
import os
#from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOllama(model="llama3:8b") # <-- Sử dụng model bạn đã kéo về, ví dụ "llama3", "mistral"

class AgentState(TypedDict):
    input: str
    messages: Annotated[List[str], operator.add]
    
prompt = hub.pull("hwchase17/react")

def new_session(user_id: str = "default_user", clear_history: bool = True, keep_preferences: bool = True, auto_continue: bool = False, replay_last_n: int = 20) -> str:
    sid = memory_manager.start_new_session(user_id=user_id, clear_history=clear_history, keep_preferences=keep_preferences)
    print(f"New session started: {sid}")
    if auto_continue:
        initial_state = build_state_from_memory(user_id=user_id, max_messages=replay_last_n)
        run_langgraph_chat(initial_state=initial_state)
    return sid

sid = new_session()

all_items = long_term_memory.collection.get(include=["metadatas"])
session_ids = sorted({m.get("session_id") for m in all_items["metadatas"] if m})
print(session_ids)

def create_initial_state() -> AgentState:
    return {
        "messages": [],
        "current_agent": "coordinator_agent",
        "needs_user_input": False,
        "conversation_stage": "greeting",
        "original_text": "",
        "summary_type": None,
        "grade_level": 0,
        "processed_text": "",
        "summary_result": "",
        "final_result": "",
        "input_classification": None
    }
    
# Cập nhật AgentState với workflow mới
class AgentState(TypedDict):
    messages: Annotated[List[Any], operator.add]
    current_agent: str
    needs_user_input: bool
    conversation_stage: Literal["greeting", "text_input", "summary_type", "processing", "completed", "evaluation"]
    original_text: str
    summary_type: Literal["extract", "abstract", None]
    grade_level: int
    processed_text: str
    summary_result: str
    final_result: str
    input_classification: Literal["greeting", "off_topic", "system_question", "text_to_summarize", None]

def create_initial_state() -> AgentState:
    return {
        "messages": [],
        "current_agent": "coordinator_agent",
        "needs_user_input": False,
        "conversation_stage": "greeting",
        "original_text": "",
        "summary_type": None,
        "grade_level": 0,
        "processed_text": "",
        "summary_result": "",
        "final_result": "",
        "input_classification": None
    }

# Hàm điều hướng thông minh cho coordinator
def coordinator_router(state: AgentState):
    stage = state.get("conversation_stage", "greeting")
    needs_input = state.get("needs_user_input", False)
    
    if needs_input:
        return "END"  # Chờ user input
    
    # QUAN TRỌNG: Kiểm tra nếu có user input mới
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], HumanMessage):
        user_input = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        user_lower = user_input.lower() if isinstance(user_input, str) else ""
        
        # QUAN TRỌNG: Kiểm tra nếu đã có original_text/processed_text và input có từ khóa tóm tắt
        # Đây là yêu cầu về loại tóm tắt, KHÔNG cần phân loại lại
        original_text = state.get("original_text", "")
        processed_text = state.get("processed_text", "")
        
        if (original_text or processed_text) and any(word in user_lower for word in [
            "tóm tắt", "diễn giải", "trích xuất", "extract", "abstract",
            "lớp 1", "lớp 2", "lớp 3", "lớp 4", "lớp 5",
            "khối 1", "khối 2", "khối 3", "khối 4", "khối 5",
            "lớp", "khối"
        ]):
            # Đã có văn bản và đây là yêu cầu tóm tắt, xử lý trực tiếp ở coordinator
            return "coordinator_agent"
        
        # Nếu đang ở stage summary_type, không phân loại, xử lý trực tiếp
        if stage == "summary_type":
            return "coordinator_agent"
        
        # Có input từ user, cần phân loại trước
        classification = state.get("input_classification")
        if classification is None:
            # Chưa được phân loại, BẮT BUỘC gọi input_classifier
            print("🔍 Chưa có classification, gọi input_classifier_agent...")
            return "input_classifier_agent"
    
    # Sau khi đã có classification, mới xử lý theo stage
    if stage == "greeting":
        return "coordinator_agent"
    elif stage == "text_input":
        # Chỉ chuyển sang OCR nếu đã được phân loại là text_to_summarize
        classification = state.get("input_classification")
        if classification == "text_to_summarize":
            return "reader_ocr_agent"  # Bắt đầu xử lý văn bản
        else:
            # Chưa phải văn bản cần tóm tắt, quay lại coordinator để xử lý
            return "coordinator_agent"
    elif stage == "summary_type":
        return "coordinator_agent"  # Chờ user chọn loại tóm tắt - xử lý trực tiếp
    elif stage == "processing":
        summary_type = state.get("summary_type")
        if summary_type == "extract":
            return "extractor_agent"
        elif summary_type == "abstract":
            return "abstracter_agent"
        else:
            return "coordinator_agent"
    elif stage == "completed":
        return "coordinator_agent"  # Chờ đánh giá
    else:
        return "coordinator_agent"

# Build đồ thị LangGraph với workflow mới
workflow = StateGraph(AgentState)

# Thêm các nodes
workflow.add_node("coordinator_agent", Coordinator_Agent.coordinator_agent)
workflow.add_node("input_classifier_agent", InputClassifier_Agent.input_classifier_agent)
workflow.add_node("reader_ocr_agent", OCR_Agent.ocr_agent)
workflow.add_node("spellchecker_agent", SpellChecker_Agent.spellchecker_agent)
workflow.add_node("extractor_agent", Extractor_Agent.extractor_agent)
workflow.add_node("abstracter_agent", Abstracter_Agent.abstracter_agent)
workflow.add_node("grade_calibrator_agent", GradeCalibrator_Agent.grade_calibrator_agent)
workflow.add_node("evaluator_agent", Evaluator_Agent.evaluator_agent)
workflow.add_node("aggregator_agent", Aggregator_Agent.aggregator_agent)

# Set entry point
workflow.set_entry_point("coordinator_agent")

# Workflow mới: Coordinator -> InputClassifier (nếu có user input) -> Coordinator -> OCR -> SpellChecker -> Coordinator -> Extractor/Abstracter -> GradeCalibrator -> Evaluator -> Aggregator -> Coordinator
workflow.add_conditional_edges("coordinator_agent", coordinator_router, {
    "coordinator_agent": "coordinator_agent",
    "input_classifier_agent": "input_classifier_agent",
    "reader_ocr_agent": "reader_ocr_agent",
    "extractor_agent": "extractor_agent", 
    "abstracter_agent": "abstracter_agent",
    "END": END
})

# Sau khi phân loại input, quay lại coordinator để xử lý
workflow.add_edge("input_classifier_agent", "coordinator_agent")

# Workflow tuần tự sau khi có văn bản
workflow.add_edge("reader_ocr_agent", "spellchecker_agent")
workflow.add_edge("spellchecker_agent", "coordinator_agent")  # Quay lại coordinator để hỏi loại tóm tắt

# Sau khi có loại tóm tắt, chạy pipeline
workflow.add_edge("extractor_agent", "grade_calibrator_agent")
workflow.add_edge("abstracter_agent", "grade_calibrator_agent")
workflow.add_edge("grade_calibrator_agent", "evaluator_agent")
workflow.add_edge("evaluator_agent", "aggregator_agent")
workflow.add_edge("aggregator_agent", "coordinator_agent")  # Quay lại coordinator để hỏi đánh giá

app = workflow.compile()

print("✅ Workflow mới đã được thiết lập theo yêu cầu!")


# Import hàm build_state_from_memory đã được sửa từ memory_helpers.py
# Hàm này xác định đúng conversation_stage từ lịch sử chat
from Source.ai.Multi_Agent.Source.Main.Program_Main.memory_helpers import build_state_from_memory

print("✅ Đã import hàm build_state_from_memory từ memory_helpers.py!")


def read_long_term_memory_by_session_id(session_id: str):
    col = long_term_memory.collection
    all_items = col.get(include=["documents","metadatas"])
    for doc, meta in zip(all_items["documents"], all_items["metadatas"]):
        if meta.get("session_id") == session_id:
            print(meta.get("timestamp"), meta.get("session_id"), meta.get("role"), ":", doc)


# ⚠️ QUAN TRỌNG: Cell này phải chạy SAU cell 6 (workflow) và cell 8 (các hàm cũ)
# Import các hàm đã được sửa từ file riêng và override các hàm cũ
from Source.ai.Multi_Agent.Source.Main.Program_Main.chat_functions import (
    run_langgraph_chat_fixed as run_langgraph_chat_fixed_new,
    continue_chat_from_session as continue_chat_from_session_new,
    read_long_term_memory_by_session_id as read_long_term_memory_by_session_id_new
)

# Override các hàm cũ với hàm mới
def run_langgraph_chat_fixed(initial_state=None):
    """Wrapper để gọi hàm mới với app và create_initial_state"""
    return run_langgraph_chat_fixed_new(app, create_initial_state, initial_state=initial_state)

def continue_chat_from_session(session_id: str, user_id: str = "default_user", replay_last_n: int = 20):
    """Wrapper để gọi hàm mới với app và create_initial_state
    Hàm này sẽ sử dụng build_state_from_memory từ memory_helpers.py (hàm continue_chat_from_session_new sẽ tự import)
    """
    # Không cần truyền build_state_from_memory_func vì hàm continue_chat_from_session_new sẽ tự import từ memory_helpers.py
    return continue_chat_from_session_new(session_id, app, create_initial_state, user_id=user_id, replay_last_n=replay_last_n)

def read_long_term_memory_by_session_id(session_id: str):
    """Wrapper để gọi hàm mới"""
    return read_long_term_memory_by_session_id_new(session_id)

print("✅ Đã import và override các hàm với version mới! Hàm cũ trong cell 8 đã bị override.")


continue_chat_from_session(sid)