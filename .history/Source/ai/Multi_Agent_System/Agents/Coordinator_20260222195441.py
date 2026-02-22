from langchain_community.chat_models import ChatOllama
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