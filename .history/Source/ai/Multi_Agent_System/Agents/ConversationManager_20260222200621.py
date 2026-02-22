class ConversationManager:
    
    def __init__(
        self,
        intent_agent,
        clarification_agent,
        planning_agent,
        coordinator_agent,
        session_memory
    ):
        self.intent_agent = intent_agent
        self.clarification_agent = clarification_agent
        self.planning_agent = planning_agent
        self.coordinator_agent = coordinator_agent
        self.session_memory = session_memory

    def chat(self, session_id: str, user_input: str):

        print("\n===== NEW MESSAGE =====")
        print("User:", user_input)

        # 1️⃣ Intent
        intent_result = self.intent_agent.classify(user_input)
        print("Intent:", intent_result)

        # 2️⃣ Clarification
        clarification = self.clarification_agent.analyze(
            user_input,
            intent_result
        )

        if clarification["need_clarification"]:
            return clarification["question"]

        # 3️⃣ Planning
        plan = self.planning_agent.plan(intent_result)
        print("Plan:", plan)

        # 4️⃣ Execution
        result_state = self.coordinator_agent.execute(
            plan,
            user_input
        )

        print("Execution state:", result_state)

        # 5️⃣ Trả output chính
        return result_state.get("current_output")