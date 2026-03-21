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

OCR_SYSTEM = """Bạn là OCR Agent chuyên nghiệp. Nhiệm vụ:
1. Nhận văn bản từ user và chuyển thành dạng text chuẩn
2. Trả về văn bản đã được xử lý
3. Luôn trả lời ngắn gọn và đi thẳng vào vấn đề"""

def ocr_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    original_text = state.get("original_text", "")
    
    if not original_text:
        response = AIMessage(content="Không có văn bản để xử lý.")
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
            "summary_result": ""
        }
    
    # Sử dụng LLM để xử lý và chuẩn hóa văn bản
    context = memory_manager.get_context_summary(include_long_term=True, current_input=original_text)
    prompt = [
        SystemMessage(content=f"{OCR_SYSTEM}\n\nContext từ memory:\n{context}"),
        HumanMessage(content=f"Hãy xử lý và chuẩn hóa văn bản sau thành dạng text chuẩn:\n\n{original_text}")
    ]
    
    llm_response = llm.invoke(prompt)
    processed_text = llm_response.content.strip()
    
    # Nếu LLM trả về quá dài hoặc có format không mong muốn, fallback về xử lý đơn giản
    if len(processed_text) > len(original_text) * 2:
        processed_text = original_text.strip()
    
    response = AIMessage(content=f"✅ Văn bản đã được xử lý!\n\n📝 **Văn bản của bạn:**\n{processed_text}\n\n---\n\n🔍 **Bây giờ hãy chọn loại tóm tắt và khối lớp:**\n\n1️⃣ **TRÍCH XUẤT** (Extract): Giữ nguyên câu từ quan trọng từ văn bản gốc\n2️⃣ **DIỄN GIẢI** (Abstract): Viết lại theo cách hiểu, diễn đạt lại nội dung\n\n📚 **Khối lớp:** Chọn lớp 1, 2, 3, 4, hoặc 5\n\n💡 **Ví dụ:** \"Tôi muốn tóm tắt theo cách diễn giải cho lớp 5\" hoặc \"Trích xuất cho lớp 3\"")
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],
        "current_agent": "coordinator_agent",
        "needs_user_input": True,
        "conversation_stage": "summary_type",
        "original_text": original_text,
        "summary_type": None,
        "grade_level": 0,
        "processed_text": processed_text,
        "summary_result": ""
    }
ocr_tool = Tool(
    name="OCRAgent",
    func=ocr_agent,
    description="Use this to OCR a given image. Input must be a image."
)