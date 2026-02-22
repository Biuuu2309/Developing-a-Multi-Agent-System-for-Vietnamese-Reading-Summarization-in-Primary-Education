class ConversationManager:
    
    def __init__(
        self,
        intent_classifier,
        coordinator_agent,
        session_memory,
        clarification_agent,
        planning_agent
    ):
        self.intent_classifier = intent_classifier
        self.coordinator_agent = coordinator_agent
        self.session_memory = session_memory
        self.clarification_agent = clarification_agent
        self.planning_agent = planning_agent
    # =========================
    # Session Handling
    # =========================

    def create_session(self):
        return self.session_memory.create_session()

    # =========================
    # Main Chat Entry Point
    # =========================

    def chat(self, session_id: str, user_input: str):

        # 1️⃣ Save user message
        self.session_memory.add_message(
            session_id, "user", user_input
        )
        print("User input:", user_input)

        # 2️⃣ Classify intent
        intent_result = self.intent_classifier.classify(user_input)
        print("Intent result:", intent_result)
        
        clarification = self.clarification_agent.analyze(
            user_input,
            intent_result
        )

        if clarification["need_clarification"]:
            return clarification["question"]
        
        # 3️⃣ Plan task
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