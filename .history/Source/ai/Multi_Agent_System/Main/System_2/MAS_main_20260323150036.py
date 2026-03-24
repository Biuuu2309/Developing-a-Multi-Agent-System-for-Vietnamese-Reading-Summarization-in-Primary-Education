from typing import TypedDict, Optional, List, Dict
from langgraph.graph import StateGraph, END
from vncorenlp import VnCoreNLP

class MASState(TypedDict):
    user_input: str
    history: List[Dict]
    intent: Optional[dict]
    clarification_needed: Optional[bool]
    clarification_question: Optional[str]
    plan: Optional[dict]
    original_text: Optional[str]
    summary: Optional[str]
    evaluation: Optional[dict]
    final_output: Optional[str]
    plan_revision_count: Optional[int]
    strategy_changed: Optional[bool]
    improvement_count: Optional[int]
    needs_improvement: Optional[bool]
    # Retry theo ràng buộc grade_vocab
    vocab_retry_count: Optional[int]
    vocab_best_ratio: Optional[float]
    vocab_best_summary: Optional[str]
    vocab_best_eval_result: Optional[dict]
    improvement_reason: Optional[str]
    # Image OCR support
    image_path: Optional[str]
    extracted_text: Optional[str]
    # Advanced MAS features
    goal_state: Optional[dict]
    agent_confidences: Optional[dict]
    negotiation_result: Optional[dict]
    agent_memories: Optional[dict]
    
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
from Source.ai.Multi_Agent_System.Agents.Intent_Agent import IntentAgent
from Source.ai.Multi_Agent_System.Agents.Coordinator_Agent import CoordinatorAgent
from Source.ai.Multi_Agent_System.Agents.SessionMemory import SessionMemory
from Source.ai.Multi_Agent_System.Agents.ConversationManager import ConversationManager
from Source.ai.Multi_Agent_System.Agents.Clarification_Agent import ClarificationAgent
from Source.ai.Multi_Agent_System.Agents.Planning_Agent import PlanningAgent
from Source.ai.Multi_Agent_System.Agents.Evaluation_Agent import EvaluationAgent
from Source.ai.Multi_Agent_System.Agents.Image2Text_Agent import Image2TextAgent
# Advanced MAS features
from Source.ai.Multi_Agent_System.Agents.AgentMemory import AgentMemory
from Source.ai.Multi_Agent_System.Agents.GoalState import GoalState, GoalStatus
from Source.ai.Multi_Agent_System.Agents.Confidence import ConfidenceManager
from Source.ai.Multi_Agent_System.Agents.Negotiation import NegotiationAgent

# Initialize agents
intent_agent = IntentAgent()
clarification_agent = ClarificationAgent()
# Planning Agent: "fast" (nhanh, không LLM), "balanced" (planning với LLM), "advanced" (planning + meta-reasoning)
# Mặc định dùng "fast" để nhanh, có thể đổi thành "balanced" hoặc "advanced" khi cần
planning_agent = PlanningAgent(mode="fast")
evaluation_agent = EvaluationAgent()

# Initialize VnCoreNLP annotator (dùng chung cho AbstracterAgent)
annotator = VnCoreNLP(
    r"E:\Project_NguyenMinhVu_2211110063\Source\ai\VnCoreNLP-master\VnCoreNLP-1.1.1.jar",
    annotators="wseg,pos,ner",
    max_heap_size='-Xmx2g'
)

# Initialize Image2Text Agent for OCR (ưu tiên chất lượng và độ đầy đủ)
image2text_agent = Image2TextAgent(
    model="qwen2.5vl:7b-q4_K_M",  # Quantized model
    temperature=0,
    num_ctx=8192,                  # Đủ lớn để không bị cắt text dài
    num_predict=2048                # Đủ lớn để extract toàn bộ nội dung
)

abstracter = AbstracterAgent(
    model_path=r"E:\Project_NguyenMinhVu_2211110063\Source\ai\Model Train\Model_DG_ver2\vit5_grade_summary",
    small_model_path=r"E:\Project_NguyenMinhVu_2211110063\Source\ai\Model Train\Model_DG\vit5_grade_summary",
    annotator=annotator
)

extractor = ExtractorAgent(
    model_path=r"E:\Project_NguyenMinhVu_2211110063\Source\ai\Model Train\Model_TX\vubert_summary_model.pth"
)

system1_engine = Orchestrator(
    abstracter_agent=abstracter,
    extractor_agent=extractor
)

# Initialize Advanced MAS components
goal_state = GoalState()
confidence_manager = ConfidenceManager()
negotiation_agent = NegotiationAgent()

# Initialize agent memories
agent_memories = {
    "intent_agent": AgentMemory("intent_agent"),
    "planning_agent": AgentMemory("planning_agent"),
    "abstracter_agent": AgentMemory("abstracter_agent"),
    "extractor_agent": AgentMemory("extractor_agent"),
    "evaluation_agent": AgentMemory("evaluation_agent"),
    "image2text_agent": AgentMemory("image2text_agent")
}

print("MAS Agents initialized successfully.")
print("Advanced MAS features: Goal State, Confidence, Negotiation, Internal Memory")
print("Image OCR support: Image2Text Agent initialized")

def extract_intent_from_history(history: list) -> dict:
    """
    Extract intent từ history bằng cách tìm các user messages có chứa strategy/grade
    """
    extracted_intent = {}
    
    # Tìm ngược từ cuối history
    for msg in reversed(history):
        if msg.get("role") == "user":
            content = msg.get("content", "").lower()
            
            # Tìm strategy
            if "trích xuất" in content or "extract" in content:
                extracted_intent["summarization_type"] = "extractive"
            elif "diễn giải" in content or "abstract" in content:
                extracted_intent["summarization_type"] = "abstractive"
            
            # Tìm grade_level
            import re
            grade_match = re.search(r'lớp\s*(\d+)', content)
            if grade_match:
                extracted_intent["grade_level"] = int(grade_match.group(1))
            
            # Nếu đã tìm thấy cả strategy và grade_level, dừng lại
            if extracted_intent.get("summarization_type") and extracted_intent.get("grade_level"):
                break
    
    return extracted_intent

