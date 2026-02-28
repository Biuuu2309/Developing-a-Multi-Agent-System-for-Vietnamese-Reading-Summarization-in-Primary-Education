from typing import TypedDict, Literal, Optional, List, Dict, Any
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
import json


class TaskDefinition(TypedDict):
    task_type: Literal[
        "summarization",
        "evaluation",
        "explain_system",
        "casual_chat",
        "image_analysis",
        "unknown"
    ]
    strategy: Optional[Literal["abstractive", "extractive"]]
    grade_level: Optional[int]


class PlanningAgent:
    """
    Advanced Planning Agent với:
    - Dynamic planning: Tạo kế hoạch động dựa trên context
    - Meta-reasoning: Đánh giá, self-critique, reflection
    - Strategy switching: Có thể thay đổi strategy dựa trên feedback
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        if use_llm:
            self.llm = ChatOllama(model="qwen2.5:7b")
            self._setup_prompts()

    def _setup_prompts(self):
        """Setup prompts cho dynamic planning và meta-reasoning"""
        
        self.planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là Planning Agent thông minh. Nhiệm vụ của bạn là tạo kế hoạch thực thi động cho hệ thống tóm tắt văn bản.

Hãy phân tích yêu cầu và tạo kế hoạch với các thành phần:
1. Subgoals: Phân rã mục tiêu thành các mục tiêu con
2. Action Steps: Các bước hành động cụ thể (summarize, evaluate, refine, etc.)
3. Strategy Selection: Chọn strategy phù hợp (extractive/abstractive) dựa trên đặc điểm văn bản
4. Assumptions & Risks: Các giả định và rủi ro tiềm ẩn
5. Self-critique: Tự phê bình những điểm có thể cải thiện trong plan

Trả về JSON với format:
{{
    "subgoals": ["goal1", "goal2", ...],
    "pipeline": [
        {{"step": "summarize", "strategy": "extractive|abstractive", "grade_level": int, "reasoning": "lý do"}},
        {{"step": "evaluate", "metrics": ["rouge", "bertscore"], "reasoning": "lý do"}},
        ...
    ],
    "assumptions": ["assumption1", ...],
    "risks": ["risk1", ...],
    "self_critique": "nhận xét về plan",
    "alternative_strategies": ["strategy khác nếu cần"],
    "reflection": "suy nghĩ về cách cải thiện plan"
}}"""),
            ("human", """Yêu cầu: {task_description}
Intent: {intent_info}
History context: {history_context}
Text length: {text_length} characters
Current strategy: {current_strategy}""")
        ])
        
        self.meta_reasoning_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là Meta-Reasoning Agent. Nhiệm vụ của bạn là đánh giá và cải thiện kế hoạch.

Hãy thực hiện:
1. Đánh giá tính khả thi của plan
2. Xác định các điểm yếu và rủi ro
3. Đề xuất cải thiện
4. Xem xét việc thay đổi strategy nếu cần

Trả về JSON:
{{
    "feasibility_score": float (0-1),
    "weaknesses": ["weakness1", ...],
    "improvements": ["improvement1", ...],
    "strategy_recommendation": "extractive|abstractive|hybrid|keep_current",
    "reasoning": "lý do cho recommendation",
    "revised_plan": {{...}} hoặc null nếu không cần sửa
}}"""),
            ("human", """Plan hiện tại: {current_plan}
