from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class NegotiationStatus(Enum):
    INITIATED = "initiated"
    PROPOSED = "proposed"
    COUNTERED = "countered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class NegotiationAgent:
    """
    Negotiation Mechanism giữa các Agents
    Cho phép agents đàm phán về:
    - Strategy selection
    - Resource allocation
    - Task assignment
    - Parameter adjustment
    """
    
    def __init__(self):
        self.negotiations: Dict[str, Dict[str, Any]] = {}
        self.negotiation_history: List[Dict[str, Any]] = []
        self.agent_preferences: Dict[str, Dict[str, Any]] = {}
    
    def initiate_negotiation(
        self,
        negotiation_id: str,
        initiator: str,
        participants: List[str],
        topic: str,
        initial_proposal: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Khởi tạo negotiation"""
        negotiation = {
            "id": negotiation_id,
            "initiator": initiator,
            "participants": participants,
            "topic": topic,
            "status": NegotiationStatus.INITIATED.value,
            "proposals": [{
                "agent": initiator,
                "proposal": initial_proposal,
                "timestamp": datetime.now().isoformat(),
                "round": 1
            }],
            "responses": {},
            "constraints": constraints or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "max_rounds": 5,
            "current_round": 1
        }
        
        self.negotiations[negotiation_id] = negotiation
        
        return negotiation
    
    def propose(
        self,
        negotiation_id: str,
        agent: str,
        proposal: Dict[str, Any],
        reasoning: Optional[str] = None
    ) -> bool:
        """Đưa ra proposal mới"""
        if negotiation_id not in self.negotiations:
            return False
        
        negotiation = self.negotiations[negotiation_id]
        
        # Kiểm tra xem agent có trong participants không
        if agent not in negotiation["participants"]:
            return False
        
        # Kiểm tra max rounds
        if negotiation["current_round"] >= negotiation["max_rounds"]:
            negotiation["status"] = NegotiationStatus.TIMEOUT.value
            return False
        
        # Thêm proposal
        negotiation["proposals"].append({
            "agent": agent,
            "proposal": proposal,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
            "round": negotiation["current_round"]
        })
        
        negotiation["current_round"] += 1
        negotiation["status"] = NegotiationStatus.PROPOSED.value
        negotiation["updated_at"] = datetime.now().isoformat()
        
        return True
    
    def respond(
        self,
        negotiation_id: str,
        agent: str,
        response: str,  # "accept", "reject", "counter"
        counter_proposal: Optional[Dict[str, Any]] = None,
        reasoning: Optional[str] = None
    ) -> bool:
        """Trả lời proposal"""
        if negotiation_id not in self.negotiations:
            return False
        
        negotiation = self.negotiations[negotiation_id]
        
        if agent not in negotiation["participants"]:
            return False
        
        negotiation["responses"][agent] = {
            "response": response,
            "counter_proposal": counter_proposal,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cập nhật status
        if response == "accept":
            # Kiểm tra xem tất cả đã accept chưa
            all_accepted = all(
                resp.get("response") == "accept"
                for resp in negotiation["responses"].values()
            )
            if all_accepted:
                negotiation["status"] = NegotiationStatus.ACCEPTED.value
            else:
                negotiation["status"] = NegotiationStatus.PROPOSED.value
        elif response == "reject":
            negotiation["status"] = NegotiationStatus.REJECTED.value
        elif response == "counter" and counter_proposal:
            negotiation["status"] = NegotiationStatus.COUNTERED.value
            # Tự động tạo proposal mới từ counter
            self.propose(negotiation_id, agent, counter_proposal, reasoning)
        
        negotiation["updated_at"] = datetime.now().isoformat()
        
        return True
    
    def get_negotiation_result(self, negotiation_id: str) -> Optional[Dict[str, Any]]:
        """Lấy kết quả negotiation"""
        if negotiation_id not in self.negotiations:
            return None
        
        negotiation = self.negotiations[negotiation_id]
        
        if negotiation["status"] == NegotiationStatus.ACCEPTED.value:
            # Lấy proposal cuối cùng được accept
            last_proposal = negotiation["proposals"][-1]
            return {
                "status": "accepted",
                "final_proposal": last_proposal["proposal"],
                "agreed_by": list(negotiation["responses"].keys()),
                "rounds": negotiation["current_round"]
            }
        elif negotiation["status"] == NegotiationStatus.REJECTED.value:
            return {
                "status": "rejected",
                "reason": "Proposal bị reject bởi một hoặc nhiều participants"
            }
        elif negotiation["status"] == NegotiationStatus.TIMEOUT.value:
            return {
                "status": "timeout",
                "reason": "Đạt max rounds"
            }
        else:
            return {
                "status": "in_progress",
                "current_round": negotiation["current_round"]
            }
    
    def negotiate_strategy(
        self,
        agents: List[str],
        options: List[str],
        preferences: Optional[Dict[str, Dict[str, float]]] = None
    ) -> Optional[str]:
        """
        Negotiate về strategy selection
        Returns: strategy được chọn hoặc None nếu không đạt được thỏa thuận
        """
        negotiation_id = f"strategy_{datetime.now().timestamp()}"
        
        # Initial proposal: chọn strategy phổ biến nhất
        initial_proposal = {"strategy": options[0] if options else "abstractive"}
        
        negotiation = self.initiate_negotiation(
            negotiation_id,
            agents[0],
            agents,
            "strategy_selection",
            initial_proposal
        )
        
        # Mỗi agent đưa ra preference
        for agent in agents:
            if preferences and agent in preferences:
                agent_prefs = preferences[agent]
                # Chọn strategy có preference cao nhất
                if agent_prefs and isinstance(agent_prefs, dict):
                    best_strategy = max(agent_prefs.items(), key=lambda x: x[1])[0]
                    if best_strategy in options:
                        self.propose(
                            negotiation_id,
                            agent,
                            {"strategy": best_strategy},
                            f"Agent {agent} prefers {best_strategy}"
                        )
        
        # Simple voting mechanism
        strategy_votes = {}
        for proposal in negotiation["proposals"]:
            strategy = proposal["proposal"].get("strategy")
            if strategy:
                strategy_votes[strategy] = strategy_votes.get(strategy, 0) + 1
        
        if strategy_votes:
            # Chọn strategy có nhiều vote nhất
            chosen_strategy = max(strategy_votes.items(), key=lambda x: x[1])[0]
            
            # Tất cả agents accept
            for agent in agents:
                self.respond(negotiation_id, agent, "accept")
            
            return chosen_strategy
        
        return None
    
    def get_negotiation_history(self, agent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy negotiation history"""
        if agent:
            return [
                n for n in self.negotiation_history
                if agent in n.get("participants", [])
            ]
        return self.negotiation_history