def detect_image_path(user_input: str) -> Optional[str]:
    """
    Detect image path từ user input
    Hỗ trợ:
    - Đường dẫn file trực tiếp
    - Từ khóa như "ảnh", "image", "hình" kèm đường dẫn
    """
    import re
    from pathlib import Path
    
    user_input = user_input.strip()
    print(f"[DEBUG detect_image_path] Input: {user_input[:100]}...")
    
    # Pattern 1: Đường dẫn file trực tiếp (có extension ảnh)
    # Hỗ trợ cả absolute path (E:\...) và relative path
    image_extensions = r'\.(jpg|jpeg|png|gif|bmp|webp|tiff|tif)'
    # Pattern cho absolute path: E:\path\to\file.png hoặc E:/path/to/file.png
    # Cho phép khoảng trắng trong path (như "Model Train")
    absolute_path_pattern = rf'([A-Za-z]:[\\/][^\n\r]+{image_extensions})'
    # Pattern cho relative path (không có khoảng trắng)
    relative_path_pattern = rf'([^\s]+{image_extensions})'
    
    # Tìm absolute paths trước
    matches = re.findall(absolute_path_pattern, user_input, re.IGNORECASE)
    print(f"[DEBUG detect_image_path] Absolute path matches: {matches}")
    for match in matches:
        if isinstance(match, tuple):
            match = match[0]
        path = Path(match)
        print(f"[DEBUG detect_image_path] Checking path: {path}, exists: {path.exists()}, is_image: {image2text_agent.is_image_file(str(path)) if path.exists() else False}")
        if path.exists() and image2text_agent.is_image_file(str(path)):
            result = str(path.absolute())
            print(f"[DEBUG detect_image_path] Found absolute path: {result}")
            return result
    
    # Tìm relative paths hoặc paths sau từ khóa
    matches = re.findall(relative_path_pattern, user_input, re.IGNORECASE)
    print(f"[DEBUG detect_image_path] Relative path matches: {matches}")
    for match in matches:
        if isinstance(match, tuple):
            match = match[0]
        # Bỏ qua nếu là URL hoặc không phải path hợp lệ
        if match.startswith('http://') or match.startswith('https://'):
            continue
        path = Path(match)
        print(f"[DEBUG detect_image_path] Checking relative path: {path}, exists: {path.exists()}, is_image: {image2text_agent.is_image_file(str(path)) if path.exists() else False}")
        if path.exists() and image2text_agent.is_image_file(str(path)):
            result = str(path.absolute())
            print(f"[DEBUG detect_image_path] Found relative path: {result}")
            return result
    
    # Pattern 2: Tìm từ khóa "ảnh", "image", "hình" và đường dẫn sau đó
    keywords = ["ảnh", "image", "hình", "picture", "photo", "từ ảnh", "từ hình"]
    for keyword in keywords:
        idx = user_input.lower().find(keyword)
        if idx != -1:
            print(f"[DEBUG detect_image_path] Found keyword '{keyword}' at index {idx}")
            # Tìm đường dẫn sau keyword (có thể có dấu hai chấm)
            after_keyword = user_input[idx + len(keyword):].strip()
            # Loại bỏ dấu hai chấm ở đầu nếu có
            if after_keyword.startswith(':'):
                after_keyword = after_keyword[1:].strip()
            print(f"[DEBUG detect_image_path] After keyword: {after_keyword[:100]}")
            
            # Tìm absolute path (có thể có khoảng trắng)
            path_matches = re.findall(absolute_path_pattern, after_keyword, re.IGNORECASE)
            for match in path_matches:
                if isinstance(match, tuple):
                    match = match[0]
                # Loại bỏ khoảng trắng ở cuối nếu có
                match = match.strip()
                path = Path(match)
                print(f"[DEBUG detect_image_path] Checking path after keyword: {path}, exists: {path.exists()}")
                if path.exists() and image2text_agent.is_image_file(str(path)):
                    result = str(path.absolute())
                    print(f"[DEBUG detect_image_path] Found path after keyword: {result}")
                    return result
            
            # Tìm relative path
            path_matches = re.findall(relative_path_pattern, after_keyword, re.IGNORECASE)
            for match in path_matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match.startswith('http://') or match.startswith('https://'):
                    continue
                path = Path(match)
                print(f"[DEBUG detect_image_path] Checking relative path after keyword: {path}, exists: {path.exists()}")
                if path.exists() and image2text_agent.is_image_file(str(path)):
                    result = str(path.absolute())
                    print(f"[DEBUG detect_image_path] Found relative path after keyword: {result}")
                    return result
    
    print(f"[DEBUG detect_image_path] No image path found")
    return None

