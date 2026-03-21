from langchain_community.chat_models import ollama, ChatOllama
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from typing import TypedDict, Annotated, List
import operator
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager

llm = ChatOllama(model="llama3:8b") # <-- Sử dụng model bạn đã kéo về, ví dụ "llama3", "mistral"
prompt = hub.pull("hwchase17/react")

class AgentState(TypedDict):
    # Thông điệp của người dùng
    input: str
    # Đầu ra của từng agent sẽ được nối vào đây
    messages: Annotated[List[str], operator.add]
    
# Tool cho Agent Phân Tích Cảm Xúc
def analyze_sentiment(text: str) -> str:
    """Phân tích cảm xúc của đoạn văn bản. Trả về Positive, Negative hoặc Neutral.

    Tích hợp memory: thêm ngữ cảnh gần đây + long-term và lưu input/output vào memory.
    """
    user_id = "default_user"
    context = memory_manager.get_context_summary(user_id=user_id, include_long_term=True, current_input=text)
    memory_manager.add_message(role="user", content=f"[Tool Input][SentimentAnalyzer] {text}", user_id=user_id)
    prompt = (
        f"{context}\n\n"
        f"Nhiệm vụ: Phân tích cảm xúc của đoạn văn sau, chỉ trả về 1 từ 'Positive', 'Negative' hoặc 'Neutral'.\n"
        f"Đoạn văn: {text}"
    )
    analysis_msg = llm.invoke(prompt)
    analysis = analysis_msg.content.strip()
    memory_manager.add_message(role="tool:SentimentAnalyzer", content=analysis, user_id=user_id)
    return analysis

sentiment_tool = Tool(
    name="SentimentAnalyzer",
    func=analyze_sentiment,
    description="Useful for analyzing the sentiment of a given text. Input should be a string."
)