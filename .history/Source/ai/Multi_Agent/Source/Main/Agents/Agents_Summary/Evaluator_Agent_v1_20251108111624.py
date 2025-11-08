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

EVALUATOR_SYSTEM = """Bạn là Evaluator Agent chuyên nghiệp. Nhiệm vụ:
1. Đánh giá chất lượng bản tóm tắt
2. Đưa ra điểm số từ 0-10 dựa trên độ dễ hiểu
3. Đưa ra nhận xét và gợi ý cải thiện"""

def evaluator_agent(state: AgentState):
    messages = state["messages"]
    memory = memory_manager.get_memory()
    summary_result = state.get("summary_result", "")
    summary_type = state.get("summary_type", "extract")
    grade_level = state.get("grade_level", 3)
    original_text = state.get("original_text", "")
    
    if not summary_result:
        response = AIMessage(content="Không có bản tóm tắt để đánh giá.")
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
    
    context = memory_manager.get_context_summary(include_long_term=True, current_input=summary_result)
    prompt = [
        SystemMessage(content=f"{EVALUATOR_SYSTEM}\n\nContext từ memory:\n{context}\n\nVăn bản gốc:\n{original_text}\n\nBản tóm tắt:\n{summary_result}\n\nLoại: {summary_type}\nKhối lớp: {grade_level}"),
        HumanMessage(content=f"Hãy đánh giá chất lượng bản tóm tắt {summary_type} cho học sinh lớp {grade_level}")
    ]
    
    response = llm.invoke(prompt)
    memory.add_message("assistant", response.content)
    
    return {
        "messages": [response],
        "current_agent": "aggregator_agent",
        "needs_user_input": False,
        "conversation_stage": "processing",
        "original_text": original_text,
        "summary_type": summary_type,
        "grade_level": grade_level,
        "processed_text": state.get("processed_text", ""),
        "summary_result": summary_result
    }
evaluator_tool = Tool(
    name="EvaluatorAgent",
    func=evaluator_agent,
    description="Use this to evaluate a given text. Input must be a text."
)