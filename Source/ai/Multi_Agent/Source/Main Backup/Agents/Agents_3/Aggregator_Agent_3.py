from dotenv import load_dotenv
load_dotenv()

# from langchain_openai import ChatOpenAI # <-- Dòng cũ, comment lại
from langchain_community.chat_models import ChatOllama # <-- Dòng mới
from typing import TypedDict, List, Any, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager

# Khởi tạo model LLM Local từ Ollama
llm = ChatOllama(model="llama3:8b")

class AgentState(TypedDict):
    messages: List[Any]
    current_agent: str
    needs_user_input: bool
    conversation_stage: Literal["greeting", "planning", "booking", "confirmation", "completed"]

AGGREGATOR_SYSTEM = """Bạn là Aggregator Agent. Nhiệm vụ:
1. Tổng hợp ngắn gọn các đề xuất/đầu ra gần nhất từ các agent chuyên trách (travel/hotel/flight)
2. Làm rõ các lựa chọn chính (dưới dạng bullet ngắn), ưu tiên tính mạch lạc
3. Yêu cầu người dùng xác nhận hoặc cung cấp thêm thông tin để tiếp tục
4. Giữ giọng điệu tự nhiên, súc tích
"""

def aggregator_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()

    # Tìm message gần nhất (từ agent khác) để tổng hợp
    last_human = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
    context = memory_manager.get_context_summary(include_long_term=True, current_input=last_human)

    # Lấy tối đa 5 message gần nhất để aggregator tham chiếu
    tail_messages = messages[-5:] if len(messages) > 5 else messages

    prompt = [
        SystemMessage(content=f"{AGGREGATOR_SYSTEM}\n\nContext từ memory:\n{context}"),
        *tail_messages,
        AIMessage(content="Hãy tổng hợp ngắn gọn các ý chính và hỏi người dùng xác nhận."),
    ]

    response = llm.invoke(prompt)
    memory.add_message("assistant", response.content)

    return {
        "messages": messages + [response],
        "current_agent": "coordinator",  # luôn quay lại coordinator
        "needs_user_input": True,
        "conversation_stage": state.get("conversation_stage", "planning"),
    }


