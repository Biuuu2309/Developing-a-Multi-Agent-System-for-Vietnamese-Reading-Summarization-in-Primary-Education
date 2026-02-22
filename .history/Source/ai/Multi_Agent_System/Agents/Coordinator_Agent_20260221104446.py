from typing import TypedDict, Literal, Optional
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from pathlib import Path
import sys
project_root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Source' / 'ai').exists()), None)
if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from Source.ai.Multi_Agent_System.Memory.memory import MemoryManager
from Source.ai.Multi_Agent_System.Memory.experience_memory import ExperienceMemory

# ==============================
# STATE DEFINITION
# ==============================

class CoordinatorState(TypedDict):
    conversation_stage: Literal[
        "greeting",
        "input",
        "processing",
        "checking",
        "completed"
    ]
    user_input: str
    selected_strategy: Optional[str]
    agent_output: Optional[str]
    confidence: Optional[float]
    final_output: Optional[str]


# ==============================
# COORDINATOR CLASS
# ==============================

class CoordinatorAgent:

    def __init__(self, abstracter_agent, extractor_agent):
        self.llm = ChatOllama(model="qwen2.5:7b")

        self.memory_manager = MemoryManager()
        self.experience_memory = ExperienceMemory()

        self.abstracter = abstracter_agent
        self.extractor = extractor_agent

        self.graph = self._build_graph()

    # ==============================
    # GRAPH BUILDING
    # ==============================

    def _build_graph(self):

        workflow = StateGraph(CoordinatorState)

        workflow.add_node("greeting", self.greeting_stage)
        workflow.add_node("input", self.input_stage)
        workflow.add_node("processing", self.processing_stage)
        workflow.add_node("checking", self.checking_stage)
        workflow.add_node("completed", self.completed_stage)

        workflow.set_entry_point("greeting")

        workflow.add_edge("greeting", "input")
        workflow.add_edge("input", "processing")
        workflow.add_edge("processing", "checking")
        workflow.add_edge("checking", "completed")
        workflow.add_edge("completed", END)

        return workflow.compile()

    # ==============================
    # STAGES
    # ==============================

    def greeting_stage(self, state: CoordinatorState):

        return {
            **state,
            "conversation_stage": "input"
        }

    # ------------------------------

    def input_stage(self, state: CoordinatorState):

        user_input = state["user_input"]

        self.memory_manager.add_message(
            role="user",
            content=user_input
        )

        return {
            **state,
            "conversation_stage": "processing"
        }

    # ------------------------------

    def processing_stage(self, state: CoordinatorState):

        user_input = state["user_input"]

        # 🔎 Retrieve similar experiences
        similar_cases = self.experience_memory.search_similar_experiences(
            user_input,
            top_k=3
        )

        strategy_context = ""
        for case in similar_cases:
            metadata = case.get('metadata', {})
            strategy_context += (
                f"Strategy: {metadata.get('strategy', 'N/A')}, "
                f"Grade: {metadata.get('grade', 'N/A')}, "
                f"Confidence: {metadata.get('confidence', 'N/A')}\n"
            )

        # 🧠 LLM decision
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Bạn có nhiệm vụ là một tác nhân điều phối. Hãy quyết định xem nhiệm vụ cần:\n"
             "- Trích xuất tóm tắt\n"
             "- Diễn giải tóm tắt\n\n"
             "Xem xét các trường hợp trước đó.\n"
             "Trả lời chỉ với một từ: trích xuất hoặc diễn giải."),
            ("human",
             f"Yêu cầu của người dùng:\n{user_input}\n\n"
             f"Trường hợp trước đó:\n{strategy_context}")
        ])

        decision_chain = prompt | self.llm
        decision = decision_chain.invoke({}).content.strip().lower()

        if "extract" in decision:
            strategy = "extractive"
            output = self.extractor.run(user_input)
        else:
            strategy = "abstractive"
            output = self.abstracter.run(user_input)

        return {
            **state,
            "conversation_stage": "checking",
            "selected_strategy": strategy,
            "agent_output": output
        }

    # ------------------------------

    def checking_stage(self, state: CoordinatorState):

        output = state["agent_output"]
        user_input = state["user_input"]

        eval_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Evaluate the quality of the summary.\n"
             "Give a confidence score from 0 to 1.\n"
             "Respond with only a float."),
            ("human",
             f"Original text:\n{user_input}\n\n"
             f"Summary:\n{output}")
        ])

        eval_chain = eval_prompt | self.llm
        confidence_text = eval_chain.invoke({}).content.strip()

        try:
            confidence = float(confidence_text)
        except:
            confidence = 0.5

        # Save experience
        self.experience_memory.add_experience(
            input_text=user_input,
            summary_output=output,
            strategy=state["selected_strategy"],
            grade=int(confidence * 5),
            confidence=confidence
        )

        return {
            **state,
            "conversation_stage": "completed",
            "confidence": confidence,
            "final_output": output
        }

    # ------------------------------

    def completed_stage(self, state: CoordinatorState):

        self.memory_manager.add_message(
            role="assistant",
            content=state["final_output"]
        )

        return state

    # ==============================
    # PUBLIC RUN METHOD
    # ==============================

    def run(self, user_input: str):

        initial_state = {
            "conversation_stage": "greeting",
            "user_input": user_input,
            "selected_strategy": None,
            "agent_output": None,
            "confidence": None,
            "final_output": None
        }

        result = self.graph.invoke(initial_state)

        return result["final_output"]