def intent_node(state: MASState):
    previous_intent = state.get("intent", {})
    history = state.get("history", [])
    user_input = state["user_input"]
    
    # Advanced Memory: Semantic recall - tìm kiếm similar intents từ memory
    # (Có thể implement sau khi có embedding model tốt hơn)
    
    # Extract intent từ history nếu chưa có trong previous_intent
    history_intent = extract_intent_from_history(history)
    
    # Merge: history_intent -> previous_intent (ưu tiên previous_intent nếu có)
    if previous_intent:
        merged_from_history = {**history_intent, **previous_intent}
    else:
        merged_from_history = history_intent
    
    # Kiểm tra xem đây có phải là câu trả lời cho clarification không
    is_clarification_response = False
    if history:
        last_assistant_msg = None
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                last_assistant_msg = msg.get("content", "")
                break
        if last_assistant_msg and any(keyword in last_assistant_msg.lower() for keyword in 
                                     ["bạn muốn", "vui lòng", "cung cấp", "theo dạng"]):
            is_clarification_response = True
    
    # Classify intent mới từ user input
    new_intent = intent_agent.classify(
        user_input=user_input,
        history=history
    )
    
    # Merge intent: merged_from_history -> new_intent (ưu tiên merged_from_history nếu là clarification response)
    if is_clarification_response:
        # Nếu là clarification response, ưu tiên giữ thông tin từ history/previous
        merged_intent = {**merged_from_history, **new_intent}
        # Đảm bảo giữ lại strategy và grade_level từ history nếu có
        if merged_from_history.get("summarization_type"):
            merged_intent["summarization_type"] = merged_from_history["summarization_type"]
        if merged_from_history.get("grade_level"):
            merged_intent["grade_level"] = merged_from_history["grade_level"]
    else:
        merged_intent = {**merged_from_history, **new_intent}
    
    # Nếu user input là văn bản dài và không có prompt rõ ràng
    is_long_text = len(user_input.strip()) > 100 or len(user_input.split()) > 20
    user_lower = user_input.lower()
    has_explicit_prompt = any(keyword in user_lower[:100] for keyword in 
                              ["hãy tóm tắt", "tóm tắt trích", "tóm tắt diễn"])
    
    # Nếu có strategy từ history và input là văn bản dài không có prompt
    if merged_from_history.get("summarization_type") and is_long_text and not has_explicit_prompt:
        # Giữ strategy từ history
        merged_intent["summarization_type"] = merged_from_history["summarization_type"]
        if merged_from_history.get("grade_level"):
            merged_intent["grade_level"] = merged_from_history["grade_level"]
        # Đảm bảo intent là "summarize" nếu có strategy
        merged_intent["intent"] = "summarize"
    
    # Nếu có strategy từ history và đây là clarification response, đảm bảo intent là "summarize"
    if is_clarification_response and merged_from_history.get("summarization_type"):
        merged_intent["intent"] = "summarize"
    
    # Nếu có strategy nhưng intent không phải "summarize", set lại
    if merged_intent.get("summarization_type") and merged_intent.get("intent") != "summarize":
        merged_intent["intent"] = "summarize"

    # Parse length option cho tóm tắt diễn giải (ngắn / trung bình / dài)
    # Chỉ áp dụng khi intent là summarize và strategy là abstractive
    if merged_intent.get("intent") == "summarize" and merged_intent.get("summarization_type") == "abstractive":
        length_option = merged_intent.get("length_option")
        if not length_option:
            user_lower = user_input.lower()
            if "ngắn" in user_lower:
                merged_intent["length_option"] = "short"
            elif any(kw in user_lower for kw in ["trung bình", "trung-bình", "vừa"]):
                merged_intent["length_option"] = "medium"
            elif "dài" in user_lower:
                merged_intent["length_option"] = "long"
    
    # Detect image path trong user input
    image_path = detect_image_path(user_input)
    print(f"[DEBUG intent_node] image_path detected by detect_image_path(): {image_path}")
    
    # Nếu detect_image_path() không tìm thấy, kiểm tra xem IntentAgent có parse được không
    if not image_path and "image_path" in merged_intent:
        image_path = merged_intent.get("image_path")
        print(f"[DEBUG intent_node] image_path found in merged_intent: {image_path}")
    
    # Nếu vẫn không có, thử extract từ user_input bằng cách tìm pattern đơn giản hơn
    if not image_path:
        import re
        from pathlib import Path
        # Pattern đơn giản hơn: tìm bất kỳ path nào có extension ảnh, kể cả có khoảng trắng
        # Tìm từ dấu hai chấm trở đi
        if ':' in user_input:
            parts = user_input.split(':')
            if len(parts) > 1:
                potential_path = ':'.join(parts[1:]).strip()
                # Loại bỏ các từ khóa ở đầu nếu có
                potential_path = re.sub(r'^(từ\s+)?(ảnh|image|hình)\s*:?\s*', '', potential_path, flags=re.IGNORECASE).strip()
                path = Path(potential_path)
                if path.exists() and image2text_agent.is_image_file(str(path)):
                    image_path = str(path.absolute())
                    print(f"[DEBUG intent_node] image_path extracted from after colon: {image_path}")
    
    if image_path:
        # Nếu có ảnh, parse thêm thông tin từ user_input trước khi return
        user_lower = user_input.lower()
        print(f"[DEBUG intent_node] Parsing info from input with image_path")
        
        # Parse strategy từ user_input nếu chưa có
        if not merged_intent.get("summarization_type"):
            if any(kw in user_lower for kw in ["trích xuất", "extract", "extractive"]):
                merged_intent["summarization_type"] = "extractive"
                print(f"[DEBUG intent_node] Parsed strategy: extractive")
            elif any(kw in user_lower for kw in ["diễn giải", "abstract", "abstractive"]):
                merged_intent["summarization_type"] = "abstractive"
                print(f"[DEBUG intent_node] Parsed strategy: abstractive")
        
        # Parse grade_level từ user_input nếu chưa có
        if not merged_intent.get("grade_level"):
            import re
            grade_match = re.search(r'lớp\s*(\d+)', user_lower)
            if grade_match:
                merged_intent["grade_level"] = int(grade_match.group(1))
                print(f"[DEBUG intent_node] Parsed grade_level: {merged_intent['grade_level']}")
        
        # Kiểm tra xem user có muốn tóm tắt từ ảnh không
        if any(kw in user_lower for kw in ["tóm tắt", "summarize", "từ ảnh", "từ hình"]):
            # Nếu có từ khóa tóm tắt, intent là "summarize" với image_path
            merged_intent["intent"] = "summarize"
            print(f"[DEBUG intent_node] Intent set to: summarize (with image)")
        else:
            # Nếu không có từ khóa tóm tắt, chỉ OCR
            merged_intent["intent"] = "image_ocr"
            print(f"[DEBUG intent_node] Intent set to: image_ocr")
        
        # Loại bỏ image_path khỏi intent dict (sẽ lưu riêng trong state)
        merged_intent_clean = {k: v for k, v in merged_intent.items() if k != "image_path"}
        
        result = {
            "intent": merged_intent_clean,
            "image_path": image_path
        }
        print(f"[DEBUG intent_node] Returning with image_path: {image_path}. Intent: {merged_intent_clean}")
        return result
    
    print(f"[DEBUG intent_node] No image_path. Returning intent: {merged_intent}")
    return {"intent": merged_intent}

