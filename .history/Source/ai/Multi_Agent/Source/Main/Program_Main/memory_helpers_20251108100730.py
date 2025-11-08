from langchain_core.messages import HumanMessage, AIMessage
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager

def build_state_from_memory(user_id: str = "default_user", max_messages: int = 10):
    """Build state from memory with proper conversation_stage detection"""
    mem = memory_manager.get_memory(user_id)
    msgs = []
    ctrl = {"thoát","exit","quit","xóa","clear","reset","clear_all","xóa_all","reset_all"}
    
    # Xác định conversation_stage và các thông tin từ lịch sử
    conversation_stage = None  # Không set mặc định, sẽ xác định từ lịch sử
    original_text = ""
    processed_text = ""
    summary_type = None
    grade_level = 0
    
    # Đi ngược từ cuối lên để tìm thông tin mới nhất
    for m in reversed(mem.conversation_history[-max_messages:]):
        content = (m.get("content") or "").strip()
        if content.lower() in ctrl:
            continue
        role = (m.get("role") or "").lower()
        
        if role == "user":
            # Xử lý user messages - tìm văn bản cần tóm tắt
            content_lower_user = content.lower()
            # Nếu có prefix "văn bản của tôi:" hoặc "văn bản:", extract phần sau
            if "văn bản của tôi:" in content_lower_user:
                # Tách phần văn bản sau prefix (sử dụng "văn bản của tôi:" làm delimiter)
                idx = content_lower_user.find("văn bản của tôi:")
                if idx >= 0:
                    text_part = content[idx + len("văn bản của tôi:"):].strip()
                    if len(text_part) > 30:  # Đảm bảo là văn bản thực sự
                        if not original_text:  # Lấy văn bản đầu tiên tìm thấy (từ cuối lên)
                            original_text = text_part
                            print(f"   🔍 Extracted original_text từ user message (prefix 'văn bản của tôi:'): {len(original_text)} chars")
            elif "văn bản:" in content_lower_user:
                # Tách phần văn bản sau prefix "văn bản:"
                idx = content_lower_user.find("văn bản:")
                if idx >= 0:
                    text_part = content[idx + len("văn bản:"):].strip()
                    if len(text_part) > 30:
                        if not original_text:
                            original_text = text_part
                            print(f"   🔍 Extracted original_text từ user message (prefix 'văn bản:'): {len(original_text)} chars")
            elif len(content) > 50 and not any(word in content_lower_user for word in ["tóm tắt", "diễn giải", "trích xuất", "lớp", "khối", "xin chào", "chào", "muốn", "tôi muốn", "thực hiện"]):
                # Văn bản dài không có từ khóa tóm tắt
                if not original_text:  # Lấy văn bản đầu tiên tìm thấy
                    original_text = content
                    print(f"   🔍 Extracted original_text từ user message (văn bản dài): {len(original_text)} chars")
        else:
            # Xử lý assistant messages - xác định stage
            content_lower = content.lower()
            # Ưu tiên các message mới nhất (đi từ cuối lên)
            if conversation_stage is None:
                if "văn bản đã được nhận" in content_lower or "đang xử lý" in content_lower:
                    conversation_stage = "summary_type"
                elif "đã được xử lý" in content_lower or "kiểm tra chính tả" in content_lower:
                    conversation_stage = "summary_type"
                    # Cố gắng extract processed_text từ message
                    if "**Văn bản của bạn:**" in content:
                        try:
                            parts = content.split("**Văn bản của bạn:**")
                            if len(parts) > 1:
                                processed_text = parts[1].split("---")[0].strip()
                                if not original_text:
                                    original_text = processed_text
                        except:
                            pass
                elif "xác nhận" in content_lower and ("trích xuất" in content_lower or "diễn giải" in content_lower):
                    conversation_stage = "processing"
                    if "diễn giải" in content_lower:
                        summary_type = "abstract"
                    elif "trích xuất" in content_lower:
                        summary_type = "extract"
                    # Extract grade_level
                    for i in range(1, 6):
                        if f"lớp {i}" in content_lower:
                            grade_level = i
                            break
                elif "kết quả tóm tắt" in content_lower or "bản tóm tắt cuối cùng" in content_lower:
                    conversation_stage = "completed"
                elif "xin chào" in content_lower and "hãy cung cấp văn bản" in content_lower:
                    conversation_stage = "text_input"
    
    # Build messages list theo thứ tự thời gian (từ đầu đến cuối)
    for m in mem.conversation_history[-max_messages:]:
        content = (m.get("content") or "").strip()
        if content.lower() in ctrl:
            continue
        role = (m.get("role") or "").lower()
        if role == "user":
            msgs.append(HumanMessage(content=content))
        else:
            msgs.append(AIMessage(content=content))
    
    # Nếu message cuối cùng là assistant, cần user input
    needs_user_input = True if msgs and isinstance(msgs[-1], AIMessage) else False
    
    # QUAN TRỌNG: Ưu tiên xác định stage dựa trên message cuối cùng (OVERRIDE logic trong loop)
    # Điều này đảm bảo stage được xác định chính xác từ message mới nhất
    # LUÔN LUÔN override conversation_stage từ message cuối cùng
    if msgs:
        last_msg = msgs[-1]
        last_content = last_msg.content.lower() if hasattr(last_msg, 'content') else str(last_msg).lower()
        
        # Kiểm tra message cuối cùng để xác định stage chính xác (OVERRIDE)
        if isinstance(last_msg, AIMessage):
            # Message cuối là assistant - đây là điểm quan trọng nhất để xác định stage
            # LUÔN LUÔN override conversation_stage từ message cuối
            if "văn bản đã được nhận" in last_content or "đang xử lý" in last_content:
                conversation_stage = "summary_type"  # OVERRIDE - QUAN TRỌNG!
                print(f"   🔍 Set conversation_stage = 'summary_type' từ message cuối (có 'văn bản đã được nhận' hoặc 'đang xử lý')")
            elif "chọn loại tóm tắt" in last_content or "bây giờ hãy chọn loại tóm tắt" in last_content:
                conversation_stage = "summary_type"  # OVERRIDE
                print(f"   🔍 Set conversation_stage = 'summary_type' từ message cuối (có 'chọn loại tóm tắt')")
            elif "đã được xử lý" in last_content or "kiểm tra chính tả" in last_content:
                conversation_stage = "summary_type"  # OVERRIDE
                print(f"   🔍 Set conversation_stage = 'summary_type' từ message cuối (có 'đã được xử lý' hoặc 'kiểm tra chính tả')")
            elif "xác nhận" in last_content and ("trích xuất" in last_content or "diễn giải" in last_content):
                conversation_stage = "processing"  # OVERRIDE
                print(f"   🔍 Set conversation_stage = 'processing' từ message cuối (có 'xác nhận')")
            elif "kết quả tóm tắt" in last_content or "bản tóm tắt cuối cùng" in last_content:
                conversation_stage = "completed"  # OVERRIDE
                print(f"   🔍 Set conversation_stage = 'completed' từ message cuối (có 'kết quả tóm tắt')")
            elif "xin chào" in last_content and "hãy cung cấp văn bản" in last_content:
                conversation_stage = "text_input"  # OVERRIDE
                print(f"   🔍 Set conversation_stage = 'text_input' từ message cuối (greeting)")
            # Nếu không match, giữ nguyên conversation_stage từ loop hoặc set mặc định
            elif conversation_stage is None:
                conversation_stage = "text_input"
                print(f"   🔍 Set conversation_stage = 'text_input' (mặc định, không match pattern nào)")
        else:
            # Message cuối là user - cần xác định từ message trước đó (assistant)
            if len(msgs) > 1 and isinstance(msgs[-2], AIMessage):
                prev_content = msgs[-2].content.lower() if hasattr(msgs[-2], 'content') else str(msgs[-2]).lower()
                if "văn bản đã được nhận" in prev_content or "đang xử lý" in prev_content:
                    conversation_stage = "summary_type"  # OVERRIDE
                    print(f"   🔍 Set conversation_stage = 'summary_type' từ message trước (có 'văn bản đã được nhận')")
                elif "chọn loại tóm tắt" in prev_content:
                    conversation_stage = "summary_type"  # OVERRIDE
                    print(f"   🔍 Set conversation_stage = 'summary_type' từ message trước (có 'chọn loại tóm tắt')")
                elif conversation_stage is None:
                    conversation_stage = "text_input"
            elif conversation_stage is None:
                conversation_stage = "text_input"
    
    # Nếu vẫn chưa xác định được, mặc định
    if conversation_stage is None:
        if not msgs:
            conversation_stage = "greeting"
            needs_user_input = False
            print(f"   🔍 Set conversation_stage = 'greeting' (không có messages)")
        else:
            conversation_stage = "text_input"
            print(f"   🔍 Set conversation_stage = 'text_input' (mặc định cuối cùng)")
    
    # Đảm bảo có processed_text nếu có original_text
    if original_text and not processed_text:
        processed_text = original_text
    
    # Debug: In thông tin state đã build (LUÔN LUÔN để debug)
    print(f"🔍 build_state_from_memory debug:")
    print(f"   - Conversation stage: {conversation_stage}")
    print(f"   - Original text: {len(original_text)} chars" + (f" (first 50: {original_text[:50]}...)" if original_text else " (KHÔNG CÓ)"))
    print(f"   - Processed text: {len(processed_text)} chars" + (f" (first 50: {processed_text[:50]}...)" if processed_text else " (KHÔNG CÓ)"))
    print(f"   - Messages count: {len(msgs)}")
    if msgs:
        last_msg = msgs[-1]
        if isinstance(last_msg, AIMessage):
            print(f"   - Last message (assistant): {last_msg.content[:100]}...")
        else:
            print(f"   - Last message (user): {last_msg.content[:100]}...")
    else:
        print(f"   - Last message: KHÔNG CÓ MESSAGES")
    
    return {
        "messages": msgs,
        "current_agent": "coordinator_agent",
        "needs_user_input": needs_user_input,
        "conversation_stage": conversation_stage,
        "original_text": original_text,
        "summary_type": summary_type,
        "grade_level": grade_level,
        "processed_text": processed_text,
        "summary_result": "",
        "final_result": "",
        "input_classification": None
    }

