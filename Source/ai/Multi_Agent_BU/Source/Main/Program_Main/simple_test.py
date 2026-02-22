# Test hệ thống MAS đơn giản
import sys
from pathlib import Path

# Thêm project root vào sys.path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import TypedDict, Annotated, List, Any, Literal
import operator

# Định nghĩa AgentState đơn giản
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

# Mock các agent functions
def mock_coordinator_agent(state: AgentState):
    messages = state["messages"]
    conversation_stage = state.get("conversation_stage", "greeting")
    
    print(f"🔍 Coordinator Agent - Stage: {conversation_stage}, Messages: {len(messages)}")
    
    if not messages:
        response = {"content": "Xin chào! Tôi là trợ lý tóm tắt thông minh cho học sinh tiểu học.\n\nHãy cung cấp văn bản bạn muốn tóm tắt:"}
        return {
            "messages": [response],
            "current_agent": "coordinator_agent",
            "needs_user_input": True,
            "conversation_stage": "text_input",
            "original_text": "",
            "summary_type": None,
            "grade_level": 0,
            "processed_text": "",
            "summary_result": ""
        }
    
    last_message = messages[-1]
    
    if isinstance(last_message, dict) and last_message.get("role") == "user":
        user_input = last_message["content"]
        print(f"👤 User input: {user_input}")
        print(f"📊 Conversation stage: {conversation_stage}")
        
        if conversation_stage == "text_input":
            response = {"content": "Văn bản đã được nhận! Đang xử lý..."}
            return {
                "messages": [response],
                "current_agent": "reader_ocr_agent",
                "needs_user_input": False,
                "conversation_stage": "text_input",
                "original_text": user_input,
                "summary_type": None,
                "grade_level": 0,
                "processed_text": "",
                "summary_result": ""
            }
    
    return state

def mock_ocr_agent(state: AgentState):
    print("🔍 OCR Agent processing...")
    processed_text = state.get("original_text", "")
    response = {"content": f"Văn bản đã được xử lý:\n\n{processed_text}\n\nBây giờ hãy chọn loại tóm tắt:\n1. TRÍCH XUẤT (Extract): Giữ nguyên câu từ quan trọng\n2. DIỄN GIẢI (Abstract): Viết lại theo cách hiểu của bạn\n\nVà cho biết khối lớp (1-5):"}
    
    return {
        "messages": [response],
        "current_agent": "coordinator_agent",
        "needs_user_input": True,
        "conversation_stage": "summary_type",
        "original_text": state.get("original_text", ""),
        "summary_type": None,
        "grade_level": 0,
        "processed_text": processed_text,
        "summary_result": ""
    }

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

def test_workflow():
    print("🚀 Bắt đầu test workflow đơn giản...")
    
    state = create_initial_state()
    
    # Test greeting
    print("\n1. Test greeting:")
    state = mock_coordinator_agent(state)
    print(f"Response: {state['messages'][-1]['content']}")
    print(f"Needs user input: {state['needs_user_input']}")
    
    # Test user input
    print("\n2. Test user input:")
    state["messages"].append({"role": "user", "content": "Ngày khai trường đã đến. Sáng sớm, mẹ mới gọi một câu mà tôi đã vùng dậy."})
    state = mock_coordinator_agent(state)
    print(f"Response: {state['messages'][-1]['content']}")
    print(f"Current agent: {state['current_agent']}")
    
    # Test OCR processing
    print("\n3. Test OCR processing:")
    state = mock_ocr_agent(state)
    print(f"Response: {state['messages'][-1]['content']}")
    print(f"Needs user input: {state['needs_user_input']}")
    
    print("\n✅ Test workflow hoàn thành!")

if __name__ == "__main__":
    test_workflow()