def clarification_node(state: MASState):
    intent = state.get("intent", {})
    user_input = state["user_input"]
    history = state.get("history", [])
    image_path = state.get("image_path")  # Kiểm tra image_path từ state
    
    # Nếu không có trong state, kiểm tra trong intent (IntentAgent có thể đã parse)
    if not image_path and "image_path" in intent:
        image_path = intent.get("image_path")
        print(f"[DEBUG clarification_node] image_path found in intent: {image_path}")
    
    print(f"[DEBUG clarification_node] image_path (final): {image_path}")
    print(f"[DEBUG clarification_node] intent: {intent}")
    
    # Nếu có image_path, không cần kiểm tra text (text sẽ được extract từ ảnh)
    if image_path:
        print(f"[DEBUG clarification_node] Image path found, skipping text check")
        # Nếu intent là "summarize" nhưng thiếu thông tin, parse lại từ user_input
        if intent.get("intent") == "summarize":
            user_lower = user_input.lower()
            
            # Parse strategy nếu chưa có
            if not intent.get("summarization_type"):
                if any(kw in user_lower for kw in ["trích xuất", "extract", "extractive"]):
                    intent["summarization_type"] = "extractive"
                    print(f"[DEBUG clarification_node] Parsed strategy: extractive")
                elif any(kw in user_lower for kw in ["diễn giải", "abstract", "abstractive"]):
                    intent["summarization_type"] = "abstractive"
                    print(f"[DEBUG clarification_node] Parsed strategy: abstractive")
            
            # Parse grade_level nếu chưa có và strategy là abstractive
            if intent.get("summarization_type") == "abstractive" and not intent.get("grade_level"):
                import re
                grade_match = re.search(r'lớp\s*(\d+)', user_lower)
                if grade_match:
                    intent["grade_level"] = int(grade_match.group(1))
                    print(f"[DEBUG clarification_node] Parsed grade_level: {intent['grade_level']}")
        
        # Đảm bảo image_path được set vào state nếu chưa có
        result = {
            "clarification_needed": False,
            "intent": intent
        }
        # Nếu image_path có trong intent nhưng chưa có trong state, set vào state
        if image_path and not state.get("image_path"):
            result["image_path"] = image_path
            print(f"[DEBUG clarification_node] Setting image_path to state: {image_path}")
        
        print(f"[DEBUG clarification_node] Returning (no clarification needed): {result}")
        return result
    
    # Kiểm tra xem có strategy từ history không
    history_intent = extract_intent_from_history(history)
    has_strategy_from_history = bool(history_intent.get("summarization_type"))
    
    # Kiểm tra xem input có phải là text dài không
    is_long_text = len(user_input.strip()) > 100 or len(user_input.split()) > 20
    
    # Nếu có strategy từ history và input là text dài, có thể đã đủ thông tin
    if has_strategy_from_history and is_long_text:
        # Kiểm tra xem có text thực sự không (không chỉ là câu trả lời ngắn)
        user_lower = user_input.lower()
        has_strategy_keywords = any(kw in user_lower[:50] for kw in 
                                    ["trích xuất", "diễn giải", "extract", "abstract", "tôi muốn"])
        
        # Nếu không có từ khóa strategy ở đầu và text dài, coi như đã có text
        if not has_strategy_keywords:
            # Đã có đủ thông tin: strategy từ history + text từ input
            # Đảm bảo intent có strategy từ history
            updated_intent = {**intent}
            if history_intent.get("summarization_type"):
                updated_intent["summarization_type"] = history_intent["summarization_type"]
            if history_intent.get("grade_level"):
                updated_intent["grade_level"] = history_intent["grade_level"]
            updated_intent["intent"] = "summarize"
            
            return {
                "clarification_needed": False,
                "intent": updated_intent
            }
    
    # Gọi clarification agent bình thường (truyền history để tìm văn bản đã cung cấp)
    print(f"[DEBUG clarification_node] No image_path, calling clarification_agent.analyze()")
    clarification = clarification_agent.analyze(
        user_input,
        intent,
        history=history
    )
    print(f"[DEBUG clarification_node] Clarification result: {clarification}")

    if clarification["need_clarification"]:
        result = {
            "clarification_needed": True,
            "clarification_question": clarification["question"],
            "final_output": clarification["question"]
        }
        # Cập nhật intent nếu có updated_intent
        if "updated_intent" in clarification:
            result["intent"] = clarification["updated_intent"]
        print(f"[DEBUG clarification_node] Returning (clarification needed): {result}")
        return result

    # Ngay cả khi không cần clarification, vẫn cập nhật intent nếu có thay đổi
    result = {"clarification_needed": False}
    if "updated_intent" in clarification:
        result["intent"] = clarification["updated_intent"]
    print(f"[DEBUG clarification_node] Returning (no clarification needed): {result}")
    return result

