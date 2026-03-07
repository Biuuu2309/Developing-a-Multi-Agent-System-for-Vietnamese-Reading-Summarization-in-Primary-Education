from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import json
from pathlib import Path

project_root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Source' / 'ai').exists()), None)
if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Source.ai.Multi_Agent_System.Agents.SessionMemory import SessionMemory
from Source.ai.Multi_Agent_System.Agents.ConversationManager import ConversationManager

app = Flask(__name__)
CORS(app)

memory = None
cm = None
graph = None

def initialize_mas():
    global memory, cm, graph
    try:
        from Source.ai.Multi_Agent_System.Main.System_2.MAS_main import graph as mas_graph
        graph = mas_graph
        memory = SessionMemory(use_advanced_memory=True, storage_path="memory_storage")
        cm = ConversationManager(graph, memory)
        print("MAS System initialized successfully")
    except Exception as e:
        print(f"Error initializing MAS: {e}")
        raise

initialize_mas()

@app.route('/api/mas/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('sessionId')
        user_id = data.get('userId')
        user_input = data.get('userInput')
        conversation_id = data.get('conversationId')
        
        if not user_input:
            return jsonify({'error': 'userInput is required'}), 400
        
        if not session_id:
            session_id = cm.create_session(user_id)
        
        history = memory.get_history(session_id)
        
        state = {
            "user_input": user_input,
            "history": history
        }
        
        result = graph.invoke(state)
        
        output = result.get("final_output", "")
        
        memory.add_message(session_id, "user", user_input, save_to_long_term=True)
        memory.add_message(session_id, "assistant", output, save_to_long_term=True)
        
        response_data = {
            'session_id': session_id,
            'final_output': output,
            'intent': json.dumps(result.get('intent', {})),
            'plan': json.dumps(result.get('plan', {})),
            'summary': result.get('summary', ''),
            'evaluation': json.dumps(result.get('evaluation', {})),
            'clarification_needed': result.get('clarification_needed', False),
            'clarification_question': result.get('clarification_question', ''),
            'agent_confidences': json.dumps(result.get('agent_confidences', {})),
            'status': 'COMPLETED'
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'status': 'FAILED'}), 500

@app.route('/api/mas/session/<session_id>/history', methods=['GET'])
def get_history(session_id):
    try:
        history = memory.get_history(session_id)
        return jsonify({'history': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mas/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'MAS Flask API'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
