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
        self.llm = ChatOllama(model="qwen3:8b")

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