def planning_node(state: MASState):
    """Tạo plan động với context và meta-reasoning"""
    intent = state.get("intent", {})
    user_input = state.get("user_input", "")
    history = state.get("history", [])
    previous_plan = state.get("plan")
    previous_evaluation = state.get("evaluation")
    needs_improvement = state.get("needs_improvement", False)
    improvement_count = state.get("improvement_count", 0)
    
    # Advanced MAS: Goal State
    current_goal = goal_state.get_current_goal()
    if not current_goal and intent.get("intent") == "summarize":
        # Tạo goal mới cho summarization task
        goal_id = goal_state.create_goal(
            goal_type="summarization",
            description=f"Tóm tắt văn bản với strategy {intent.get('summarization_type', 'abstractive')}",
            requirements={
                "strategy": intent.get("summarization_type"),
                "grade_level": intent.get("grade_level")
            },
            priority=5
        )
        current_goal = goal_state.get_current_goal()
    
    # Advanced MAS: Retrieve from memory
    planning_memory = agent_memories.get("planning_agent")
    similar_experiences = []
    if planning_memory:
        similar_experiences = planning_memory.retrieve_similar_experiences(
            "planning",
            {"intent": intent, "text_length": len(user_input)}
        )
    
    # Advanced MAS: Negotiation nếu có conflict về strategy
    negotiation_result = None
    if intent.get("summarization_type"):
        # TODO: Hiện tại mới mock đơn giản để lưu vào DB,
        # sau này có thể triển khai thuật toán negotiate thực sự.
        negotiation_result = {
            "initiator": "planning_agent",
            "participants": ["planning_agent", "abstracter_agent", "extractor_agent", "evaluation_agent"],
            "topic": f"strategy_selection::{intent.get('summarization_type')}",
            "proposals": [],
            "responses": [],
            "constraints": [],
            "max_rounds": 1,
            "current_round": 1,
        }
    
    # Xây dựng context cho Planning Agent
    text_length = len(user_input.strip())
    text_preview = user_input[:500] if len(user_input) > 500 else user_input
    
    context = {
        "text_length": text_length,
        "text_preview": text_preview,
        "history": history,
        "previous_plan": previous_plan,
        "previous_evaluation": previous_evaluation,
        "plan_revision_count": state.get("plan_revision_count", 0),
        "improvement_count": improvement_count,
        "goal": current_goal,
        "similar_experiences": similar_experiences
    }
    
    # Nếu đang trong self-improvement loop
    if needs_improvement and previous_evaluation and previous_plan:
        # Nếu retry do vi phạm grade_vocab, giữ nguyên plan để chỉ sinh lại tóm tắt
        if state.get("improvement_reason") == "vocab":
            return {
                "plan": previous_plan,
                "plan_revision_count": state.get("plan_revision_count", 0) + 1,
                "needs_improvement": False,
            }

        rouge_f1 = previous_evaluation.get("rougeL_f1", 1.0)
        bert_f1 = previous_evaluation.get("bertscore_f1", 1.0)
        
        # Tạo plan cải thiện với các điều chỉnh:
        # 1. Thử điều chỉnh grade_level (nếu có)
        # 2. Thêm refine step
        # 3. Có thể thử strategy khác nếu cần
        
        plan = planning_agent.revise_plan(
            previous_plan,
            {
                "needs_refinement": True,
                "improvement_mode": True,
                "low_scores": {"rouge_f1": rouge_f1, "bert_f1": bert_f1}
            },
            previous_evaluation
        )
        
        # Điều chỉnh grade_level nếu có (thử grade thấp hơn để đơn giản hóa)
        for step in plan.get("pipeline", []):
            if step.get("step") == "summarize":
                current_grade = step.get("grade_level")
                if current_grade and current_grade > 1:
                    # Thử grade thấp hơn 1-2 level để đơn giản hóa
                    step["grade_level"] = max(1, current_grade - 1)
                    step["grade_adjusted"] = True
                    step["adjustment_reason"] = f"Điều chỉnh grade từ {current_grade} xuống {step['grade_level']} để cải thiện chất lượng"
        
        return {
            "plan": plan,
            "plan_revision_count": state.get("plan_revision_count", 0) + 1,
            "needs_improvement": False  # Reset flag
        }
    
    # Nếu có evaluation từ lần trước và score thấp, có thể cần revise plan
    if previous_evaluation and previous_plan:
        rouge_f1 = previous_evaluation.get("rougeL_f1", 1.0)
        bert_f1 = previous_evaluation.get("bertscore_f1", 1.0)
        
        # Nếu score thấp và chưa revise quá nhiều lần
        if (rouge_f1 < 0.5 or bert_f1 < 0.6) and state.get("plan_revision_count", 0) < 2:
            # Revise plan với strategy switching
            plan = planning_agent.revise_plan(
                previous_plan,
                {"needs_refinement": True},
                previous_evaluation
            )
            return {
                "plan": plan,
                "plan_revision_count": state.get("plan_revision_count", 0) + 1,
                "strategy_changed": any(
                    step.get("strategy_changed", False) 
                    for step in plan.get("pipeline", [])
                )
            }
    
    # Tạo plan mới với dynamic planning
    plan = planning_agent.plan(intent, context)
    
    # Nếu có image_path, thêm OCR step vào đầu pipeline
    image_path = state.get("image_path")
    if image_path and plan:
        pipeline = plan.get("pipeline", [])
        # Kiểm tra xem đã có OCR step chưa
        has_ocr_step = any(step.get("step") == "ocr" for step in pipeline)
        if not has_ocr_step:
            # Thêm OCR step vào đầu pipeline
            ocr_step = {
                "step": "ocr",
                "image_path": image_path,
                "description": "Trích xuất text từ ảnh"
            }
            pipeline.insert(0, ocr_step)
            plan["pipeline"] = pipeline
    
    # Advanced MAS: Calculate confidence
    planning_confidence = confidence_manager.calculate_confidence(
        agent_name="planning_agent",
        task_type="planning",
        input_data={"intent": intent, "context": context},
        output=plan,
        historical_performance=planning_memory.get_best_strategy("planning") if planning_memory else None
    )
    
    # Advanced MAS: Store experience in memory
    if planning_memory:
        planning_memory.store_experience(
            task_type="planning",
            input_data={"intent": intent, "text_length": text_length},
            output=plan,
            success=True,  # Sẽ được update sau khi evaluate
            context=context
        )
    
    # Advanced MAS: Update goal progress
    if current_goal:
        goal_state.add_subgoal(current_goal["id"], {
            "description": "Tạo execution plan",
            "status": "achieved" if plan else "failed"
        })

    # Advanced MAS: Serialize lightweight agent_memories summary (tránh dump toàn bộ object)
    agent_memories_summary = {
        name: {
            "has_memory": agent_memories[name] is not None
        }
        for name in agent_memories.keys()
    }

    return {
        "plan": plan,
        "agent_confidences": {
            "planning_agent": planning_confidence
        },
        "goal_state": {
            "current_goal_id": current_goal["id"] if current_goal else None,
            "progress": goal_state.get_goal_progress(current_goal["id"]) if current_goal else None
        },
        "negotiation_result": negotiation_result,
        "agent_memories": agent_memories_summary
    }

