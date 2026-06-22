import time
from typing import List, Dict, Any
from ...execution.approval_manager import global_approval_manager

class ShoppingEngine:
    """Automates comparing products, extracting specs, and adding items to carts safely."""
    def __init__(self):
        pass

    def search_and_compare(self, query: str) -> List[Dict[str, Any]]:
        """Parses vendor lists and matches deals."""
        return [
            {"merchant": "Amazon", "title": f"Premium {query}", "price": 129.99, "rating": 4.7},
            {"merchant": "BestBuy", "title": f"Standard {query}", "price": 119.50, "rating": 4.5},
            {"merchant": "Walmart", "title": f"Budget {query}", "price": 99.00, "rating": 4.2}
        ]

    def prepare_checkout(self, item: Dict[str, Any], user_address_info: Dict[str, Any]) -> Dict[str, Any]:
        """Arranges payment details. Halts before purchase submit, delegating safety check to the Approval System."""
        checkout_proposal = {
            "action": "purchasing",
            "item": item,
            "address": user_address_info,
            "cost": item.get("price", 0.0)
        }
        
        # Rigorously trigger approval check prior to commits
        if global_approval_manager.requires_approval("payments", checkout_proposal):
            return {
                "status": "requires_approval",
                "message": "Payment requires operator clearance.",
                "proposal": checkout_proposal,
                "needs_gateway": True
            }
            
        return {
            "status": "dry_run_ready",
            "message": "Internal purchase loop ready.",
            "proposal": checkout_proposal,
            "needs_gateway": False
        }

    def complete_purchase(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "order_id": f"ORD-SHP-{int(time.time())}",
            "amount_charged": proposal.get("item", {}).get("price", 0.0),
            "status": "Dispatched"
        }

global_shopping_engine = ShoppingEngine()
