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
from Source.ai.Multi_Agent.Source.Main.Agents.Agents_Summary import Abstracter_Agent, Aggregator_Agent, Coordinator_Agent, Evaluator_Agent, Extractor_Agent, GradeCalibrator_Agent, OCR_Agent, SpellChecker_Agent
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

load_dotenv()

llm = ChatOllama(model="llama3:8b") 

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
        "current_agent": "coordinator",
        "needs_user_input": False,
        "conversation_stage": "greeting",
    }
state = create_initial_state()
try:
    state = app.invoke(state, config={"recursion_limit": 20})
except Exception:
    pass

print("Nodes wired: aggregator added between specialist agents and coordinator.")


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
        "final_result": ""
    }

# Hàm điều hướng thông minh cho coordinator
def coordinator_router(state: AgentState):
    stage = state.get("conversation_stage", "greeting")
    needs_input = state.get("needs_user_input", False)
    
    if needs_input:
        return "END"  # Chờ user input
    
    if stage == "greeting":
        return "coordinator_agent"
    elif stage == "text_input":
        return "reader_ocr_agent"  # Bắt đầu xử lý văn bản
    elif stage == "summary_type":
        return "coordinator_agent"  # Chờ user chọn loại tóm tắt
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
workflow.add_node("reader_ocr_agent", OCR_Agent.ocr_agent)
workflow.add_node("spellchecker_agent", SpellChecker_Agent.spellchecker_agent)
workflow.add_node("extractor_agent", Extractor_Agent.extractor_agent)
workflow.add_node("abstracter_agent", Abstracter_Agent.abstracter_agent)
workflow.add_node("grade_calibrator_agent", GradeCalibrator_Agent.grade_calibrator_agent)
workflow.add_node("evaluator_agent", Evaluator_Agent.evaluator_agent)
workflow.add_node("aggregator_agent", Aggregator_Agent.aggregator_agent)

# Set entry point
workflow.set_entry_point("coordinator_agent")

# Workflow mới: Coordinator -> OCR -> SpellChecker -> Coordinator -> Extractor/Abstracter -> GradeCalibrator -> Evaluator -> Aggregator -> Coordinator
workflow.add_conditional_edges("coordinator_agent", coordinator_router, {
    "coordinator_agent": "coordinator_agent",
    "reader_ocr_agent": "reader_ocr_agent",
    "extractor_agent": "extractor_agent", 
    "abstracter_agent": "abstracter_agent",
    "END": END
})

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


def read_long_term_memory_by_session_id(session_id: str):
    col = long_term_memory.collection
    all_items = col.get(include=["documents","metadatas"])
    for doc, meta in zip(all_items["documents"], all_items["metadatas"]):
        if meta.get("session_id") == session_id:
            print(meta.get("timestamp"), meta.get("session_id"), meta.get("role"), ":", doc)


# Hàm run_langgraph_chat đã được sửa để xử lý đúng workflow với tích hợp memory
def run_langgraph_chat_fixed(initial_state=None):
    print("🤖 Multi-Agent System Summary For Primary School Students")
    print("=" * 60)
    print("Commands: 'exit', 'clear' (STM), 'clear_all' (STM+LTM), 'mem_stats'")

    state = initial_state or create_initial_state()

    # KHÔNG auto-invoke nếu đã có messages (tránh chào lại)
    if not state.get("messages"):
        try:
            state = app.invoke(state, config={"recursion_limit": 50})
            last = state["messages"][-1] if state["messages"] else None
            if last and isinstance(last, AIMessage):
                print(f"\n🤖{state['current_agent']}: {last.content}")
        except Exception as e:
            print(f"Error: {e}")
            pass

    while True:
        # Kiểm tra nếu cần user input
        if state.get("needs_user_input", False):
            user_input = input("\n👤 Bạn: ").strip()
            memory_manager.add_message("user", user_input)

            if user_input.lower() in ["exit", "quit", "thoát"]:
                print("👋 Bye MAS Lịch sử chat đã được lưu.")
                break
            if user_input.lower() in ["clear", "xóa", "reset"]:
                memory_manager.clear_memory()
                state = create_initial_state()
                print("🧹 Đã xóa short-term memory. Long-term vẫn giữ.")
                continue
            if user_input.lower() in ["clear_all", "xóa_all", "reset_all"]:
                memory_manager.clear_memory(also_long_term=True)
                state = create_initial_state()
                print("🧹 Đã xóa cả short-term và long-term memory.")
                continue
            if user_input.lower() in ["mem_stats", "memory_stats"]:
                print(f"📊 Long-term Memory: {long_term_memory.collection.count()} items")
                continue

            # Thêm user input vào state và tiếp tục xử lý
            state["messages"].append(HumanMessage(content=user_input))
            print(f"👤: {user_input}")
            state["needs_user_input"] = False

        # Xử lý workflow
        try:
            state = app.invoke(state, config={"recursion_limit": 50})
            last = state["messages"][-1] if state["messages"] else None
            if last and isinstance(last, AIMessage):
                print(f"\n🤖{state['current_agent']}: {last.content}")
            
            mem = memory_manager.get_memory()
            print(f"   [Memory: {len(mem.conversation_history)} msgs, {len(mem.user_preferences)} prefs]")
            
        except Exception as e:
            print(f"Error in processing: {e}")
            break

def build_state_from_memory(user_id: str = "default_user", max_messages: int = 10):
    mem = memory_manager.get_memory(user_id)
    msgs = []
    ctrl = {"thoát","exit","quit","xóa","clear","reset","clear_all","xóa_all","reset_all"}
    for m in mem.conversation_history[-max_messages:]:
        content = (m.get("content") or "").strip()
        if content.lower() in ctrl:
            continue
        role = (m.get("role") or "").lower()
        if role == "user":
            msgs.append(HumanMessage(content=content))
        else:
            msgs.append(AIMessage(content=content))
    needs_user_input = True if msgs and isinstance(msgs[-1], AIMessage) else False
    return {
        "messages": msgs,
        "current_agent": "coordinator_agent",
        "needs_user_input": needs_user_input,
        "conversation_stage": "greeting",
        "original_text": "",
        "summary_type": None,
        "grade_level": 0,
        "processed_text": "",
        "summary_result": "",
        "final_result": ""
    }

def continue_chat_from_session(session_id: str, user_id: str = "default_user", replay_last_n: int = 20):
    print("Previous chat history:")
    read_long_term_memory_by_session_id(session_id)
    loaded = memory_manager.resume_session(session_id, user_id=user_id, replay_last_n=replay_last_n)
    print(f"Resumed {loaded} messages from long-term: {session_id}")
    initial_state = build_state_from_memory(user_id=user_id, max_messages=replay_last_n)
    run_langgraph_chat_fixed(initial_state=initial_state)

# Test workflow mới
print("✅ Hàm run_langgraph_chat_fixed đã được tích hợp với memory functions!")


continue_chat_from_session(session_ids)

read_long_term_memory_by_session_id(session_ids)