def ocr_node(state: MASState):
    """
    Extract text từ ảnh sử dụng Image2Text Agent
    """
    image_path = state.get("image_path")
    intent = state.get("intent", {})
    
    if not image_path:
        return {
            "extracted_text": "",
            "final_output": "Lỗi: Không tìm thấy đường dẫn ảnh."
        }
    
    # Advanced MAS: Get agent memory và confidence
    agent_memory = agent_memories.get("image2text_agent")
    
    # Advanced Memory: Tool usage tracking
    import time
    start_time = time.time()
    
    try:
        # Extract text từ ảnh
        ocr_result = image2text_agent.extract_text_from_image(image_path)
        
        execution_time = time.time() - start_time
        
        if ocr_result["success"]:
            extracted_text = ocr_result["text"]
            
            # In ra nội dung text đã extract từ ảnh
            print(f"\n{'='*80}")
            print(f"[IMAGE TO TEXT] Nội dung text được trích xuất từ ảnh:")
            print(f"{'='*80}")
            print(extracted_text)
            print(f"{'='*80}\n")
            
            # Advanced MAS: Calculate confidence
            ocr_confidence = confidence_manager.calculate_confidence(
                agent_name="image2text_agent",
                task_type="ocr",
                input_data={"image_path": image_path},
                output=extracted_text,
                historical_performance=agent_memory.get_best_strategy("ocr") if agent_memory else None
            )
            
            # Advanced MAS: Store experience
            if agent_memory:
                agent_memory.store_experience(
                    task_type="ocr",
                    input_data={"image_path": image_path},
                    output=extracted_text,
                    success=True,
                    context={"text_length": len(extracted_text)}
                )
            
            # Update confidences
            current_confidences = state.get("agent_confidences") or {}
            if not isinstance(current_confidences, dict):
                current_confidences = {}
            current_confidences["image2text_agent"] = ocr_confidence
            
            # Nếu intent là "image_ocr" (chỉ OCR, không tóm tắt), trả về text ngay
            if intent.get("intent") == "image_ocr":
                return {
                    "extracted_text": extracted_text,
                    "original_text": extracted_text,  # Lưu để dùng cho evaluation nếu cần
                    "agent_confidences": current_confidences,
                    "final_output": f"Văn bản được trích xuất từ ảnh:\n\n{extracted_text}"
                }
            
            # Nếu intent là "summarize" với image, extracted_text sẽ được dùng trong summarize_node
            return {
                "extracted_text": extracted_text,
                "original_text": extracted_text,  # Lưu để dùng cho summarize và evaluation
                "agent_confidences": current_confidences
            }
        else:
            # Store failed experience
            if agent_memory:
                agent_memory.store_experience(
                    task_type="ocr",
                    input_data={"image_path": image_path},
                    output=f"Error: {ocr_result.get('error', 'Unknown error')}",
                    success=False
                )
            
            return {
                "extracted_text": "",
                "final_output": f"Lỗi khi trích xuất text từ ảnh: {ocr_result.get('error', 'Unknown error')}"
            }
            
    except Exception as e:
        # Store failed experience
        if agent_memory:
            agent_memory.store_experience(
                task_type="ocr",
                input_data={"image_path": image_path},
                output=f"Error: {str(e)}",
                success=False
            )
        
        return {
            "extracted_text": "",
            "final_output": f"Lỗi khi xử lý ảnh: {str(e)}"
        }

def extract_text_from_input(user_input: str, history: list = None) -> str:
    """
    Extract văn bản thực sự từ user_input hoặc history, loại bỏ các prompt
    """
    import re
    
    user_input_lower = user_input.lower()
    user_input_stripped = user_input.strip()
    
    # Kiểm tra xem có prompt không
    has_prompt = any(keyword in user_input_lower for keyword in [
        "hãy tóm tắt", "tóm tắt", "văn bản sau", "đoạn văn sau", "văn sau"
    ])
    
    # Nếu không có prompt và input dài (> 100 ký tự), có thể toàn bộ là văn bản
    if not has_prompt and len(user_input_stripped) > 100:
        return user_input_stripped
    
    # Nếu input dài (> 200 ký tự) và không có từ khóa strategy/grade ở đầu
    # Có thể đây là văn bản được cung cấp riêng
    if len(user_input_stripped) > 200:
        first_100 = user_input_lower[:100]
        has_strategy_keywords = any(kw in first_100 for kw in ["trích xuất", "diễn giải", "extract", "abstract"])
        if not has_strategy_keywords:
            return user_input_stripped
    
    # Tìm các marker phổ biến: "sau:", "đây:", hoặc dấu hai chấm
    markers = ["sau:", "đây:", "sau", ":"]
    
    for marker in markers:
        if marker in user_input_lower:
            idx = user_input_lower.find(marker)
            if idx != -1:
                text = user_input[idx + len(marker):].strip()
                text = re.sub(r'^(?:hãy\s+)?tóm\s+tắt\s+(?:trích\s+xuất|diễn\s+giải|văn\s+bản)\s*(?:theo\s+lớp\s*\d+)?\s*(?:đoạn\s+văn\s+)?', '', text, flags=re.IGNORECASE).strip()
                if len(text) > 50:
                    return text
    
    # Nếu không tìm thấy marker, tìm phần sau dấu hai chấm cuối cùng
    if ':' in user_input:
        parts = user_input.split(':')
        if len(parts) > 1:
            text = ':'.join(parts[1:]).strip()
            text = re.sub(r'^(?:hãy\s+)?tóm\s+tắt\s+(?:trích\s+xuất|diễn\s+giải|văn\s+bản)\s*(?:theo\s+lớp\s*\d+)?\s*(?:đoạn\s+văn\s+)?', '', text, flags=re.IGNORECASE).strip()
            if len(text) > 50:
                return text
    
    # Nếu không extract được từ current input, tìm trong history
    if history:
        # Tìm các user message có văn bản dài (có thể là text được cung cấp trước đó)
        for msg in reversed(history):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                content_lower = content.lower()
                # Nếu content dài và không phải là câu trả lời ngắn về strategy/grade
                if len(content.strip()) > 100:
                    # Kiểm tra xem có phải là văn bản thực sự không (có nhiều câu, nhiều từ)
                    word_count = len(content.split())
                    sentence_count = content.count('.') + content.count('!') + content.count('?')
                    
                    # Nếu có nhiều từ (> 20) hoặc nhiều câu (> 1) và không có từ khóa strategy ở đầu
                    if (word_count > 20 or sentence_count > 1) and not any(kw in content_lower[:50] for kw in 
                                                                          ["trích xuất", "diễn giải", "extract", "abstract", "tôi muốn"]):
                        # Có thể đây là văn bản được cung cấp
                        return content.strip()
    
    # Fallback: trả về toàn bộ nếu không extract được
    return user_input_stripped

