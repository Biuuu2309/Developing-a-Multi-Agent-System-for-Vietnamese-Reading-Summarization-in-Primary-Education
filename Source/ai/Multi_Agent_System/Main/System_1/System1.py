import uuid
from pathlib import Path
import sys
project_root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Source' / 'ai').exists()), None)
if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from Source.ai.Multi_Agent_System.Agents.Orchestrator import Orchestrator
from Source.ai.Multi_Agent_System.Agents.Abstracter_Agent import AbstracterAgent
from Source.ai.Multi_Agent_System.Agents.Extractor_Agent import ExtractorAgent
from Source.ai.Multi_Agent_System.Memory.memory import MemoryManager
from Source.ai.Multi_Agent_System.Memory.experience_memory import ExperienceMemory

abstracter = AbstracterAgent(
    model_path="E:\Project_NguyenMinhVu_2211110063\Source\ai\Model Train\Model_DG\vit5_grade_summary"
)

extractor = ExtractorAgent(
    model_path=r"E:\Project_NguyenMinhVu_2211110063\Source\ai\Model Train\Model_TX\vubert_summary_model.pth"
)

orchestrator = Orchestrator(
    abstracter_agent=abstracter,
    extractor_agent=extractor
)

print("MAS Agents initialized successfully.")

# =========================
# CHAT FUNCTION (SYSTEM 1)
# =========================

def chat(user_input: str):
    return orchestrator.run(user_input)


# =========================
# TEST
# =========================

test_text = """
Níc Vu-gic (Nick Vujicic) là một diễn 
giả truyền cảm hứng người Úc, sinh năm 
1982. Khi chào đời, anh không có tứ chi 
mà chỉ có một bàn chân với hai ngón 
chân nhỏ. Sự khác biệt về ngoại hình 
khiến Níc từng bị bạn bè chê cười, trêu 
chọc. Đó là thời kì vô cùng khó khăn, 
Níc Vu-gic đã chấp nhận chung sống 
với sự thiếu sót trên cơ thể mình. Anh học cách dùng chân và một cái cán để 
viết chữ, đánh bàn phím máy vi tính, tự sinh hoạt cá nhân, chăm sóc bản thân. 
Anh đã vượt qua khó khăn, biến bản thân mình thành điều kì diệu trong cuộc 
sống. Níc Vu-gic trở thành biểu tượng mãnh liệt của nghị lực sống và lan toả 
năng lượng tích cực tới người xung quanh.
"""

user_request = f"Hãy tóm tắt diễn giải văn bản sau theo lớp 1:\n{test_text}"

response = chat(user_request)

print("Response:")
print(response)