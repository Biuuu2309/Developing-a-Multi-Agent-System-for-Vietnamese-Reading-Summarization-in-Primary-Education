from langchain_core.messages import HumanMessage, AIMessage
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager
from Source.ai.Multi_Agent.Source.Main.Program_Main.memory_helpers import build_state_from_memory
import json

def process_message_api(app, create_initial_state, user_input: str, conversation_id: str, user_id: str, session_id: str = None):
    """
    Xử lý message từ API (không interactive)
    
    Args:
        app: LangGraph app
        create_initial_state: Hàm tạo initial state
        user_input: Nội dung message từ user
        conversation_id: ID của conversation (Spring Boot)
        user_id: ID của user
        session_id: Session ID của MAS (nếu có, dùng để continue session)
    
    Returns:
        dict: {
            "response": str,  # Response từ MAS
            "agent_id": str,  # ID của agent cuối cùng
            "metadata": str,  # Metadata JSON string
            "session_id": str,  # Session ID của MAS
            "needs_user_input": bool  # Có cần user input tiếp không
        }
    """
    try:
        # Quản lý session: nếu có session_id, tiếp tục session đó
        # Nếu không, tạo session mới hoặc lấy session từ conversation_id
        if session_id:
            loaded = memory_manager.resume_session(session_id, user_id=user_id, replay_last_n=20)
            print(f"Resumed {loaded} messages from session: {session_id}")
            initial_state = build_state_from_memory(user_id=user_id, max_messages=20)
        else:
            # Kiểm tra xem có session nào cho user này không
            # Lấy memory để kiểm tra xem đã có session chưa
            stm = memory_manager.get_memory(user_id)
            current_session = stm.session_id if stm else None
            
            # Nếu chưa có session hoặc session rỗng, tạo session mới
            if not current_session or not stm.conversation_history:
                new_session_id = memory_manager.start_new_session(user_id=user_id, clear_history=False, keep_preferences=True)
                print(f"Started new session: {new_session_id}")
                initial_state = create_initial_state()
            else:
                # Đã có session, build state từ memory
                initial_state = build_state_from_memory(user_id=user_id, max_messages=20)
        
        # Thêm user message vào memory và state
        print(f"📝 Adding user message to state: {user_input[:50]}...")
        memory_manager.add_message("user", user_input, user_id=user_id)
        initial_state["messages"].append(HumanMessage(content=user_input))
        initial_state["needs_user_input"] = False
        initial_state["input_classification"] = None
        
        # Chạy workflow
        print(f"🔄 Invoking MAS workflow...")
        print(f"   Initial state: conversation_stage={initial_state.get('conversation_stage')}, messages={len(initial_state.get('messages', []))}")
        try:
            state = app.invoke(initial_state, config={"recursion_limit": 50})
            print(f"✅ MAS workflow completed")
        except Exception as e:
            print(f"❌ Error during MAS workflow invocation: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Lấy response cuối cùng từ assistant
        print(f"📤 Extracting response from state...")
        last_message = None
        agent_id = "coordinator_agent"
        if state.get("messages"):
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage):
                agent_id = state.get("current_agent", "coordinator_agent")
                print(f"   Last message from agent: {agent_id}")
                print(f"   Response length: {len(last_message.content) if hasattr(last_message, 'content') else 0} chars")
        
        response_text = last_message.content if last_message and hasattr(last_message, 'content') else ""
        if not response_text:
            print(f"⚠️ Warning: No response text found, using default message")
            response_text = "Xin lỗi, tôi không thể tạo phản hồi."
        
        # Tạo metadata
        metadata = {
            "conversation_stage": state.get("conversation_stage", "unknown"),
            "summary_type": state.get("summary_type"),
            "grade_level": state.get("grade_level", 0),
            "has_original_text": bool(state.get("original_text")),
            "has_processed_text": bool(state.get("processed_text")),
            "needs_user_input": state.get("needs_user_input", False)
        }
        
        # Lấy session_id hiện tại
        current_session_id = memory_manager.get_session_id(user_id)
        
        return {
            "response": response_text,
            "agent_id": agent_id,
            "metadata": json.dumps(metadata),
            "session_id": current_session_id or "",
            "needs_user_input": state.get("needs_user_input", False)
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Error processing message: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return {
            "response": f"Xin lỗi, đã xảy ra lỗi: {str(e)}",
            "agent_id": "error",
            "metadata": json.dumps({"error": str(e)}),
            "session_id": "",
            "needs_user_input": False
        }

