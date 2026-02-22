class ConversationManager:
    
    def __init__(
        self,
        intent_classifier,
        task_planner,
        coordinator,
        session_memory,
        clarification_agent
    ):
        self.intent_classifier = intent_classifier
        self.task_planner = task_planner
        self.coordinator = coordinator
        self.session_memory = session_memory
        self.clarification_agent = clarification_agent
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
        task = self.task_planner.plan(intent_result)
        print("Task:", task)
        # 4️⃣ Execute task
        response = self.coordinator.execute(task, user_input)
        # 5️⃣ Save assistant response
        self.session_memory.add_message(
            session_id, "assistant", response
        )

        return response