from pathlib import Path
import sys
from Source.ai.Multi_Agent.Source.Main.Agents.Agents_Summary import Abstracter_Agent, Aggregator_Agent, Coordinator_Agent, Evaluator_Agent, Extractor_Agent, GradeCalibrator_Agent, OCR_Agent, SpellChecker_Agent, InputClassifier_Agent
project_root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Source' / 'ai').exists()), None)
if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from flask import Flask, request, jsonify

app = Flask(__name__)
coordinator = Coordinator_Agent()

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text")
    mode = data.get("mode")  # "extractive" hoặc "abstractive"

    summary = coordinator.handle_request(text, mode)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
