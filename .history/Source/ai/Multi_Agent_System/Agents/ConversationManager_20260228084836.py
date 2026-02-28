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

from mas_main import graph
from session_memory import SessionMemory


class ConversationManager:

    def __init__(self):
        self.memory = SessionMemory()

    def chat(self, session_id: str, user_input: str):

        # 1️⃣ lấy history
        history = self.memory.get_history(session_id)

        # 2️⃣ tạo state cho graph
        state = {
            "user_input": user_input,
            "history": history
        }

        # 3️⃣ gọi LangGraph
        result = graph.invoke(state)

        output = result.get("final_output")

        # 4️⃣ lưu memory
        self.memory.append(session_id, "user", user_input)
        self.memory.append(session_id, "assistant", output)

        return output