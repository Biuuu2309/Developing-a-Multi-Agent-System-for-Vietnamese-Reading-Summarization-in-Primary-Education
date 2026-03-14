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
        """
        Main chat entry point với Advanced Memory integration
        Trả về output và memory data (semantic_recall, tool_recommendations, knowledge_search)
        """
        # 1️⃣ Lấy history trước khi thêm message mới
        history = self.session_memory.get_history(session_id)
        
        # 2️⃣ Advanced Memory: Semantic recall - tìm similar conversations
        semantic_recall_results = []
        if hasattr(self.session_memory, 'recall_semantic') and self.session_memory.use_advanced_memory:
            try:
                semantic_recall_results = self.session_memory.recall_semantic(user_input, top_k=5)
            except Exception as e:
                print(f"[WARN] Semantic recall failed: {e}")
                semantic_recall_results = []

        # 3️⃣ Tạo graph state với memory context nếu có
        state = {
            "user_input": user_input,
            "history": history
        }
        
        # Thêm similar memories vào context nếu có
        if semantic_recall_results:
            state["similar_memories"] = semantic_recall_results

        # 4️⃣ Gọi LangGraph với tool usage tracking
        import time
        start_time = time.time()
        result = self.graph.invoke(state)
        execution_time = time.time() - start_time

        output = result.get("final_output")
        
        # 5️⃣ Advanced Memory: Get tool recommendations dựa trên intent
        tool_recommendations = []
        intent = result.get("intent", {})
        task_type = None
        if isinstance(intent, dict):
            intent_type = intent.get("intent", "")
            if intent_type == "summarize":
                task_type = "summarization"
            elif intent_type == "image_ocr":
                task_type = "ocr"
            else:
                task_type = intent_type or "general"
        
        if hasattr(self.session_memory, 'get_tool_recommendations') and self.session_memory.use_advanced_memory:
            try:
                tool_recommendations = self.session_memory.get_tool_recommendations(
                    task_type or "general",
                    context={"intent": intent, "session_id": session_id}
                )
            except Exception as e:
                print(f"[WARN] Tool recommendations failed: {e}")
                tool_recommendations = []
        
        # 6️⃣ Advanced Memory: Search knowledge base
        knowledge_search_results = {"facts": [], "relationships": [], "patterns": []}
        if hasattr(self.session_memory, 'search_knowledge') and self.session_memory.use_advanced_memory:
            try:
                # Extract keywords từ user_input để search
                keywords = user_input[:100]  # Lấy 100 ký tự đầu làm query
                knowledge_search_results = self.session_memory.search_knowledge(
                    keywords,
                    limit=10
                )
            except Exception as e:
                print(f"[WARN] Knowledge search failed: {e}")
                knowledge_search_results = {"facts": [], "relationships": [], "patterns": []}
        
        # 7️⃣ Advanced Memory: Record tool usage cho graph execution
        if hasattr(self.session_memory, 'advanced_memory') and self.session_memory.advanced_memory:
            self.session_memory.advanced_memory.record_tool_usage(
                tool_name="mas_graph",
                input_data={"user_input_length": len(user_input), "history_length": len(history)},
                output=output[:200] if output else "",
                success=output is not None and not (isinstance(output, str) and output.startswith("Lỗi")),
                execution_time=execution_time,
                agent_name="mas_system",
                context={"session_id": session_id, "intent": intent}
            )

        # 8️⃣ Lưu memory sau khi graph hoàn thành
        self.session_memory.add_message(session_id, "user", user_input, save_to_long_term=True)
        self.session_memory.add_message(session_id, "assistant", output, save_to_long_term=True)
        
        # 9️⃣ Save session to long-term memory khi kết thúc
        if len(self.session_memory.get_history(session_id)) % 20 == 0:
            self.session_memory.save_session_to_long_term(session_id)

        # 🔟 Trả về output, MAS state và memory data
        return {
            "output": output,
            "mas_state": result,  # Toàn bộ MAS state để Flask API có thể extract intent, plan, evaluation, etc.
            "memory_data": {
                "semantic_recall": semantic_recall_results,
                "tool_recommendations": tool_recommendations,
                "knowledge_search": knowledge_search_results
            }
        }