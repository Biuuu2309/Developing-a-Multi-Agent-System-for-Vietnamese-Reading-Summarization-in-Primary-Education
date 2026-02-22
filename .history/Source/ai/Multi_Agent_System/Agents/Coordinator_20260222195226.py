from langchain_community.chat_models import ChatOllama

class Coordinator:

    def __init__(
        self,
        system1_engine,
        evaluation_module=None
    ):
        """
        system1_engine: Orchestrator of System 1
        evaluation_module: Optional evaluation component
        """

        self.system1 = system1_engine
        self.evaluator = evaluation_module

        # LLM dùng cho chat / explain
        self.llm = ChatOllama(model="qwen2.5:7b")

    # ==========================================
    # Main Execute Method
    # ==========================================

    def execute(self, task: dict, user_input: str) -> str:

        task_type = task.get("task_type")

        # =========================
        # 1️⃣ Summarization
        # =========================

        if task_type == "summarization":

            strategy = task.get("strategy")
            grade_level = task.get("grade_level")

            return self.system1.run(
                user_input=user_input,
                strategy=strategy,
                grade_level=grade_level
            )

        # =========================
        # 2️⃣ Evaluation
        # =========================

        if task_type == "evaluation":

            if self.evaluator is None:
                return "Evaluation module is not available."

            return self.evaluator.evaluate(user_input)

        # =========================
        # 3️⃣ Explain System
        # =========================

        if task_type == "explain_system":

            prompt = (
                "Giải thích cách hệ thống tóm tắt hoạt động "
                "dựa trên kiến trúc System 1 và System 2."
            )

            return self.llm.invoke(prompt).content

        # =========================
        # 4️⃣ Casual Chat
        # =========================

        if task_type == "casual_chat":

            return self.llm.invoke(user_input).content

        # =========================
        # 5️⃣ Image Analysis
        # =========================

        if task_type == "image_analysis":
            return "Image analysis module is not implemented yet."

        # =========================
        # 6️⃣ Unknown fallback
        # =========================

        return self.llm.invoke(user_input).content

class CoordinatorAgent:
    
    def __init__(
        self,
        system1_engine,
        evaluation_agent=None
    ):
        self.system1_engine = system1_engine
        self.evaluation_agent = evaluation_agent

    def execute(self, plan: dict, user_input: str) -> dict:
        """
        Thực thi pipeline do PlanningAgent sinh ra
        """

        pipeline = plan.get("pipeline", [])
        state = {
            "original_input": user_input,
            "current_output": None,
            "evaluation": None
        }

        for step_config in pipeline:

            step = step_config.get("step")

            if step == "summarize":
                state["current_output"] = self._run_summarization(
                    user_input=state["original_input"],
                    strategy=step_config.get("strategy"),
                    grade_level=step_config.get("grade_level")
                )

            elif step == "evaluate":
                if not self.evaluation_agent:
                    continue

                state["evaluation"] = self.evaluation_agent.evaluate(
                    text=state["original_input"],
                    summary=state["current_output"],
                    metrics=step_config.get("metrics", [])
                )

            elif step == "refine":
                state["current_output"] = self._run_refinement(
                    summary=state["current_output"]
                )

        return state

    def _run_summarization(self, user_input, strategy, grade_level):
        return self.system1_engine.run(
            user_input=user_input,
            strategy=strategy,
            grade_level=grade_level
        )

    def _run_refinement(self, summary):
        """
        Sau này có thể tách thành RefinementAgent
        """
        # Placeholder logic
        return summary