Evaluation results (nếu có): {evaluation_results}
Text characteristics: {text_characteristics}""")
        ])

    def plan(
        self, 
        intent_result: dict,
        context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Tạo execution plan động dựa trên intent và context
        
        Args:
            intent_result: Kết quả từ Intent Agent
            context: Context bổ sung (history, text info, etc.)
        """
        intent = intent_result.get("intent")
        context = context or {}

        if intent == "summarize":
            return self._build_dynamic_summarization_plan(intent_result, context)

        if intent == "evaluate":
            return self._build_evaluation_plan(intent_result)

        return {
            "pipeline": [],
            "message": "Intent not supported"
        }

    def _build_dynamic_summarization_plan(
        self, 
        intent_result: dict,
        context: Dict[str, Any]
    ) -> dict:
        """Tạo plan động cho summarization với meta-reasoning"""
        
        strategy = intent_result.get("summarization_type", "abstractive")
        grade_level = intent_result.get("grade_level")
        text_length = context.get("text_length", 0)
        history = context.get("history", [])
        
        # Nếu không dùng LLM, fallback về plan đơn giản
        if not self.use_llm:
            return self._build_simple_plan(intent_result)
        
        # Tạo plan động với LLM
        try:
            task_description = self._build_task_description(intent_result, context)
            history_context = self._extract_history_context(history)
            
            prompt_input = {
                "task_description": task_description,
                "intent_info": json.dumps(intent_result, ensure_ascii=False),
                "history_context": history_context,
                "text_length": text_length,
                "current_strategy": strategy
            }
            
            chain = self.planning_prompt | self.llm
            response = chain.invoke(prompt_input)
            if hasattr(response, 'content'):
                response = response.content.strip()
            else:
                response = str(response).strip()
            
            # Parse JSON response
            plan = self._parse_llm_response(response)
            
            # Meta-reasoning: Đánh giá và cải thiện plan
            refined_plan = self._meta_reasoning(plan, intent_result, context)
            
            return refined_plan
            
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            # Fallback về plan đơn giản nếu LLM fail
            return self._build_simple_plan(intent_result)

    def _build_task_description(
        self, 
        intent_result: dict,
        context: Dict[str, Any]
    ) -> str:
        """Xây dựng mô tả task từ intent và context"""
        strategy = intent_result.get("summarization_type", "abstractive")
        grade_level = intent_result.get("grade_level")
        
        desc = f"Tóm tắt văn bản sử dụng strategy: {strategy}"
        if grade_level:
            desc += f", cho học sinh lớp {grade_level}"
        
        text_length = context.get("text_length", 0)
        if text_length > 0:
            desc += f". Độ dài văn bản: {text_length} ký tự"
        
        return desc

    def _extract_history_context(self, history: List[Dict]) -> str:
        """Extract context từ history"""
        if not history:
            return "Không có lịch sử"
        
        recent_messages = history[-3:]  # Lấy 3 message gần nhất
        context_parts = []
        for msg in recent_messages:
            role = msg.get("role", "")
            content = msg.get("content", "")[:100]  # Giới hạn độ dài
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)

    def _parse_llm_response(self, response: str) -> dict:
        """Parse response từ LLM thành dict"""
        # Loại bỏ markdown nếu có
        response = response.replace("```json", "").replace("```", "").strip()
        
        try:
            plan = json.loads(response)
            # Đảm bảo có pipeline
            if "pipeline" not in plan:
                plan["pipeline"] = []
            return plan
        except json.JSONDecodeError:
            # Nếu không parse được, trả về plan mặc định
            return {
                "pipeline": [
                    {"step": "summarize", "strategy": "abstractive"}
                ],
                "self_critique": "Không thể parse response từ LLM"
            }

    def _meta_reasoning(
        self,
        plan: dict,
        intent_result: dict,
        context: Dict[str, Any]
    ) -> dict:
        """Meta-reasoning: Đánh giá và cải thiện plan"""
        
        if not self.use_llm:
            return plan
        
        try:
            text_length = context.get("text_length", 0)
            text_characteristics = self._analyze_text_characteristics(context)
            evaluation_results = context.get("previous_evaluation")
            
            prompt_input = {
                "current_plan": json.dumps(plan, ensure_ascii=False),
                "evaluation_results": json.dumps(evaluation_results) if evaluation_results else "Chưa có",
                "text_characteristics": text_characteristics
            }
            
            chain = self.meta_reasoning_prompt | self.llm
            response = chain.invoke(prompt_input)
            if hasattr(response, 'content'):
                response = response.content.strip()
            else:
                response = str(response).strip()
            
            meta_result = self._parse_llm_response(response)
            
            # Áp dụng improvements nếu có
            if meta_result.get("revised_plan"):
                plan = meta_result["revised_plan"]
            
            # Thêm meta-reasoning info vào plan
            plan["meta_reasoning"] = {
                "feasibility_score": meta_result.get("feasibility_score", 0.8),
                "weaknesses": meta_result.get("weaknesses", []),
                "improvements": meta_result.get("improvements", []),
                "strategy_recommendation": meta_result.get("strategy_recommendation", "keep_current"),
                "reasoning": meta_result.get("reasoning", "")
            }
            
            # Áp dụng strategy recommendation nếu khác với current
            strategy_rec = meta_result.get("strategy_recommendation")
            if strategy_rec and strategy_rec != "keep_current":
                if strategy_rec in ["extractive", "abstractive"]:
                    # Cập nhật strategy trong pipeline
                    for step in plan.get("pipeline", []):
                        if step.get("step") == "summarize":
                            step["strategy"] = strategy_rec
                            step["strategy_changed"] = True
                            step["change_reason"] = meta_result.get("reasoning", "")
            
            return plan
            
        except (json.JSONDecodeError, AttributeError, KeyError) as err:
            # Nếu meta-reasoning fail, trả về plan gốc
            plan["meta_reasoning"] = {
                "error": str(err),
                "feasibility_score": 0.7
            }
            return plan

    def _analyze_text_characteristics(self, context: Dict[str, Any]) -> str:
        """Phân tích đặc điểm văn bản"""
        text_length = context.get("text_length", 0)
        text_preview = context.get("text_preview", "")
        
        characteristics = []
        
        if text_length > 1000:
            characteristics.append("Văn bản dài")
        elif text_length < 200:
            characteristics.append("Văn bản ngắn")
        
        if text_preview:
            # Đếm số câu
            sentence_count = text_preview.count('.') + text_preview.count('!') + text_preview.count('?')
            if sentence_count > 10:
                characteristics.append("Nhiều câu")
            elif sentence_count < 3:
                characteristics.append("Ít câu")
        
        return ", ".join(characteristics) if characteristics else "Không có thông tin"

    def _build_simple_plan(self, intent_result: dict) -> dict:
        """Fallback: Tạo plan đơn giản không dùng LLM"""
        strategy = intent_result.get("summarization_type", "abstractive")
        grade_level = intent_result.get("grade_level")

        plan = {
            "pipeline": [
                {
                    "step": "summarize",
                    "strategy": strategy,
                    "grade_level": grade_level,
                    "reasoning": f"Sử dụng strategy {strategy} dựa trên yêu cầu"
                }
            ],
            "subgoals": ["Tóm tắt văn bản", "Đánh giá chất lượng"],
            "assumptions": ["Văn bản đầu vào hợp lệ"],
            "risks": ["Chất lượng tóm tắt có thể không đạt yêu cầu"],
            "self_critique": "Plan đơn giản, có thể cải thiện với dynamic planning"
        }

        if intent_result.get("require_evaluation", True):
            plan["pipeline"].append(
                {
                    "step": "evaluate",
                    "metrics": intent_result.get("metrics", ["rouge", "bertscore"]),
                    "reasoning": "Đánh giá chất lượng tóm tắt"
                }
            )

        return plan

    def _build_evaluation_plan(self, intent_result: dict) -> dict:
        """Tạo plan cho evaluation"""
        return {
            "pipeline": [
                {
                    "step": "evaluate",
                    "metrics": intent_result.get("metrics", ["rouge"]),
                    "reasoning": "Đánh giá chất lượng tóm tắt"
                }
            ]
        }

    def revise_plan(
        self,
        current_plan: dict,
        feedback: Dict[str, Any],
        evaluation_results: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Điều chỉnh plan dựa trên feedback và evaluation results
        
        Args:
            current_plan: Plan hiện tại
            feedback: Feedback từ user hoặc system
            evaluation_results: Kết quả evaluation nếu có
        """
        # Nếu evaluation score thấp, có thể cần thay đổi strategy
        if evaluation_results:
            rouge_f1 = evaluation_results.get("rougeL_f1", 0)
            bert_f1 = evaluation_results.get("bertscore_f1", 0)
            
            # Nếu score thấp, đề xuất thay đổi strategy
            if rouge_f1 < 0.5 or bert_f1 < 0.6:
                for step in current_plan.get("pipeline", []):
                    if step.get("step") == "summarize":
                        current_strategy = step.get("strategy", "abstractive")
                        # Đổi strategy
                        new_strategy = "extractive" if current_strategy == "abstractive" else "abstractive"
                        step["strategy"] = new_strategy
                        step["strategy_changed"] = True
                        step["change_reason"] = f"Score thấp (ROUGE: {rouge_f1:.2f}, BERT: {bert_f1:.2f}), thử strategy {new_strategy}"
        
        # Thêm step refine nếu cần
        if feedback.get("needs_refinement", False):
            current_plan["pipeline"].append({
                "step": "refine",
                "reasoning": "Cần cải thiện tóm tắt dựa trên feedback"
            })
        
        return current_plan