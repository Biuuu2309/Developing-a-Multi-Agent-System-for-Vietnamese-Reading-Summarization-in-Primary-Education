# coordinator.py

from typing import TypedDict, Literal, Optional
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from memory import MemoryManager
from experience_memory import ExperienceMemory


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
        self.llm = ChatOllama(model="qwen3:8b")

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
            strategy_context += (
                f"Strategy: {case['strategy']}, "
                f"Grade: {case['grade']}, "
                f"Confidence: {case['confidence']}\n"
            )

        # 🧠 LLM decision
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a task coordinator.\n"
             "Decide whether the task requires:\n"
             "- extractive summarization\n"
             "- abstractive summarization\n\n"
             "Consider previous similar cases.\n"
             "Respond with ONLY one word: extractive or abstractive."),
            ("human",
             f"User request:\n{user_input}\n\n"
             f"Previous cases:\n{strategy_context}")
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
            summary=output,
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