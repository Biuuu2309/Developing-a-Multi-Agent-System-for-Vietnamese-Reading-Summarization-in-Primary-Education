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
    input_classification: Literal["greeting", "off_topic", "system_question", "text_to_summarize", None]

COORDINATOR_SYSTEM = """Bạn là Coordinator Agent thông minh giúp học sinh tiểu học tóm tắt văn bản theo 2 cách (TRÍCH XUẤT và DIỄN GIẢI) phù hợp với khối lớp (1-5).

Workflow của bạn:
1. GREETING: Chào hỏi và yêu cầu user cung cấp văn bản
2. TEXT_INPUT: Nhận văn bản từ user và chuyển cho OCR/SpellChecker để xử lý
3. SUMMARY_TYPE: Hỏi user muốn tóm tắt TRÍCH XUẤT hay DIỄN GIẢI và khối lớp nào (1-5)
4. PROCESSING: Phân công cho agent phù hợp (Extractor hoặc Abstracter)
5. COMPLETED: Tổng hợp kết quả và hỏi đánh giá hệ thống

QUAN TRỌNG:
- Khi nhận input không liên quan (off_topic): Phản hồi nhẹ nhàng, lịch sự và điều hướng người dùng quay lại nhiệm vụ chính
- Khi nhận lời chào (greeting): Chào lại và nhắc nhở về chức năng của hệ thống
- Khi nhận câu hỏi về hệ thống (system_question): Giải thích ngắn gọn về chức năng

Luôn trả lời ngắn gọn, thân thiện và đi thẳng vào vấn đề."""

