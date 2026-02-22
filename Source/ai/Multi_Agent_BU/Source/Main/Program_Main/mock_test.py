# Test đơn giản không cần dependencies
from typing import TypedDict, Annotated, List, Any, Literal
import operator

# Mock AIMessage và HumanMessage
class MockMessage:
    def __init__(self, content, role=None):
        self.content = content
        self.role = role

class MockAIMessage(MockMessage):
    def __init__(self, content):
        super().__init__(content, "assistant")

class MockHumanMessage(MockMessage):
    def __init__(self, content):
        super().__init__(content, "user")

# Mock memory manager
class MockMemoryManager:
    def __init__(self):
        self.messages = []
    
    def get_memory(self):
        return self
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        print(f"💾 Memory: {role} - {content[:50]}...")

# Mock LLM
class MockLLM:
    def invoke(self, prompt):
        return MockAIMessage("Mock response from LLM")

# Định nghĩa AgentState
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

# Mock coordinator agent
def mock_coordinator_agent(state: AgentState):
    messages = state["messages"]
    conversation_stage = state.get("conversation_stage", "greeting")
    
    print(f"🔍 Coordinator Agent - Stage: {conversation_stage}, Messages: {len(messages)}")
    
    # Xử lý trường hợp messages rỗng - GREETING
    if not messages:
        response = MockAIMessage("Xin chào! Tôi là trợ lý tóm tắt thông minh cho học sinh tiểu học.\n\nHãy cung cấp văn bản bạn muốn tóm tắt:")
        memory_manager.add_message("assistant", response.content)
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
    
    if isinstance(last_message, MockHumanMessage):
        user_input = last_message.content
        memory_manager.add_message("user", user_input)
        
        print(f"👤 User input: {user_input}")
        print(f"📊 Conversation stage: {conversation_stage}")
        
        # Xử lý theo từng giai đoạn
        if conversation_stage == "text_input":
            # Lưu văn bản gốc và chuyển sang xử lý OCR/SpellChecker
            response = MockAIMessage("Văn bản đã được nhận! Đang xử lý...")
            memory_manager.add_message("assistant", response.content)
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

# Khởi tạo mock objects
memory_manager = MockMemoryManager()

def test_workflow():
    print("🚀 Test workflow đơn giản...")
    
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
        result = mock_coordinator_agent(state)
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
    state["messages"].append(MockHumanMessage(content="Ngày khai trường đã đến. Sáng sớm, mẹ mới gọi một câu mà tôi đã vùng dậy."))
    try:
        result = mock_coordinator_agent(state)
        print(f"✅ Coordinator response: {result['messages'][-1].content}")
        print(f"Current agent: {result['current_agent']}")
        state = result
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test hoàn thành!")
    print(f"📊 Total messages in memory: {len(memory_manager.messages)}")

if __name__ == "__main__":
    test_workflow()
