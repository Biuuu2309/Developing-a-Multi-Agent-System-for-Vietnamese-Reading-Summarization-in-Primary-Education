from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import traceback

print("🔄 Initializing Flask MAS API...")

# Ensure repository root (with 'Source/ai') is on sys.path
project_root = next((p for p in [Path(__file__).parent.parent.parent.parent.parent.parent, *Path(__file__).parent.parent.parent.parent.parent.parent.parents] if (p / 'Source' / 'ai').exists()), None)
if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print(f"✅ Added project root to path: {project_root}")

# Import MAS components with error handling
try:
    print("📦 Importing MAS_Program...")
    from Source.ai.Multi_Agent.Source.Main.Program_Main.MAS_Program import app, create_initial_state
    print("✅ MAS_Program imported successfully")
except Exception as e:
    print(f"❌ Error importing MAS_Program: {e}")
    traceback.print_exc()
    raise

try:
    print("📦 Importing mas_api_handler...")
    from Source.ai.Multi_Agent.Source.Main.Program_Main.mas_api_handler import process_message_api
    print("✅ mas_api_handler imported successfully")
except Exception as e:
    print(f"❌ Error importing mas_api_handler: {e}")
    traceback.print_exc()
    raise

try:
    print("📦 Importing memory_manager...")
    from Source.ai.Multi_Agent.Source.Main.Memory.memory.memory import memory_manager
    print("✅ memory_manager imported successfully")
except Exception as e:
    print(f"❌ Error importing memory_manager: {e}")
    traceback.print_exc()
    raise

app_flask = Flask(__name__)
CORS(app_flask)
print("✅ Flask app created")

# Dictionary để lưu mapping conversation_id -> session_id
# Format: {conversation_id: {"session_id": str, "user_id": str, "last_activity": timestamp}}
conversation_session_map = {}

@app_flask.route('/process', methods=['POST'])
def process_message():
    """
    Endpoint để xử lý message từ Spring Boot
    
    Request body:
    {
        "conversationId": str,
        "userId": str,
        "content": str,
        "messageId": str,
        "role": str
    }
    
    Response:
    {
        "response": str,
        "agentId": str,
        "metadata": str,
        "role": str
    }
    """
    try:
        print(f"\n📨 Received request at /process")
        data = request.get_json()
        
        if not data:
            print("❌ No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400
        
        conversation_id = data.get("conversationId")
        user_id = data.get("userId", "default_user")
        content = data.get("content", "")
        message_id = data.get("messageId", "")
        role = data.get("role", "user")
        
        print(f"📝 Request data: conversationId={conversation_id}, userId={user_id}, content={content[:50]}...")
        
        if not content:
            print("❌ Content is required")
            return jsonify({"error": "Content is required"}), 400
        
        # Lấy hoặc tạo session_id cho conversation_id
        session_info = conversation_session_map.get(conversation_id)
        session_id = None
        if session_info:
            session_id = session_info.get("session_id")
            # Kiểm tra xem user_id có khớp không
            if session_info.get("user_id") != user_id:
                # User khác, tạo session mới
                session_id = None
        
        # Xử lý message qua MAS
        print(f"🔄 Processing message through MAS...")
        result = process_message_api(
            app=app,
            create_initial_state=create_initial_state,
            user_input=content,
            conversation_id=conversation_id,
            user_id=user_id,
            session_id=session_id
        )
        print(f"✅ MAS processing completed")
        
        # Lưu session_id vào map
        if result.get("session_id"):
            import time
            conversation_session_map[conversation_id] = {
                "session_id": result["session_id"],
                "user_id": user_id,
                "last_activity": time.time()
            }
            print(f"💾 Saved session: {conversation_id} -> {result['session_id']}")
        
        # Tạo response theo format MASResponse
        response = {
            "response": result.get("response", ""),
            "agentId": result.get("agent_id", "coordinator_agent"),
            "metadata": result.get("metadata", "{}"),
            "role": "assistant"
        }
        
        print(f"✅ Sending response: agentId={response['agentId']}, response length={len(response['response'])}")
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        error_msg = f"Error in Flask API: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({
            "error": error_msg,
            "response": f"Xin lỗi, đã xảy ra lỗi: {str(e)}",
            "agentId": "error",
            "metadata": "{}",
            "role": "assistant"
        }), 500

@app_flask.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "MAS Flask API"}), 200

@app_flask.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions"""
    return jsonify({
        "conversation_sessions": conversation_session_map,
        "active_sessions_count": len(conversation_session_map)
    }), 200

if __name__ == '__main__':
    print("🚀 Starting MAS Flask API Server...")
    print("📡 Endpoint: http://localhost:8000/process")
    print("💚 Health check: http://localhost:8000/health")
    # Tắt debug mode để tránh lỗi reload trên Windows
    # Nếu cần debug, có thể set debug=True nhưng sẽ có warning về reload
    app_flask.run(host='0.0.0.0', port=8000, debug=False)

