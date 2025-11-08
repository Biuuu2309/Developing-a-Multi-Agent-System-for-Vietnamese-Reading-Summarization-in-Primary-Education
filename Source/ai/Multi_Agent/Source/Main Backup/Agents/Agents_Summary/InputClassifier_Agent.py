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

INPUT_CLASSIFIER_SYSTEM = """Bạn là Input Classifier Agent thông minh. Nhiệm vụ của bạn là phân loại input từ người dùng thành một trong các loại sau:

1. **greeting**: Lời chào, hỏi thăm (ví dụ: "xin chào", "chào bạn", "bạn khỏe không", "hello", "hi")
2. **off_topic**: Câu hỏi hoặc nội dung KHÔNG liên quan đến tóm tắt văn bản (ví dụ: "thời tiết hôm nay thế nào", "bạn có thể nấu ăn không", "kể chuyện cười", "hôm nay là ngày gì")
3. **system_question**: Câu hỏi về hệ thống, cách sử dụng (ví dụ: "bạn làm gì", "hệ thống này hoạt động thế nào", "cách sử dụng", "bạn có thể làm gì")
4. **text_to_summarize**: Văn bản cần tóm tắt - là đoạn văn bản dài, có nội dung cụ thể, có thể có nhiều câu, đoạn văn (ví dụ: đoạn văn, bài văn, câu chuyện, nội dung bài học)

QUAN TRỌNG:
- Nếu input ngắn (< 20 ký tự) và chỉ là lời chào → "greeting"
- Nếu input là câu hỏi về chức năng hệ thống → "system_question"
- Nếu input là câu hỏi hoặc yêu cầu KHÔNG liên quan đến tóm tắt → "off_topic"
- Nếu input là văn bản dài (> 30 ký tự) hoặc có nhiều câu, có nội dung cụ thể → "text_to_summarize"

Trả về CHỈ một từ: "greeting", "off_topic", "system_question", hoặc "text_to_summarize"
"""

