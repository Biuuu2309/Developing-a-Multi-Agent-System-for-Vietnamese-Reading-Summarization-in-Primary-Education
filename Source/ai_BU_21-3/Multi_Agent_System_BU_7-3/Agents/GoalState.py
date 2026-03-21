from typing import Dict, List, Any, Optional, Literal
from enum import Enum
from datetime import datetime


class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GoalState:
    """
    Goal State Management
    Quản lý mục tiêu và trạng thái của hệ thống
    """
    
    def __init__(self):
        self.goals: List[Dict[str, Any]] = []
        self.current_goal_id: Optional[str] = None
        self.goal_history: List[Dict[str, Any]] = []
    
    def create_goal(
        self,
        goal_type: str,
        description: str,
        requirements: Dict[str, Any],
        priority: int = 5
    ) -> str:
        """Tạo goal mới"""
        goal_id = f"goal_{len(self.goals)}_{datetime.now().timestamp()}"
        
        goal = {
            "id": goal_id,
            "type": goal_type,
            "description": description,
            "requirements": requirements,
            "priority": priority,
            "status": GoalStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "subgoals": [],
            "constraints": [],
            "success_criteria": {}
        }
        
        self.goals.append(goal)
        self.current_goal_id = goal_id
        
        return goal_id
    
    def set_current_goal(self, goal_id: str):
        """Set goal hiện tại"""
        if any(g["id"] == goal_id for g in self.goals):
            self.current_goal_id = goal_id
    
    def get_current_goal(self) -> Optional[Dict[str, Any]]:
        """Lấy goal hiện tại"""
        if self.current_goal_id:
            for goal in self.goals:
                if goal["id"] == self.current_goal_id:
                    return goal
        return None
    
    def update_goal_status(
        self,
        goal_id: str,
        status: GoalStatus,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Cập nhật trạng thái goal"""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["status"] = status.value
                goal["updated_at"] = datetime.now().isoformat()
                if metadata:
                    goal.update(metadata)
                
                # Lưu vào history
                self.goal_history.append({
                    "goal_id": goal_id,
                    "status": status.value,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata or {}
                })
                break
    
    def add_subgoal(self, parent_goal_id: str, subgoal: Dict[str, Any]):
        """Thêm subgoal"""
        for goal in self.goals:
            if goal["id"] == parent_goal_id:
                subgoal_id = f"subgoal_{len(goal['subgoals'])}_{datetime.now().timestamp()}"
                subgoal["id"] = subgoal_id
                subgoal["status"] = GoalStatus.PENDING.value
                goal["subgoals"].append(subgoal)
                break
    
    def check_goal_achievement(
        self,
        goal_id: str,
        results: Dict[str, Any]
    ) -> bool:
        """Kiểm tra xem goal đã đạt được chưa"""
        goal = next((g for g in self.goals if g["id"] == goal_id), None)
        if not goal:
            return False
        
        success_criteria = goal.get("success_criteria", {})
        
        # Kiểm tra các criteria
        if not success_criteria or not isinstance(success_criteria, dict):
            # Nếu không có criteria, coi như đã đạt được
            return True
        
        for criterion, threshold in success_criteria.items():
            if criterion in results:
                if results[criterion] < threshold:
                    return False
            else:
                return False
        
        return True
    
    def get_goal_progress(self, goal_id: str) -> Dict[str, Any]:
        """Lấy tiến độ của goal"""
        goal = next((g for g in self.goals if g["id"] == goal_id), None)
        if not goal:
            return {"progress": 0, "status": "not_found"}
        
        total_subgoals = len(goal.get("subgoals", []))
        completed_subgoals = sum(
            1 for sg in goal.get("subgoals", [])
            if sg.get("status") == GoalStatus.ACHIEVED.value
        )
        
        progress = (completed_subgoals / total_subgoals * 100) if total_subgoals > 0 else 0
        
        return {
            "goal_id": goal_id,
            "status": goal["status"],
            "progress": progress,
            "completed_subgoals": completed_subgoals,
            "total_subgoals": total_subgoals
        }
    
    def get_all_goals(self) -> List[Dict[str, Any]]:
        """Lấy tất cả goals"""
        return self.goals
    
    def clear_completed_goals(self):
        """Xóa các goals đã hoàn thành"""
        self.goals = [
            g for g in self.goals
            if g["status"] not in [GoalStatus.ACHIEVED.value, GoalStatus.CANCELLED.value]
        ]
