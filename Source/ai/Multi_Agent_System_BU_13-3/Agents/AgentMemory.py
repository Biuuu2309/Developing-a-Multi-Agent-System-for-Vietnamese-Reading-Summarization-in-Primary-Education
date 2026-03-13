from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class AgentMemory:
    """
    Internal Memory cho từng Agent
    Lưu trữ:
    - Past experiences
    - Successful strategies
    - Failed attempts
    - Context patterns
    """
    
    def __init__(self, agent_name: str, max_memory_size: int = 100):
        self.agent_name = agent_name
        self.max_memory_size = max_memory_size
        self.experiences: List[Dict[str, Any]] = []
        self.successful_patterns: Dict[str, Any] = {}
        self.failed_patterns: Dict[str, Any] = {}
        self.context_cache: Dict[str, Any] = {}
    
    def store_experience(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        output: Any,
        success: bool,
        metrics: Optional[Dict[str, float]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Lưu trữ một experience"""
        experience = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "input": input_data,
            "output": output,
            "success": success,
            "metrics": metrics or {},
            "context": context or {}
        }
        
        self.experiences.append(experience)
        
        # Giới hạn kích thước memory
        if len(self.experiences) > self.max_memory_size:
            self.experiences.pop(0)
        
        # Cập nhật patterns
        if success:
            self._update_successful_pattern(task_type, input_data, metrics)
        else:
            self._update_failed_pattern(task_type, input_data)
    
    def _update_successful_pattern(self, task_type: str, input_data: Dict, metrics: Dict):
        """Cập nhật successful patterns"""
        if task_type not in self.successful_patterns:
            self.successful_patterns[task_type] = {
                "count": 0,
                "avg_metrics": {},
                "best_metrics": {},
                "common_inputs": []
            }
        
        pattern = self.successful_patterns[task_type]
        pattern["count"] += 1
        
        # Cập nhật average metrics
        if metrics:
            for key, value in metrics.items():
                # Chỉ xử lý metrics là số
                try:
                    # Convert value sang float nếu có thể
                    if isinstance(value, str):
                        # Bỏ qua nếu là string không phải số
                        continue
                    value_float = float(value)
                    
                    if key not in pattern["avg_metrics"]:
                        pattern["avg_metrics"][key] = value_float
                        pattern["best_metrics"][key] = value_float
                    else:
                        # Đảm bảo avg_metrics[key] là số
                        current_avg = pattern["avg_metrics"][key]
                        if isinstance(current_avg, str):
                            # Nếu đã lưu là string, reset về value hiện tại
                            pattern["avg_metrics"][key] = value_float
                            pattern["best_metrics"][key] = value_float
                        else:
                            # Moving average
                            pattern["avg_metrics"][key] = (
                                float(current_avg) * (pattern["count"] - 1) + value_float
                            ) / pattern["count"]
                            
                            # Best metrics
                            current_best = pattern["best_metrics"][key]
                            if isinstance(current_best, str):
                                pattern["best_metrics"][key] = value_float
                            elif value_float > float(current_best):
                                pattern["best_metrics"][key] = value_float
                except (ValueError, TypeError):
                    # Bỏ qua nếu không convert được sang số
                    continue
    
    def _update_failed_pattern(self, task_type: str, input_data: Dict):
        """Cập nhật failed patterns"""
        if task_type not in self.failed_patterns:
            self.failed_patterns[task_type] = {
                "count": 0,
                "common_inputs": []
            }
        
        self.failed_patterns[task_type]["count"] += 1
    
    def retrieve_similar_experiences(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Tìm các experiences tương tự"""
        similar = []
        
        for exp in reversed(self.experiences):
            if exp["task_type"] == task_type:
                # Simple similarity check (có thể cải thiện với embedding)
                similarity = self._calculate_similarity(exp["input"], input_data)
                if similarity > 0.5:
                    similar.append({**exp, "similarity": similarity})
        
        # Sort by similarity và limit
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        return similar[:limit]
    
    def _calculate_similarity(self, input1: Dict, input2: Dict) -> float:
        """Tính similarity giữa 2 inputs (đơn giản)"""
        common_keys = set(input1.keys()) & set(input2.keys())
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if input1[key] == input2[key]:
                matches += 1
        
        return matches / len(common_keys) if common_keys else 0.0
    
    def get_best_strategy(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Lấy strategy tốt nhất cho task type"""
        if task_type in self.successful_patterns:
            return {
                "pattern": self.successful_patterns[task_type],
                "recommendation": "Dựa trên " + str(self.successful_patterns[task_type]["count"]) + " lần thành công"
            }
        return None
    
    def cache_context(self, key: str, value: Any):
        """Cache context để tái sử dụng"""
        self.context_cache[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_cached_context(self, key: str) -> Optional[Any]:
        """Lấy cached context"""
        if key in self.context_cache:
            return self.context_cache[key]["value"]
        return None
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Lấy summary của memory"""
        return {
            "agent_name": self.agent_name,
            "total_experiences": len(self.experiences),
            "successful_patterns": len(self.successful_patterns),
            "failed_patterns": len(self.failed_patterns),
            "cached_contexts": len(self.context_cache)
        }
