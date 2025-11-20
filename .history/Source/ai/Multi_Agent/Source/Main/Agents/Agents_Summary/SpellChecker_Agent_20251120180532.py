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

SPELLCHECKER_SYSTEM = """Bạn là Spell Checker Agent chuyên nghiệp. Nhiệm vụ:
1. Kiểm tra và sửa lỗi chính tả trong văn bản
2. KHÔNG thay đổi nội dung, chỉ sửa lỗi chính tả, dấu câu, và các từ sai
3. Trả về văn bản đã được sửa"""

def spellchecker_agent(state: AgentState):
    memory = memory_manager.get_memory()
    processed_text = state.get("processed_text", "")
    
    if not processed_text:
        response = AIMessage(content="Không có văn bản để kiểm tra chính tả.")
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
    
    # Sử dụng LLM để kiểm tra và sửa lỗi chính tả
    context = memory_manager.get_context_summary(include_long_term=True, current_input=processed_text)
    prompt = [
        SystemMessage(content=f"{SPELLCHECKER_SYSTEM}\n\nContext từ memory:\n{context}"),
        HumanMessage(content=f"Hãy kiểm tra và sửa lỗi chính tả, dấu câu trong văn bản sau (KHÔNG thay đổi nội dung, chỉ sửa lỗi):\n\n{processed_text}")
    ]
    
    llm_response = llm.invoke(prompt)
    corrected_text = llm_response.content.strip()
    
    # Nếu LLM trả về quá dài hoặc có format không mong muốn, fallback về văn bản gốc
    if len(corrected_text) > len(processed_text) * 1.5:
        corrected_text = processed_text
    
    response = AIMessage(content=f"✅ Văn bản đã được kiểm tra chính tả!\n\n📝 **Văn bản của bạn:**\n{corrected_text}\n\n---\n\n🔍 **Bây giờ hãy chọn loại tóm tắt và khối lớp:**\n\n1️⃣ **TRÍCH XUẤT** (Extract): Giữ nguyên câu từ quan trọng từ văn bản gốc\n2️⃣ **DIỄN GIẢI** (Abstract): Viết lại theo cách hiểu, diễn đạt lại nội dung\n\n📚 **Khối lớp:** Chọn lớp 1, 2, 3, 4, hoặc 5\n\n💡 **Ví dụ:** \"Tôi muốn tóm tắt theo cách diễn giải cho lớp 5\" hoặc \"Trích xuất cho lớp 3\"")
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],
        "current_agent": "coordinator_agent",
        "needs_user_input": True,
        "conversation_stage": "summary_type",
        "original_text": state.get("original_text", ""),
        "summary_type": None,
        "grade_level": 0,
        "processed_text": corrected_text,
        "summary_result": ""
    }
spellchecker_tool = Tool(
    name="SpellCheckerAgent",
    func=spellchecker_agent,
    description="Use this to check the spelling of a given text. Input must be a text."
)