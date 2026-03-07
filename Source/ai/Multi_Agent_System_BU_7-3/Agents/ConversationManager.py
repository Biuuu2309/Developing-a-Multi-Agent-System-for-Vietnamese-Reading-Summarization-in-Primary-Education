# class ConversationManager:
    
#     def __init__(
#         self,
#         intent_classifier,
#         coordinator_agent,
#         session_memory,
#         clarification_agent,
#         planning_agent
#     ):
#         self.intent_classifier = intent_classifier
#         self.coordinator_agent = coordinator_agent
#         self.session_memory = session_memory
#         self.clarification_agent = clarification_agent
#         self.planning_agent = planning_agent
#     # =========================
#     # Session Handling
#     # =========================

#     def create_session(self):
#         return self.session_memory.create_session()

#     # =========================
#     # Main Chat Entry Point
#     # =========================

#     def chat(self, session_id: str, user_input: str):

#         # 1️⃣ Save user message
#         self.session_memory.add_message(
#             session_id, "user", user_input
#         )
#         print("User input:", user_input)

#         # 2️⃣ Classify intent
#         intent_result = self.intent_classifier.classify(user_input)
#         print("Intent result:", intent_result)
        
#         clarification = self.clarification_agent.analyze(
#             user_input,
#             intent_result
#         )

#         if clarification["need_clarification"]:
#             return clarification["question"]
        
#         # 3️⃣ Plan task
#         plan = self.planning_agent.plan(intent_result)
#         print("Plan:", plan)

#         # 4️⃣ Execution
#         result_state = self.coordinator_agent.execute(
#             plan,
#             user_input
#         )

#         print("Execution state:", result_state)

#         # 5️⃣ Hiển thị evaluation nếu có
#         evaluation = result_state.get("evaluation")
#         if evaluation:
#             print("\n=== EVALUATION RESULTS ===")
#             print(f"ROUGE-1 F1: {evaluation.get('rouge1_f1', 'N/A'):.4f}")
#             print(f"ROUGE-L F1: {evaluation.get('rougeL_f1', 'N/A'):.4f}")
#             if "bertscore_f1" in evaluation:
#                 print(f"BERTScore F1: {evaluation.get('bertscore_f1', 'N/A'):.4f}")
#             print(f"Comment: {evaluation.get('comment', 'N/A')}")
#             print("=" * 30 + "\n")

#         # 6️⃣ Trả output chính
#         return result_state.get("current_output")

class ConversationManager:
    
    def __init__(self, graph, session_memory):
        self.graph = graph
        self.session_memory = session_memory

    # =========================
    # Session Handling
    # =========================

    def create_session(self):
        return self.session_memory.create_session()

    # =========================
    # Main Chat Entry Point
    # =========================

    def chat(self, session_id: str, user_input: str):

        # 1️⃣ Lấy history trước khi thêm message mới
        history = self.session_memory.get_history(session_id)
        
        # Advanced Memory: Semantic recall - tìm similar conversations
        if hasattr(self.session_memory, 'recall_semantic'):
            similar_memories = self.session_memory.recall_semantic(user_input, top_k=3)
            # Có thể sử dụng similar_memories để cải thiện context

        # 2️⃣ Tạo graph state
        state = {
            "user_input": user_input,
            "history": history
        }

        # 3️⃣ Gọi LangGraph với tool usage tracking
        import time
        start_time = time.time()
        result = self.graph.invoke(state)
        execution_time = time.time() - start_time

        output = result.get("final_output")
        
        # Advanced Memory: Record tool usage cho graph execution
        if hasattr(self.session_memory, 'advanced_memory') and self.session_memory.advanced_memory:
            self.session_memory.advanced_memory.record_tool_usage(
                tool_name="mas_graph",
                input_data={"user_input_length": len(user_input), "history_length": len(history)},
                output=output[:200] if output else "",
                success=output is not None and not (isinstance(output, str) and output.startswith("Lỗi")),
                execution_time=execution_time,
                agent_name="mas_system",
                context={"session_id": session_id}
            )

        # 4️⃣ Lưu memory sau khi graph hoàn thành
        self.session_memory.add_message(session_id, "user", user_input, save_to_long_term=True)
        self.session_memory.add_message(session_id, "assistant", output, save_to_long_term=True)
        
        # 5️⃣ Save session to long-term memory khi kết thúc
        # (Có thể optimize bằng cách batch save)
        if len(self.session_memory.get_history(session_id)) % 20 == 0:
            self.session_memory.save_session_to_long_term(session_id)

        return output