def input_classifier_agent(state: AgentState):
    messages = state["messages"]
    
    # Lấy message cuối cùng từ user
    last_message = messages[-1] if messages else None
    
    if not last_message or not isinstance(last_message, HumanMessage):
        # Không có input từ user, trả về None
        return {
            "messages": [],
            "current_agent": "coordinator_agent",
            "needs_user_input": False,
            "conversation_stage": state.get("conversation_stage", "greeting"),
            "original_text": state.get("original_text", ""),
            "summary_type": state.get("summary_type", None),
            "grade_level": state.get("grade_level", 0),
            "processed_text": state.get("processed_text", ""),
            "summary_result": state.get("summary_result", ""),
            "final_result": state.get("final_result", ""),
            "input_classification": None
        }
    
    user_input = last_message.content.strip()
    
    # Sử dụng LLM để phân loại
    context = memory_manager.get_context_summary(include_long_term=True, current_input=user_input)
    prompt = [
        SystemMessage(content=f"{INPUT_CLASSIFIER_SYSTEM}\n\nContext từ memory:\n{context}"),
        HumanMessage(content=f"Hãy phân loại input sau đây:\n\n\"{user_input}\"\n\nTrả về CHỈ một từ: greeting, off_topic, system_question, hoặc text_to_summarize")
    ]
    
    try:
        response = llm.invoke(prompt)
        classification = response.content.strip().lower()
        
        # Làm sạch kết quả - chỉ lấy từ đầu tiên phù hợp
        if "greeting" in classification:
            classification = "greeting"
        elif "off_topic" in classification or "off-topic" in classification or "offtopic" in classification:
            classification = "off_topic"
        elif "system_question" in classification or "system-question" in classification or "systemquestion" in classification:
            classification = "system_question"
        elif "text_to_summarize" in classification or "text-to-summarize" in classification or "texttosummarize" in classification:
            classification = "text_to_summarize"
        else:
            # Fallback: phân tích thủ công
            user_lower = user_input.lower()
            
            # QUAN TRỌNG: Kiểm tra yêu cầu về tóm tắt trước (có từ "tóm tắt", "diễn giải", "trích xuất", "lớp", "khối")
            # Nếu có original_text (đã có văn bản) và input có từ liên quan đến tóm tắt, đây là summary_type request
            # Không nên phân loại là greeting/off_topic
            has_summary_keywords = any(word in user_lower for word in [
                "tóm tắt", "diễn giải", "trích xuất", "extract", "abstract",
                "lớp 1", "lớp 2", "lớp 3", "lớp 4", "lớp 5",
                "khối 1", "khối 2", "khối 3", "khối 4", "khối 5",
                "lớp", "khối"
            ])
            
            # Nếu có từ liên quan đến tóm tắt và ngắn (< 50 ký tự), có thể là summary request
            # Nhưng nếu đã có original_text, thì đây chắc chắn là summary request
            original_text = state.get("original_text", "")
            if has_summary_keywords and len(user_input) < 50:
                # Nếu đã có văn bản cần tóm tắt, đây là yêu cầu về loại tóm tắt
                # Không phân loại, để coordinator xử lý như summary_type
                if original_text:
                    classification = "off_topic"  # Tạm thời, sẽ được xử lý ở coordinator
                else:
                    # Chưa có văn bản, có thể là greeting hoặc system_question
                    if any(word in user_lower for word in ["chào", "hello", "hi", "xin chào"]):
                        classification = "greeting"
                    else:
                        classification = "system_question"
            # Kiểm tra greeting (ngắn và chỉ là lời chào)
            elif len(user_input) < 30 and any(word in user_lower for word in ["chào", "hello", "hi", "xin chào", "chào bạn", "chào", "hey"]):
                classification = "greeting"
            # Kiểm tra system_question
            elif any(word in user_lower for word in ["bạn làm gì", "hệ thống", "cách sử dụng", "chức năng", "bạn có thể", "bạn là gì", "bạn giúp gì", "làm gì"]):
                classification = "system_question"
            # Kiểm tra câu hỏi (có dấu ? hoặc từ hỏi)
            elif user_input.count("?") > 0 or any(word in user_lower for word in ["là gì", "thế nào", "tại sao", "vì sao", "bao nhiêu", "khi nào", "ở đâu", "ai", "cái gì"]):
                classification = "off_topic"
            # Kiểm tra văn bản dài (có nhiều câu, nhiều dấu chấm)
            elif len(user_input) > 50 and (user_input.count(".") > 1 or user_input.count("!") > 0):
                classification = "text_to_summarize"
            # Kiểm tra văn bản dài không có dấu hỏi
            elif len(user_input) > 30 and user_input.count("?") == 0:
                classification = "text_to_summarize"
            else:
                # Mặc định là off_topic cho các trường hợp khác
                classification = "off_topic"
        
        print(f"🔍 Input Classification: {classification}")
        
    except Exception as e:
        print(f"⚠️ Error in classification: {e}")
        # Fallback classification
        user_lower = user_input.lower()
        if len(user_input) < 30 and any(word in user_lower for word in ["chào", "hello", "hi", "xin chào", "chào bạn"]):
            classification = "greeting"
        elif any(word in user_lower for word in ["bạn làm gì", "hệ thống", "cách sử dụng", "chức năng"]):
            classification = "system_question"
        elif user_input.count("?") > 0 or any(word in user_lower for word in ["là gì", "thế nào", "tại sao"]):
            classification = "off_topic"
        elif len(user_input) > 50:
            classification = "text_to_summarize"
        else:
            classification = "off_topic"
    
    return {
        "messages": [],
        "current_agent": "coordinator_agent",
        "needs_user_input": False,
        "conversation_stage": state.get("conversation_stage", "greeting"),
        "original_text": state.get("original_text", ""),
        "summary_type": state.get("summary_type", None),
        "grade_level": state.get("grade_level", 0),
        "processed_text": state.get("processed_text", ""),
        "summary_result": state.get("summary_result", ""),
        "final_result": state.get("final_result", ""),
        "input_classification": classification
    }

input_classifier_tool = Tool(
    name="InputClassifierAgent",
    func=input_classifier_agent,
    description="Use this to classify user input into greeting, off_topic, system_question, or text_to_summarize. Input must be a user message."
)