def summarize_node(state: MASState):
    plan = state.get("plan")
    if not plan:
        return {"summary": "Lỗi: Không có kế hoạch thực thi."}
    
    pipeline = plan.get("pipeline", [])
    history = state.get("history", [])

    for step in pipeline:
        # Bỏ qua OCR step (đã được xử lý ở OCR node)
        if step.get("step") == "ocr":
            continue
            
        if step["step"] == "summarize":
            # Ưu tiên sử dụng extracted_text từ OCR nếu có
            if state.get("extracted_text"):
                text_to_summarize = state["extracted_text"]
            else:
                # Extract văn bản thực sự từ user_input hoặc history
                text_to_summarize = extract_text_from_input(
                    state["user_input"], 
                    history=history
                )
            
            # Kiểm tra xem có text để tóm tắt không
            if not text_to_summarize or len(text_to_summarize.strip()) < 20:
                return {
                    "summary": "Lỗi: Không tìm thấy văn bản cần tóm tắt. Vui lòng cung cấp văn bản.",
                    "original_text": text_to_summarize or ""
                }
            
            # Lưu text gốc vào state để dùng cho evaluation
            original_text = text_to_summarize
            
            # Advanced MAS: Get agent memory và confidence
            strategy = step.get("strategy", "abstractive")
            agent_name = f"{strategy}_agent"
            agent_memory = agent_memories.get(agent_name)
            
            # Check confidence trước khi proceed
            agent_confidence = confidence_manager.get_agent_confidence(agent_name)
            if agent_confidence < 0.3:
                # Confidence quá thấp, có thể cần negotiation hoặc fallback
                pass
            
            # Advanced Memory: Tool usage tracking
            import time
            start_time = time.time()
            
            try:
                # Lấy length_option cho abstractive summarization (ngắn / trung bình / dài)
                intent_for_length = state.get("intent", {}) or {}
                length_option = intent_for_length.get("length_option", "medium")

                summary = system1_engine.run(
                    text_to_summarize,
                    strategy=strategy,
                    grade_level=step.get("grade_level"),
                    length_option=length_option
                )
                
                execution_time = time.time() - start_time
                
                # Advanced Memory: Record tool usage (sẽ được record trong ConversationManager)
                # Tool usage tracking được thực hiện ở level cao hơn
                
                # Advanced MAS: Calculate confidence
                summary_confidence = confidence_manager.calculate_confidence(
                    agent_name=agent_name,
                    task_type="summarization",
                    input_data={"text_length": len(text_to_summarize), "strategy": strategy},
                    output=summary,
                    historical_performance=agent_memory.get_best_strategy("summarization") if agent_memory else None
                )
                
                # Advanced MAS: Store experience
                if agent_memory:
                    agent_memory.store_experience(
                        task_type="summarization",
                        input_data={"text_length": len(text_to_summarize), "strategy": strategy},
                        output=summary,
                        success=True,  # Sẽ được update sau khi evaluate
                        context={"grade_level": step.get("grade_level")}
                    )
                
                # Update confidences
                current_confidences = state.get("agent_confidences") or {}
                if not isinstance(current_confidences, dict):
                    current_confidences = {}
                current_confidences[agent_name] = summary_confidence
                
                return {
                    "summary": summary,
                    "original_text": original_text,
                    "agent_confidences": current_confidences
                }
            except Exception as e:
                # Store failed experience
                if agent_memory:
                    agent_memory.store_experience(
                        task_type="summarization",
                        input_data={"text_length": len(text_to_summarize), "strategy": strategy},
                        output=f"Error: {str(e)}",
                        success=False
                    )
                
                return {
                    "summary": f"Lỗi khi tạo tóm tắt: {str(e)}",
                    "original_text": original_text
                }

    return {"summary": "Lỗi: Không tìm thấy bước tóm tắt trong kế hoạch."}

