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
    conversation_stage: Literal["greeting", "text_input", "summary_type", "processing", "completed", "evaluation"]
    original_text: str
    summary_type: Literal["extract", "abstract", None]
    grade_level: int
    processed_text: str
    summary_result: str
    final_result: str

AGGREGATOR_SYSTEM = """Bạn là Aggregator Agent chuyên nghiệp. Nhiệm vụ:
1. Tổng hợp các bản tóm tắt cuối cùng từ Extractor Agent và Abstracter Agent, sau đó chọn lọc, tinh chỉnh để được bản tóm tắt cuối cùng có chất lượng cao nhất
2. Tùy vào yêu cầu là tóm tắt TRÍCH XUẤT hay DIỄN GIẢI. Bạn hãy đối chiếu, so sánh các bản tóm tắt cuối cùng với các yêu cầu sau:
    2.1. Tóm tắt TRÍCH XUẤT:
    - Ngắn gọn, càng mạch lạc càng tốt và đảm bảo độ dễ hiểu của văn bản sau tóm tắt
    - Văn bản tóm tắt đầu ra phải đảm bảo ý nghĩa của văn bản gốc
    - Độ liên kết giữa các câu trong văn bản tóm tắt đầu ra phải không cần quá cao, có tính liền mạch, hạn chế bớt sự ngắt quãng
    - Tùy thuộc vào cấp lớp người dùng yêu cầu, văn bản tóm tắt đầu ra phải phù hợp với cấp lớp đó về độ dài. Độ dài có thể tinh chỉnh tăng dần theo từng cấp lớp
    2.2. Tóm tắt DIỄN GIẢI:
    - Ngắn gọn, mạch lạc, dễ hiểu
    - Không thay đổi ý nghĩa của văn bản gốc
    - Có thể thêm bớt từ, câu, đoạn nhưng phải đảm bảo ý nghĩa của văn bản gốc
    - Văn bản tóm tắt đầu ra phải đảm bảo ý nghĩa của văn bản gốc
    - Độ liên kết giữa các câu trong văn bản tóm tắt đầu ra phải cao, có tính liền mạch, không bị ngắt quãng
    - Tùy thuộc vào cấp lớp người dùng yêu cầu, văn bản tóm tắt đầu ra phải phù hợp với cấp lớp đó về từ vựng, cấu trúc câu, ngữ pháp, độ dài, các yếu tố trừu tượng,... Các yếu tố này được phép thêm, bớt, tinh chỉnh tăng dần theo từng cấp lớp
3. Đưa ra kết quả tốt nhất, hoàn chỉnh cho user
4. Đảm bảo chất lượng tóm tắt đầu ra phải cao, không bị lặp lại, không bị ngắt quãng, không bị sai lệch ý nghĩa"""

def aggregator_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    summary_result = state.get("summary_result", "")
    summary_type = state.get("summary_type", "extract")
    grade_level = state.get("grade_level", 3)
    original_text = state.get("original_text", "")
    
    if not summary_result:
        response = AIMessage(content="Không có bản tóm tắt để tổng hợp.")
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
            "summary_result": "",
            "final_result": ""
        }
    
    # Sử dụng LLM để tổng hợp và tinh chỉnh bản tóm tắt cuối cùng
    context = memory_manager.get_context_summary(include_long_term=True, current_input=summary_result)
    prompt = [
        SystemMessage(content=f"{AGGREGATOR_SYSTEM}\n\nContext từ memory:\n{context}\n\nVăn bản gốc:\n{original_text}\n\nBản tóm tắt hiện tại:\n{summary_result}\n\nLoại: {summary_type}\nKhối lớp: {grade_level}"),
        HumanMessage(content=f"Hãy tổng hợp và tinh chỉnh bản tóm tắt {summary_type} cho học sinh lớp {grade_level} để có chất lượng cao nhất")
    ]
    
    llm_response = llm.invoke(prompt)
    refined_summary = llm_response.content
    
    # Tạo bản tóm tắt cuối cùng với format đẹp
    summary_type_vn = "TRÍCH XUẤT" if summary_type == "extract" else "DIỄN GIẢI"
    final_summary = f"""📝 **BẢN TÓM TẮT CUỐI CÙNG**

**Loại tóm tắt:** {summary_type_vn}
**Khối lớp:** {grade_level}

**Nội dung:**
{refined_summary}

---

Bản tóm tắt đã hoàn thành! Bạn có hài lòng với kết quả này không? Hãy đánh giá hệ thống từ 1-10 điểm."""
    
    response = AIMessage(content=final_summary)
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],
        "current_agent": "coordinator_agent",
        "needs_user_input": False,  # Không cần user input, sẽ chuyển về coordinator
        "conversation_stage": "processing",
        "original_text": original_text,
        "summary_type": summary_type,
        "grade_level": grade_level,
        "processed_text": state.get("processed_text", ""),
        "summary_result": summary_result,
        "final_result": final_summary  # Truyền kết quả cuối cùng
    }
aggregator_tool = Tool(
    name="AggregatorAgent",
    func=aggregator_agent,
    description="Use this to aggregate a given text. Input must be a text."
)