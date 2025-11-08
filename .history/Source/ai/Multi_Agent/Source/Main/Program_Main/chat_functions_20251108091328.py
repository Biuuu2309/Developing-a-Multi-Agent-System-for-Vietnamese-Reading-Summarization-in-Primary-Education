from langchain_core.messages import HumanMessage, AIMessage
from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager
from Source.ai.Multi_Agent.Source.Main.Program_Main.memory_helpers import build_state_from_memory

def run_langgraph_chat_fixed(app, create_initial_state, initial_state=None):
    """Hàm run_langgraph_chat đã được sửa để xử lý đúng workflow với tích hợp memory"""
    print("🤖 Multi-Agent System Summary For Primary School Students")
    print("=" * 60)
    print("Commands: 'exit', 'clear' (STM), 'clear_all' (STM+LTM), 'mem_stats'")

    state = initial_state or create_initial_state()

    # KHÔNG auto-invoke nếu đã có messages (tránh chào lại)
    # Nếu đã có messages từ memory và needs_user_input = True, hiển thị message cuối cùng
    if not state.get("messages"):
        try:
            state = app.invoke(state, config={"recursion_limit": 50})
            last = state["messages"][-1] if state["messages"] else None
            if last and isinstance(last, AIMessage):
                print(f"\n🤖{state['current_agent']}: {last.content}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            pass
    elif state.get("messages") and state.get("needs_user_input", False):
        # Có messages từ memory và đang chờ user input, hiển thị message cuối cùng
        last = state["messages"][-1] if state["messages"] else None
        if last and isinstance(last, AIMessage):
            print(f"\n🤖{state.get('current_agent', 'coordinator_agent')}: {last.content}")
            # Hiển thị thông tin về stage hiện tại
            print(f"📊 Conversation stage: {state.get('conversation_stage', 'unknown')}")
            mem = memory_manager.get_memory()
            print(f"   [Memory: {len(mem.conversation_history)} msgs, {len(mem.user_preferences)} prefs]")

    while True:
        # Kiểm tra nếu cần user input
        if state.get("needs_user_input", False):
            user_input = input("\n👤 Bạn: ").strip()
            memory_manager.add_message("user", user_input)

            if user_input.lower() in ["exit", "quit", "thoát"]:
                print("👋 Bye MAS Lịch sử chat đã được lưu.")
                break
            if user_input.lower() in ["clear", "xóa", "reset"]:
                memory_manager.clear_memory()
                state = create_initial_state()
                print("🧹 Đã xóa short-term memory. Long-term vẫn giữ.")
                continue
            if user_input.lower() in ["clear_all", "xóa_all", "reset_all"]:
                memory_manager.clear_memory(also_long_term=True)
                state = create_initial_state()
                print("🧹 Đã xóa cả short-term và long-term memory.")
                continue
            if user_input.lower() in ["mem_stats", "memory_stats"]:
                from Source.ai.Multi_Agent.Source.Main.Memory.memory.long_term_memory import long_term_memory
                print(f"📊 Long-term Memory: {long_term_memory.collection.count()} items")
                continue

            # Thêm user input vào state và tiếp tục xử lý
            state["messages"].append(HumanMessage(content=user_input))
            print(f"👤: {user_input}")
            state["needs_user_input"] = False
            # Reset input_classification để phân loại lại
            state["input_classification"] = None

        # Xử lý workflow
        try:
            state = app.invoke(state, config={"recursion_limit": 50})
            last = state["messages"][-1] if state["messages"] else None
            if last and isinstance(last, AIMessage):
                print(f"\n🤖{state['current_agent']}: {last.content}")
            
            mem = memory_manager.get_memory()
            print(f"   [Memory: {len(mem.conversation_history)} msgs, {len(mem.user_preferences)} prefs]")
            
        except Exception as e:
            print(f"Error in processing: {e}")
            import traceback
            traceback.print_exc()
            break

def read_long_term_memory_by_session_id(session_id: str):
    """Đọc lịch sử chat từ session_id"""
    from Source.ai.Multi_Agent.Source.Main.Memory.memory.long_term_memory import long_term_memory
    col = long_term_memory.collection
    all_items = col.get(include=["documents","metadatas"])
    for doc, meta in zip(all_items["documents"], all_items["metadatas"]):
        if meta.get("session_id") == session_id:
            print(meta.get("timestamp"), meta.get("session_id"), meta.get("role"), ":", doc)

def continue_chat_from_session(session_id: str, app, create_initial_state, build_state_from_memory_func=None, user_id: str = "default_user", replay_last_n: int = 20):
    """Tiếp tục chat từ session cũ
    
    Args:
        session_id: ID của session cần continue
        app: LangGraph app
        create_initial_state: Hàm tạo initial state
        build_state_from_memory_func: Hàm build_state_from_memory (nếu None, sẽ import từ memory_helpers)
        user_id: User ID
        replay_last_n: Số message cuối cùng để replay
    """
    # Import build_state_from_memory nếu chưa có
    if build_state_from_memory_func is None:
        from Source.ai.Multi_Agent.Source.Main.Program_Main.memory_helpers import build_state_from_memory as build_state_from_memory_func
    
    print("Previous chat history:")
    read_long_term_memory_by_session_id(session_id)
    loaded = memory_manager.resume_session(session_id, user_id=user_id, replay_last_n=replay_last_n)
    print(f"Resumed {loaded} messages from long-term: {session_id}")
    
    # Sử dụng hàm build_state_from_memory đã được sửa để xác định đúng conversation_stage
    initial_state = build_state_from_memory_func(user_id=user_id, max_messages=replay_last_n)
    
    # Debug: Hiển thị thông tin state đã build
    print(f"📊 Built state info:")
    print(f"   - Messages: {len(initial_state.get('messages', []))}")
    print(f"   - Conversation stage: {initial_state.get('conversation_stage', 'unknown')}")
    print(f"   - Needs user input: {initial_state.get('needs_user_input', False)}")
    print(f"   - Original text: {len(initial_state.get('original_text', ''))} chars")
    print(f"   - Processed text: {len(initial_state.get('processed_text', ''))} chars")
    
    run_langgraph_chat_fixed(app, create_initial_state, initial_state=initial_state)