def evaluation_node(state: MASState):
    pipeline = state.get("plan", {}).get("pipeline", [])
    
    # Kiểm tra xem có summary không
    if "summary" not in state or not state.get("summary"):
        return {
            "final_output": "Lỗi: Không thể tạo tóm tắt. Vui lòng thử lại."
        }
    
    # Sử dụng original_text nếu có, nếu không thì dùng user_input
    text_for_eval = state.get("original_text") or state["user_input"]

    for step in pipeline:
        if step["step"] == "evaluate":
            eval_result = evaluation_agent.evaluate(
                text=text_for_eval,
                summary=state["summary"],
                metrics=step.get("metrics", [])
            )
            
            # ==========================================
            # Grade vocab constraint + retry (max 3)
            # ==========================================
            vocab_threshold = 0.8
            chosen_summary = state["summary"]

            needs_improvement = False
            improvement_count = state.get("improvement_count", 0)
            improvement_reason = None

            # Lấy grade_level và strategy từ plan
            grade_level = None
            strategy = None
            for plan_step in pipeline:
                if plan_step.get("step") == "summarize":
                    grade_level = plan_step.get("grade_level")
                    strategy = plan_step.get("strategy", "abstractive")
                    break

            if grade_level is None:
                grade_level = 5
            if strategy is None:
                strategy = "abstractive"

            vocab_check = evaluation_agent.grade_vocab_match_ratio(state["summary"], grade_level)
            vocab_ratio = vocab_check.get("vocab_match_ratio", 0.0)

            eval_result["grade_level"] = grade_level
            eval_result["vocab_match_ratio"] = vocab_ratio
            eval_result["vocab_threshold"] = vocab_threshold
            eval_result["vocab_ok"] = vocab_ratio >= vocab_threshold

            vocab_retry_count = state.get("vocab_retry_count", 0) or 0
            vocab_best_ratio = state.get("vocab_best_ratio", -1.0) or -1.0
            vocab_best_summary = state.get("vocab_best_summary") or state["summary"]
            vocab_best_eval_result = state.get("vocab_best_eval_result")

            if vocab_ratio < vocab_threshold:
                # Cập nhật bản tóm tắt có % vocab cao nhất
                if vocab_ratio > vocab_best_ratio or vocab_best_eval_result is None:
                    vocab_best_ratio = vocab_ratio
                    vocab_best_summary = state["summary"]
                    vocab_best_eval_result = eval_result

                vocab_retry_count = vocab_retry_count + 1

                if vocab_retry_count < 3:
                    needs_improvement = True
                    improvement_reason = "vocab"
                else:
                    # Đủ 3 lần mà vẫn dưới 80% -> lấy bản có % lớn nhất
                    chosen_summary = vocab_best_summary or state["summary"]
                    eval_result = vocab_best_eval_result or eval_result
            else:
                # Nếu đã đạt threshold, vẫn cho phép self-improve theo rouge/bert như cũ
                if strategy == "abstractive" and improvement_count < 2:
                    rouge_f1 = eval_result.get("rougeL_f1", 1.0)
                    bert_f1 = eval_result.get("bertscore_f1", 1.0)

                    # Điều kiện: f1 < 0.6 và rouge_f1 < 0.3
                    if bert_f1 < 0.6 and rouge_f1 < 0.3:
                        needs_improvement = True

                # Update best (để trace nếu cần)
                if vocab_ratio >= vocab_best_ratio:
                    vocab_best_ratio = vocab_ratio
                    vocab_best_summary = state["summary"]
                    vocab_best_eval_result = eval_result
            
            # Advanced MAS: Calculate confidence cho evaluation
            eval_confidence = confidence_manager.calculate_confidence(
                agent_name="evaluation_agent",
                task_type="evaluation",
                input_data={"summary_length": len(state["summary"])},
                output=eval_result,
                metrics=eval_result
            )
            
            # Advanced MAS: Store experience
            eval_memory = agent_memories.get("evaluation_agent")
            if eval_memory:
                eval_memory.store_experience(
                    task_type="evaluation",
                    input_data={"summary_length": len(state["summary"])},
                    output=eval_result,
                    success=not needs_improvement,
                    metrics=eval_result
                )
            
            # Advanced MAS: Update goal achievement
            current_goal = goal_state.get_current_goal()
            if current_goal:
                goal_achieved = goal_state.check_goal_achievement(
                    current_goal["id"],
                    eval_result
                )
                if goal_achieved:
                    goal_state.update_goal_status(
                        current_goal["id"],
                        GoalStatus.ACHIEVED,
                        {"final_metrics": eval_result}
                    )
            
            # Update confidences
            current_confidences = state.get("agent_confidences") or {}
            if not isinstance(current_confidences, dict):
                current_confidences = {}
            current_confidences["evaluation_agent"] = eval_confidence
            
            return {
                "evaluation": eval_result,
                "summary": chosen_summary,
                "needs_improvement": needs_improvement,
                "improvement_count": improvement_count + (1 if needs_improvement else 0),
                "improvement_reason": improvement_reason,
                "vocab_retry_count": vocab_retry_count,
                "vocab_best_ratio": vocab_best_ratio,
                "vocab_best_summary": vocab_best_summary,
                "vocab_best_eval_result": vocab_best_eval_result,
                "agent_confidences": current_confidences,
                "final_output": f"{chosen_summary}\n\nĐánh giá:\n{eval_result}" if not needs_improvement else None
            }

    return {
        "final_output": state.get("summary", "Không có tóm tắt.")
    }
    
builder = StateGraph(MASState)

builder.add_node("intent", intent_node)
builder.add_node("clarification", clarification_node)
builder.add_node("planning", planning_node)
builder.add_node("ocr", ocr_node)
builder.add_node("summarize", summarize_node)
builder.add_node("evaluate", evaluation_node)

builder.set_entry_point("intent")

builder.add_edge("intent", "clarification")

# Conditional routing
def route_after_clarification(state: MASState):
    if state.get("clarification_needed"):
        return END
    return "planning"

builder.add_conditional_edges(
    "clarification",
    route_after_clarification
)

# Conditional routing sau planning: check nếu cần OCR
def route_after_planning(state: MASState):
    plan = state.get("plan", {})
    pipeline = plan.get("pipeline", [])
    # Kiểm tra xem có OCR step không
    has_ocr = any(step.get("step") == "ocr" for step in pipeline)
    if has_ocr:
        return "ocr"
    return "summarize"

builder.add_conditional_edges(
    "planning",
    route_after_planning
)

# Routing sau OCR: check intent
def route_after_ocr(state: MASState):
    intent = state.get("intent", {})
    # Nếu intent là "image_ocr" (chỉ OCR), kết thúc
    if intent.get("intent") == "image_ocr":
        return END
    # Nếu intent là "summarize" với image, tiếp tục summarize
    return "summarize"

builder.add_conditional_edges(
    "ocr",
    route_after_ocr
)

builder.add_edge("summarize", "evaluate")

# Conditional routing sau evaluation: self-improvement loop
def route_after_evaluation(state: MASState):
    if state.get("needs_improvement", False):
        return "planning"
    return END

builder.add_conditional_edges(
    "evaluate",
    route_after_evaluation
)

graph = builder.compile()

def run_mas(user_input: str):
    initial_state = {
        "user_input": user_input
    }

    result = graph.invoke(initial_state)
    return result.get("final_output")

if __name__ == "__main__":
    # Initialize SessionMemory với Advanced Memory (long-term, semantic, tool, knowledge)
    memory = SessionMemory(use_advanced_memory=True, storage_path="memory_storage")
    cm = ConversationManager(graph, memory)

    session_id = cm.create_session()
    print("Session id: ", session_id)
    while True:
        user_input = input("You: ")
        response = cm.chat(session_id, user_input)
        print("You:", user_input)
        print("Bot:", response)