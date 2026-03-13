from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
from collections import defaultdict


class ToolMemory:
    """
    Tool Usage Memory
    Ghi nhớ việc sử dụng tools:
    - Tool usage history
    - Success/failure rates
    - Tool preferences
    - Tool combinations
    """
    
    def __init__(self, storage_path: str = "memory_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.tool_usage_file = self.storage_path / "tool_usage.json"
        
        # In-memory storage
        self.tool_usage: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.tool_stats: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load tool usage data"""
        if self.tool_usage_file.exists():
            try:
                with open(self.tool_usage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tool_usage = defaultdict(list, data.get("usage", {}))
                    self.tool_stats = data.get("stats", {})
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_data(self):
        """Save tool usage data"""
        try:
            data = {
                "usage": dict(self.tool_usage),
                "stats": self.tool_stats,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.tool_usage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving tool usage: {e}")
    
    def record_tool_usage(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        output: Any,
        success: bool,
        execution_time: Optional[float] = None,
        agent_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Ghi lại việc sử dụng tool"""
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_data,
            "output": str(output)[:500],  # Limit output length
            "success": success,
            "execution_time": execution_time,
            "agent_name": agent_name,
            "context": context or {}
        }
        
        self.tool_usage[tool_name].append(usage_entry)
        
        # Giới hạn số lượng entries per tool (giữ 200 gần nhất)
        if len(self.tool_usage[tool_name]) > 200:
            self.tool_usage[tool_name] = self.tool_usage[tool_name][-200:]
        
        # Update statistics
        self._update_stats(tool_name)
        
        # Auto-save
        self._save_data()
    
    def _update_stats(self, tool_name: str):
        """Cập nhật statistics cho tool"""
        usages = self.tool_usage[tool_name]
        
        if not usages:
            return
        
        total = len(usages)
        successful = sum(1 for u in usages if u.get("success", False))
        failed = total - successful
        
        execution_times = [u.get("execution_time") for u in usages if u.get("execution_time")]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else None
        
        # Recent performance (last 20 uses)
        recent_usages = usages[-20:]
        recent_successful = sum(1 for u in recent_usages if u.get("success", False))
        recent_success_rate = recent_successful / len(recent_usages) if recent_usages else 0.0
        
        self.tool_stats[tool_name] = {
            "total_uses": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "recent_success_rate": recent_success_rate,
            "avg_execution_time": avg_time,
            "last_used": usages[-1]["timestamp"] if usages else None
        }
    
    def get_tool_stats(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Lấy statistics của tool"""
        return self.tool_stats.get(tool_name)
    
    def get_all_tool_stats(self) -> Dict[str, Dict[str, Any]]:
        """Lấy statistics của tất cả tools"""
        return self.tool_stats.copy()
    
    def get_tool_history(
        self,
        tool_name: str,
        limit: Optional[int] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Lấy history sử dụng tool"""
        usages = self.tool_usage.get(tool_name, [])
        
        if success_only:
            usages = [u for u in usages if u.get("success", False)]
        
        if limit:
            return usages[-limit:]
        
        return usages
    
    def get_tool_combinations(
        self,
        tool_name: str,
        limit: int = 5
    ) -> List[Tuple[str, int]]:
        """Lấy các tool thường được dùng cùng với tool này"""
        usages = self.tool_usage.get(tool_name, [])
        
        # Tìm tools được dùng trong cùng context
        combination_count = defaultdict(int)
        
        for usage in usages:
            context = usage.get("context", {})
            other_tools = context.get("other_tools", [])
            for other_tool in other_tools:
                if other_tool != tool_name:
                    combination_count[other_tool] += 1
        
        # Sort và return top combinations
        sorted_combinations = sorted(
            combination_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_combinations[:limit]
    
    def get_recommended_tools(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Đề xuất tools dựa trên task type và context"""
        recommendations = []
        
        # Tìm tools có success rate cao cho task type tương tự
        for tool_name, stats in self.tool_stats.items():
            if stats.get("recent_success_rate", 0) > 0.7:
                # Check nếu tool đã được dùng cho task type tương tự
                usages = self.tool_usage.get(tool_name, [])
                similar_tasks = sum(
                    1 for u in usages[-20:]
                    if u.get("context", {}).get("task_type") == task_type
                )
                
                if similar_tasks > 0:
                    recommendations.append({
                        "tool_name": tool_name,
                        "success_rate": stats.get("recent_success_rate", 0),
                        "similar_task_count": similar_tasks,
                        "avg_execution_time": stats.get("avg_execution_time")
                    })
        
        # Sort by success rate và similar task count
        recommendations.sort(
            key=lambda x: (x["success_rate"], x["similar_task_count"]),
            reverse=True
        )
        
        return recommendations[:5]
    
    def get_tool_usage_summary(self) -> Dict[str, Any]:
        """Lấy summary của tool usage"""
        return {
            "total_tools": len(self.tool_stats),
            "total_uses": sum(s.get("total_uses", 0) for s in self.tool_stats.values()),
            "most_used_tools": sorted(
                self.tool_stats.items(),
                key=lambda x: x[1].get("total_uses", 0),
                reverse=True
            )[:5],
            "most_reliable_tools": sorted(
                self.tool_stats.items(),
                key=lambda x: x[1].get("recent_success_rate", 0),
                reverse=True
            )[:5]
        }
