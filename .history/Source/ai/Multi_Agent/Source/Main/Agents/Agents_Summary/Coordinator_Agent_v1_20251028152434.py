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
    messages: List[Any]
    current_agent: str
    needs_user_input: bool
    conversation_stage: Literal["greeting", "planning", "checking", "processing", "aggregator", "completed"]

COORDINATOR_SYSTEM = """Bạn là Coordinator Agent thông minh giúp học sinh tiểu học tóm tắt văn bản theo 2 cách (TRÍCH XUẤT và DIỄN GIẢI) phù hợp với khối lớp (1-5).
Nhiệm vụ của bạn:
1. Phân tích yêu cầu user về hình thức tóm tắt (TRÍCH XUẤT hoặc DIỄN GIẢI) và khối lớp (1-5). Sau đó chuyển cho agent phù hợp.
2. Agent Reader/OCR: Nhận văn bản từ hình ảnh/PDF và chuyển sang dạng text
3. Agent Spell Checker: Kiểm tra từ viết sai và sửa lại
4. Agent Extractor: Trích xuất thông tin chính từ văn bản
5. Agent Abstracter: Tóm tắt văn bản thành văn bản ngắn gọn
6. Agent Grade Calibrator: Điều chỉnh độ dài và từ vựng phù hợp theo khối lớp
7. Agent Evaluator: Đánh giá chất lượng tóm tắt và đưa ra thang điểm (0-10) dựa trên độ "dễ hiểu"
9. Agent Aggregator: Tổng hợp tóm tắt và đưa ra kết quả cuối cùng
Luôn trả lời tự nhiên. """

def coordinator_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    
    # Xử lý trường hợp messages rỗng
    if not messages:
        response = AIMessage(content="Xin chào! Tôi là trợ lý xưởng tóm tắt thông minh theo khối lớp. Tôi có thể giúp gì cho bạn?")
        memory.add_message("assistant", response.content)
        return {
            "messages": [response],  # Chỉ trả về message mới
            "current_agent": "reader_ocr_agent",
            "needs_user_input": True,
            "conversation_stage": "greeting"
        }
    
    last_message = messages[-1]
    
    if state.get("needs_user_input", False):
        return state
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content
        memory.add_message("user", user_input)
        
        context = memory_manager.get_context_summary(include_long_term=True, current_input=user_input)
        prompt = [
            SystemMessage(content=f"{COORDINATOR_SYSTEM}\n\nContext từ memory:\n{context}"),
            *messages[:-1],
            HumanMessage(content=user_input)
        ]
        
        response = llm.invoke(prompt)
        memory.add_message("assistant", response.content)
        
        # Xác định agent tiếp theo
        content = response.content.lower()
        if any(x in content for x in ["đọc", "nhập", "reader", "ocr", "hình ảnh", "pdf", "văn bản", "file"]):
            next_agent = "reader_ocr_agent"
        elif any(x in content for x in ["trích xuất", "extractor", "extract", "extract_information", "trích", "ý chính", "nội dung chính"]):
            next_agent = "extractor_agent"
        elif any(x in content for x in ["tóm tắt", "tóm tắt ngắn gọn", "viết lại ngắn gọn", "diễn giải", "abstract", "abstracter", "summarize", "summarize_text", "summarize_data"]):
            next_agent = "abstracter_agent"
        elif any(x in content for x in ["điều chỉnh", "calibrate", "grade_calibrator", "chỉnh độ dài", "adjust_length", "adjust_vocabulary", "theo khối lớp"]):
            next_agent = "grade_calibrator_agent"
        elif any(x in content for x in ["đánh giá", "evaluate", "evaluator", "evaluate_summary", "evaluate_quality", "evaluate_understandability"]):
            next_agent = "evaluator_agent"
        elif any(x in content for x in ["điều phối", "orchestrate", "orchestrator", "orchestrate_pipeline", "orchestrate_process", "orchestrate_flow", "xử lý lỗi", "handle_error", "handle_exception", "handle_failure"]):
            next_agent = "orchestrator_agent"
        elif any(x in content for x in ["tổng hợp", "aggregate", "aggregator", "aggregate_summary", "aggregate_result", "aggregate_output", "tổng kết", "tổng hợp kết quả", "tổng hợp ý chính"]):
            next_agent = "aggregator_agent"
        else:
            next_agent = "coordinator_agent"
            
        return {
            "messages": [response],  # Chỉ trả về message mới
            "current_agent": next_agent,
            "needs_user_input": True,
            "conversation_stage": state.get("conversation_stage", "planning")
        }
    
    # Trường hợp không phải HumanMessage
    return {
        "messages": [],  # Không có message mới
        "current_agent": "coordinator_agent",
        "needs_user_input": True,
        "conversation_stage": state.get("conversation_stage", "greeting")
    }
    
coordinator_tool = Tool(
    name="CoordinatorAgent",
    func=coordinator_agent,
    description="Use this to get current coordinator for a given task. Input must be a task name."
)