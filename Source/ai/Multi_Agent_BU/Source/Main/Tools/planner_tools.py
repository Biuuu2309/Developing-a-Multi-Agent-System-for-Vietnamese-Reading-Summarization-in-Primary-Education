from langchain_community.chat_models import ChatOllama
from langchain.tools import Tool
from langchain import hub
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager

llm = ChatOllama(model="llama3:8b")
prompt = hub.pull("hwchase17/react")

def planner(plan_input: str) -> str:
    """Sinh kế hoạch gồm: subgoals, steps, assumptions/risks, self-critique, reflection.

    Lưu input/output vào memory (short + long term)."""
    user_id = "default_user"
    memory_manager.add_message(role="user", content=f"[Tool Input][Planner] {plan_input}", user_id=user_id)

    system_directives = (
        "Bạn là Planner. Hãy thực hiện:")
    instructions = (
        "1) Subgoal decomposition (gạch đầu dòng)\n"
        "2) Action steps (tuần tự)\n"
        "3) Assumptions & Risks (ngắn gọn)\n"
        "4) Self-critique (tự phê bình những điểm có thể sai)\n"
        "5) Reflection (điều chỉnh/ưu tiên lại nếu cần)\n"
        "Đầu ra ngắn gọn, rõ ràng."
    )

    full_prompt = (
        f"{system_directives}\n{instructions}\n\n"
        f"Nhiệm vụ/đề bài: {plan_input}\n"
    )

    resp = llm.invoke(full_prompt)
    plan_text = resp.content.strip()
    memory_manager.add_message(role="tool:Planner", content=plan_text, user_id=user_id)
    return plan_text

planner_tool = Tool(
    name="Planner",
    func=planner,
    description="Create a structured plan: subgoals, steps, assumptions/risks, self-critique, reflection."
)


