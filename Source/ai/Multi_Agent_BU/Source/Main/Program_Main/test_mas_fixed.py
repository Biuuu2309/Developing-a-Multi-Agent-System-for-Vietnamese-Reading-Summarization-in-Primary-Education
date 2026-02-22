# Test hệ thống MAS đã được sửa
from pathlib import Path
import sys

project_root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Source' / 'ai').exists()), None)
if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
import operator
from Source.ai.Multi_Agent.Source.Main.Agents.Agents_Summary import Abstracter_Agent, Aggregator_Agent, Coordinator_Agent, Evaluator_Agent, Extractor_Agent, GradeCalibrator_Agent, OCR_Agent, SpellChecker_Agent
from typing import TypedDict, Annotated, List, Any, Literal
from langchain_core.messages import HumanMessage, AIMessage
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager

load_dotenv()

# Định nghĩa AgentState đúng cách
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
        "summary_result": ""
    }

# Hàm điều hướng đơn giản
def decide_next_agent(state: AgentState):
    if state.get("needs_user_input", False):
        return "END"
    return state.get("current_agent", "coordinator_agent")

# Tạo workflow graph mới
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

# Thêm conditional edges
workflow.add_conditional_edges(
    "coordinator_agent",
    decide_next_agent,
    {
        "reader_ocr_agent": "reader_ocr_agent",
        "spellchecker_agent": "spellchecker_agent", 
        "extractor_agent": "extractor_agent",
        "abstracter_agent": "abstracter_agent",
        "grade_calibrator_agent": "grade_calibrator_agent",
        "evaluator_agent": "evaluator_agent",
        "aggregator_agent": "aggregator_agent",
        "coordinator_agent": "coordinator_agent",
        "END": END,
    },
)

# Thêm các edges tuần tự
workflow.add_edge("reader_ocr_agent", "spellchecker_agent")
workflow.add_edge("spellchecker_agent", "extractor_agent")
workflow.add_edge("spellchecker_agent", "abstracter_agent")
workflow.add_edge("extractor_agent", "grade_calibrator_agent")
workflow.add_edge("abstracter_agent", "grade_calibrator_agent")
workflow.add_edge("grade_calibrator_agent", "evaluator_agent")
workflow.add_edge("evaluator_agent", "aggregator_agent")
workflow.add_edge("aggregator_agent", END)

# Compile workflow
app = workflow.compile()

def run_langgraph_chat(initial_state=None):
    print("🤖 Multi-Agent System Summary For Primary School Students")
    print("=" * 60)
    print("Commands: 'exit', 'clear' (STM), 'clear_all' (STM+LTM), 'mem_stats'")

    state = initial_state or create_initial_state()

    # KHÔNG auto-invoke nếu đã có messages (tránh chào lại)
    if not state.get("messages"):
        try:
            print("🚀 Bắt đầu hệ thống...")
            state = app.invoke(state, config={"recursion_limit": 50})
            last = state["messages"][-1] if state["messages"] else None
            if last and isinstance(last, AIMessage):
                print(f"\n🤖{state['current_agent']}: {last.content}")
        except Exception as e:
            print(f"Error: {e}")
            pass

    while True:
        if not state.get("needs_user_input", True):
            try:
                print(f"🔄 Đang xử lý với {state['current_agent']}...")
                state = app.invoke(state, config={"recursion_limit": 50})
                last = state["messages"][-1] if state["messages"] else None
                if last and isinstance(last, AIMessage):
                    print(f"\n🤖{state['current_agent']}: {last.content}")
                mem = memory_manager.get_memory()
                print(f"   [Memory: {len(mem.conversation_history)} msgs, {len(mem.user_preferences)} prefs]")
                continue
            except Exception as e:
                print(f"Error in processing: {e}")
                break

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

        state["messages"].append(HumanMessage(content=user_input))
        print(f"👤: {user_input}")
        state["needs_user_input"] = False

if __name__ == "__main__":
    print("🚀 Bắt đầu test hệ thống MAS đã được sửa...")
    run_langgraph_chat()
