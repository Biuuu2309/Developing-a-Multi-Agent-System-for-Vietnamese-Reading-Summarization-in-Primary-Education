from typing import Dict, Any, Optional
from datetime import datetime
import math


class ConfidenceManager:
    """
    Confidence Management
    Quản lý độ tin cậy của các agents và decisions
    """
    
    def __init__(self):
        self.agent_confidence: Dict[str, float] = {}
        self.decision_confidence: Dict[str, Dict[str, Any]] = {}
        self.confidence_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def calculate_confidence(
        self,
        agent_name: str,
        task_type: str,
        input_data: Dict[str, Any],
        output: Any,
        metrics: Optional[Dict[str, float]] = None,
        historical_performance: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Tính confidence score (0.0 - 1.0)
        Dựa trên:
        - Historical performance
        - Current metrics
        - Task complexity
        - Output quality
        """
        confidence = 0.5  # Base confidence
        
        # Factor 1: Historical performance
        if historical_performance:
            success_rate = historical_performance.get("success_rate", 0.5)
            avg_metrics = historical_performance.get("avg_metrics", {})
            
            # Weight: 30%
            confidence += (success_rate - 0.5) * 0.3
        
        # Factor 2: Current metrics
        if metrics:
            # Normalize metrics to 0-1 range
            normalized_metrics = {}
            for key, value in metrics.items():
                if "f1" in key.lower() or "score" in key.lower():
                    normalized_metrics[key] = min(max(value, 0.0), 1.0)
            
            if normalized_metrics:
                avg_metric = sum(normalized_metrics.values()) / len(normalized_metrics)
                # Weight: 40%
                confidence += (avg_metric - 0.5) * 0.4
        
        # Factor 3: Output quality heuristics
        if output:
            output_str = str(output)
            # Check length (reasonable length indicates quality)
            if 50 < len(output_str) < 2000:
                confidence += 0.05
            
            # Check for error messages
            if "[Error]" in output_str or "Lỗi" in output_str:
                confidence -= 0.2
        
        # Factor 4: Task complexity (simpler tasks = higher confidence)
        complexity = self._estimate_complexity(input_data)
        if complexity < 0.5:
            confidence += 0.1
        elif complexity > 0.8:
            confidence -= 0.1
        
        # Clamp to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        # Store confidence
        self.agent_confidence[agent_name] = confidence
        
        # Store decision confidence
        decision_id = f"{agent_name}_{task_type}_{datetime.now().timestamp()}"
        self.decision_confidence[decision_id] = {
            "agent_name": agent_name,
            "task_type": task_type,
            "confidence": confidence,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        if agent_name not in self.confidence_history:
            self.confidence_history[agent_name] = []
        
        self.confidence_history[agent_name].append({
            "confidence": confidence,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return confidence
    
    def _estimate_complexity(self, input_data: Dict[str, Any]) -> float:
        """Ước tính độ phức tạp của task"""
        complexity = 0.5
        
        # Text length factor
        text = input_data.get("text", input_data.get("user_input", ""))
        if isinstance(text, str):
            if len(text) > 1000:
                complexity += 0.2
            elif len(text) < 100:
                complexity -= 0.1
        
        # Number of requirements
        requirements = input_data.get("requirements", {})
        if len(requirements) > 3:
            complexity += 0.1
        
        return max(0.0, min(1.0, complexity))
    
    def get_agent_confidence(self, agent_name: str) -> float:
        """Lấy confidence của agent"""
        return self.agent_confidence.get(agent_name, 0.5)
    
    def get_average_confidence(self, agent_name: str, window: int = 10) -> float:
        """Lấy average confidence trong window gần nhất"""
        if agent_name not in self.confidence_history:
            return 0.5
        
        history = self.confidence_history[agent_name][-window:]
        if not history:
            return 0.5
        
        avg = sum(h["confidence"] for h in history) / len(history)
        return avg
    
    def should_proceed(self, agent_name: str, threshold: float = 0.6) -> bool:
        """Quyết định có nên tiếp tục không dựa trên confidence"""
        confidence = self.get_agent_confidence(agent_name)
        return confidence >= threshold
    
    def get_confidence_level(self, confidence: float) -> str:
        """Chuyển confidence score thành level"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very_low"
    
    def get_confidence_summary(self) -> Dict[str, Any]:
        """Lấy summary của confidence"""
        return {
            "agent_confidences": self.agent_confidence,
            "total_decisions": len(self.decision_confidence),
            "average_confidence": (
                sum(self.agent_confidence.values()) / len(self.agent_confidence)
                if self.agent_confidence else 0.5
            )
        }