def coordinator_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    conversation_stage = state.get("conversation_stage", "greeting")
    
    print(f"🔍 Coordinator Agent - Stage: {conversation_stage}, Messages: {len(messages)}")
    
    # Xử lý trường hợp messages rỗng - GREETING
    if not messages:
        response = AIMessage(content="Xin chào! Tôi là trợ lý tóm tắt thông minh cho học sinh tiểu học.\n\nHãy cung cấp văn bản bạn muốn tóm tắt:")
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
            "final_result": "",
            "input_classification": None
        }
    
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content
        memory.add_message("user", user_input)
        
        print(f"👤 User input: {user_input}")
        print(f"📊 Conversation stage: {conversation_stage}")
        
        # Kiểm tra phân loại input từ InputClassifier
        input_classification = state.get("input_classification")
        
        # Xử lý các trường hợp đặc biệt dựa trên classification
        if input_classification == "greeting":
            response = AIMessage(content="Xin chào! 😊 Tôi là trợ lý tóm tắt thông minh cho học sinh tiểu học.\n\nTôi có thể giúp bạn tóm tắt văn bản theo 2 cách:\n• TRÍCH XUẤT: Giữ nguyên câu từ quan trọng\n• DIỄN GIẢI: Viết lại theo cách hiểu\n\nHãy cung cấp văn bản bạn muốn tóm tắt nhé!")
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
                "final_result": "",
                "input_classification": None
            }
        
        elif input_classification == "off_topic":
            response = AIMessage(content="Xin lỗi, tôi là trợ lý chuyên về tóm tắt văn bản cho học sinh tiểu học. Tôi không thể trả lời câu hỏi này.\n\nTôi có thể giúp bạn:\n• Tóm tắt văn bản theo cách TRÍCH XUẤT\n• Tóm tắt văn bản theo cách DIỄN GIẢI\n\nHãy cung cấp văn bản bạn muốn tóm tắt nhé! 😊")
            memory.add_message("assistant", response.content)
            return {
                "messages": [response],
                "current_agent": "coordinator_agent",
                "needs_user_input": True,
                "conversation_stage": conversation_stage if conversation_stage != "greeting" else "text_input",
                "original_text": state.get("original_text", ""),
                "summary_type": state.get("summary_type", None),
                "grade_level": state.get("grade_level", 0),
                "processed_text": state.get("processed_text", ""),
                "summary_result": state.get("summary_result", ""),
                "final_result": state.get("final_result", ""),
                "input_classification": None
            }
        
        elif input_classification == "system_question":
            response = AIMessage(content="Tôi là trợ lý tóm tắt thông minh cho học sinh tiểu học! 📚\n\n**Chức năng của tôi:**\n• Tóm tắt văn bản theo 2 cách: TRÍCH XUẤT và DIỄN GIẢI\n• Điều chỉnh độ dài và từ vựng phù hợp với khối lớp (1-5)\n\n**Cách sử dụng:**\n1. Cung cấp văn bản bạn muốn tóm tắt\n2. Chọn loại tóm tắt (TRÍCH XUẤT hoặc DIỄN GIẢI)\n3. Chọn khối lớp (1-5)\n4. Nhận kết quả tóm tắt phù hợp\n\nHãy cung cấp văn bản bạn muốn tóm tắt nhé! 😊")
            memory.add_message("assistant", response.content)
            return {
                "messages": [response],
                "current_agent": "coordinator_agent",
                "needs_user_input": True,
                "conversation_stage": conversation_stage if conversation_stage != "greeting" else "text_input",
                "original_text": state.get("original_text", ""),
                "summary_type": state.get("summary_type", None),
                "grade_level": state.get("grade_level", 0),
                "processed_text": state.get("processed_text", ""),
                "summary_result": state.get("summary_result", ""),
                "final_result": state.get("final_result", ""),
                "input_classification": None
            }
        
        # Xử lý theo từng giai đoạn
        if conversation_stage == "text_input":
            # QUAN TRỌNG: Chỉ xử lý nếu đã được phân loại và là văn bản cần tóm tắt
            if input_classification is None:
                # Chưa được phân loại, cần gọi input_classifier trước
                # Trả về state hiện tại để router gọi input_classifier
                return {
                    "messages": [],
                    "current_agent": "input_classifier_agent",
                    "needs_user_input": False,
                    "conversation_stage": "text_input",
                    "original_text": "",
                    "summary_type": None,
                    "grade_level": 0,
                    "processed_text": "",
                    "summary_result": "",
                    "final_result": "",
                    "input_classification": None
                }
            
            # Nếu không phải văn bản cần tóm tắt, đã được xử lý ở trên (greeting, off_topic, system_question)
            if input_classification != "text_to_summarize":
                # Đã xử lý ở trên, không cần làm gì thêm
                return {
                    "messages": [],
                    "current_agent": "coordinator_agent",
                    "needs_user_input": True,
                    "conversation_stage": conversation_stage,
                    "original_text": state.get("original_text", ""),
                    "summary_type": state.get("summary_type", None),
                    "grade_level": state.get("grade_level", 0),
                    "processed_text": state.get("processed_text", ""),
                    "summary_result": state.get("summary_result", ""),
                    "final_result": state.get("final_result", ""),
                    "input_classification": None
                }
            
            # Chỉ xử lý khi input_classification == "text_to_summarize"
            # Lưu văn bản gốc và chuyển sang xử lý OCR/SpellChecker
            response = AIMessage(content="Văn bản đã được nhận! Đang xử lý...")
            memory.add_message("assistant", response.content)
            return {
                "messages": [response],
                "current_agent": "reader_ocr_agent",
                "needs_user_input": False,
                "conversation_stage": "text_input",
                "original_text": user_input,
                "summary_type": None,
                "grade_level": 0,
                "processed_text": "",
                "summary_result": "",
                "final_result": "",
                "input_classification": None
            }
            
        elif conversation_stage == "summary_type":
            # Phân tích yêu cầu về loại tóm tắt và khối lớp
            content = user_input.lower()
            if "trích xuất" in content or "extract" in content or "1" in content:
                summary_type = "extract"
            elif "diễn giải" in content or "abstract" in content or "2" in content:
                summary_type = "abstract"
            else:
                summary_type = "extract"  # Mặc định
            
            # Tìm khối lớp
            grade_level = 3  # Mặc định lớp 3
            for i in range(1, 6):
                if str(i) in content:
                    grade_level = i
                    break
            
            response = AIMessage(content=f"Đã xác nhận: Tóm tắt {summary_type} cho lớp {grade_level}. Đang xử lý...")
            memory.add_message("assistant", response.content)
            
            return {
                "messages": [response],
                "current_agent": "coordinator_agent",
                "needs_user_input": False,
                "conversation_stage": "processing",
                "original_text": state.get("original_text", ""),
                "summary_type": summary_type,
                "grade_level": grade_level,
                "processed_text": state.get("processed_text", ""),
                "summary_result": "",
                "final_result": "",
                "input_classification": None
            }
            
        elif conversation_stage == "completed":
            # Xử lý đánh giá từ user
            if "tốt" in user_input.lower() or "hay" in user_input.lower() or "được" in user_input.lower():
                response = AIMessage(content="Cảm ơn bạn đã đánh giá tích cực! Hệ thống sẽ tiếp tục cải thiện.")
            else:
                response = AIMessage(content="Cảm ơn bạn đã đánh giá! Hệ thống sẽ tiếp tục cải thiện.")
            
            memory.add_message("assistant", response.content)
            return {
                "messages": [response],
                "current_agent": "coordinator_agent",
                "needs_user_input": True,
                "conversation_stage": "greeting",
                "original_text": "",
                "summary_type": None,
                "grade_level": 0,
                "processed_text": "",
                "summary_result": "",
                "final_result": "",
                "input_classification": None
            }
    
    # Xử lý khi nhận kết quả từ Aggregator Agent
    elif conversation_stage == "processing" and state.get("final_result"):
        final_result = state.get("final_result", "")
        response = AIMessage(content=f"🎉 **KẾT QUẢ TÓM TẮT**\n\n{final_result}\n\n---\n\nBạn có hài lòng với bản tóm tắt này không? Hãy đánh giá hệ thống:")
        memory.add_message("assistant", response.content)
        return {
            "messages": [response],
            "current_agent": "coordinator_agent",
            "needs_user_input": True,
            "conversation_stage": "completed",
            "original_text": state.get("original_text", ""),
            "summary_type": state.get("summary_type", None),
            "grade_level": state.get("grade_level", 0),
            "processed_text": state.get("processed_text", ""),
            "summary_result": state.get("summary_result", ""),
            "final_result": final_result,
            "input_classification": None
        }
    
    # Trường hợp không phải HumanMessage
    return {
        "messages": [],
        "current_agent": "coordinator_agent",
        "needs_user_input": True,
        "conversation_stage": conversation_stage,
        "original_text": state.get("original_text", ""),
        "summary_type": state.get("summary_type", None),
        "grade_level": state.get("grade_level", 0),
        "processed_text": state.get("processed_text", ""),
        "summary_result": state.get("summary_result", ""),
        "final_result": state.get("final_result", ""),
        "input_classification": state.get("input_classification", None)
    }
    
coordinator_tool = Tool(
    name="CoordinatorAgent",
    func=coordinator_agent,
    description="Use this to get current coordinator for a given task. Input must be a task name."
)