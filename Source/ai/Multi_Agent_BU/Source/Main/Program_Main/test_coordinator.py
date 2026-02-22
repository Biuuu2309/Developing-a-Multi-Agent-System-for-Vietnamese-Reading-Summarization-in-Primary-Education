# Test trực tiếp các agent
import sys
from pathlib import Path

# Thêm project root vào sys.path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import trực tiếp từ file
sys.path.append(str(Path(__file__).parent.parent / "Agents" / "Agents_Summary"))

from Coordinator_Agent import coordinator_agent
from langchain_core.messages import HumanMessage, AIMessage

print("🚀 Test trực tiếp Coordinator Agent...")

# Tạo state ban đầu
state = {
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

print(f"Initial state: {state}")

# Test greeting
print("\n1. Test greeting:")
try:
    result = coordinator_agent(state)
    print(f"✅ Coordinator response: {result['messages'][-1].content}")
    print(f"Current agent: {result['current_agent']}")
    print(f"Needs user input: {result['needs_user_input']}")
    state = result
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test với user input
print("\n2. Test với user input:")
state["messages"].append(HumanMessage(content="Ngày khai trường đã đến. Sáng sớm, mẹ mới gọi một câu mà tôi đã vùng dậy."))
try:
    result = coordinator_agent(state)
    print(f"✅ Coordinator response: {result['messages'][-1].content}")
    print(f"Current agent: {result['current_agent']}")
    state = result
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test hoàn thành!")
