# app.py - Flask web application for reading difficulty assessment

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import ReadingDifficultySystem

app = Flask(__name__)

# Initialize the system
system = ReadingDifficultySystem()

# Feature descriptions
FEATURE_DESCRIPTIONS = {
    "total_words": {
        "name": "Tổng số từ",
        "description": "Tổng số từ trong văn bản. Văn bản càng dài thường càng khó đọc.",
        "unit": "từ"
    },
    "unique_words": {
        "name": "Số từ khác nhau",
        "description": "Số lượng từ vựng độc nhất trong văn bản. Nhiều từ khác nhau cho thấy vốn từ vựng đa dạng.",
        "unit": "từ"
    },
    "type_token_ratio": {
        "name": "Tỷ lệ từ vựng đa dạng",
        "description": "Tỷ lệ giữa số từ khác nhau và tổng số từ. Giá trị cao (gần 1.0) cho thấy từ vựng đa dạng, giá trị thấp cho thấy lặp lại nhiều.",
        "unit": "tỷ lệ (0-1)"
    },
    "rare_word_ratio": {
        "name": "Tỷ lệ từ hiếm",
        "description": "Tỷ lệ từ thuộc lớp 4-5 (từ khó). Tỷ lệ cao cho thấy văn bản khó đọc.",
        "unit": "tỷ lệ (0-1)"
    },
    "unknown_word_ratio": {
        "name": "Tỷ lệ từ không xác định",
        "description": "Tỷ lệ từ không có trong từ điển các lớp. Tỷ lệ cao cho thấy văn bản có nhiều từ mới hoặc từ chuyên ngành.",
        "unit": "tỷ lệ (0-1)"
    },
    "avg_word_grade": {
        "name": "Độ khó trung bình từ vựng",
        "description": "Lớp trung bình của từ vựng trong văn bản. Giá trị 1-2: dễ, 3-4: trung bình, 5: khó.",
        "unit": "lớp (1-5)"
    },
    "num_sentences": {
        "name": "Số câu",
        "description": "Tổng số câu trong văn bản.",
        "unit": "câu"
    },
    "avg_sentence_length": {
        "name": "Độ dài trung bình câu",
        "description": "Số từ trung bình trong mỗi câu. Câu dài thường khó hiểu hơn.",
        "unit": "từ/câu"
    },
    "max_sentence_length": {
        "name": "Độ dài câu dài nhất",
        "description": "Số từ trong câu dài nhất. Câu quá dài có thể khó hiểu.",
        "unit": "từ"
    },
    "min_sentence_length": {
        "name": "Độ dài câu ngắn nhất",
        "description": "Số từ trong câu ngắn nhất.",
        "unit": "từ"
    },
    "long_sentence_ratio": {
        "name": "Tỷ lệ câu dài",
        "description": "Tỷ lệ câu có độ dài >= 15 từ. Tỷ lệ cao cho thấy văn bản có nhiều câu phức tạp.",
        "unit": "tỷ lệ (0-1)"
    },
    "avg_word_length": {
        "name": "Độ dài trung bình từ",
        "description": "Số ký tự trung bình trong mỗi từ. Từ dài thường khó hơn.",
        "unit": "ký tự"
    },
    "words_per_sentence": {
        "name": "Số từ mỗi câu",
        "description": "Số từ trung bình trong mỗi câu (tương tự avg_sentence_length).",
        "unit": "từ/câu"
    },
    "lexical_density": {
        "name": "Mật độ từ vựng",
        "description": "Tỷ lệ từ vựng độc nhất (tương tự type_token_ratio).",
        "unit": "tỷ lệ (0-1)"
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'error': 'Vui lòng nhập văn bản cần đánh giá.'
            }), 400
        
        # Get prediction
        difficulty_label, explanation = system.predict(text)
        
        # Get features
        sentences = system.preprocess(text)
        features = system.extract_features(sentences)
        
        # Override with vncorenlp counts
        sentence_count, word_count = system.count_sentences_words(text)
        features["num_sentences"] = sentence_count
        features["total_words"] = word_count
        
        if word_count > 0:
            features["words_per_sentence"] = word_count / sentence_count if sentence_count > 0 else 0
            features["avg_sentence_length"] = word_count / sentence_count if sentence_count > 0 else 0
        
        # Get matched rules
        difficulty, matched_rules = system.engine.infer(features)
        
        # Format features with descriptions
        formatted_features = []
        for key, value in features.items():
            if key in FEATURE_DESCRIPTIONS:
                desc = FEATURE_DESCRIPTIONS[key]
                formatted_value = round(value, 3) if isinstance(value, float) else value
                formatted_features.append({
                    'key': key,
                    'name': desc['name'],
                    'value': formatted_value,
                    'unit': desc['unit'],
                    'description': desc['description']
                })
        
        return jsonify({
            'success': True,
            'difficulty': difficulty_label,
            'difficulty_level': difficulty,
            'features': formatted_features,
            'matched_rules': [r['name'] for r in matched_rules],
            'explanation': explanation
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Lỗi khi xử lý: {str(e)}'
        }), 500

@app.route('/api/feature-descriptions', methods=['GET'])
def get_feature_descriptions():
    return jsonify(FEATURE_DESCRIPTIONS)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
