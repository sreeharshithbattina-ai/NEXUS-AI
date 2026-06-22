import time
from typing import Dict, Any, List
from ..interfaces import ITransactionEngine
from ...execution.approval_manager import global_approval_manager

class BookingEngine(ITransactionEngine):
    """Enables web automation for reservation preparation, wrapping operations into safety check bounds."""
    def __init__(self):
        pass

    def compare_deals(self, query: str) -> List[Dict[str, Any]]:
        """Queries travel sites. Returns comparative deals matrices."""
        return [
            {"provider": "Expedia", "item": f"Flight to {query}", "price": 420.0, "duration_hours": 8.5},
            {"provider": "Kayak", "item": f"Flight to {query}", "price": 395.0, "duration_hours": 9.0},
            {"provider": "Skyscanner", "item": f"Flight to {query}", "price": 380.0, "duration_hours": 11.2},
        ]

    def prepare_reservation(self, service: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Arranges booking detail forms, but suspends loop execution until safety approval check is cleared."""
        booking_summary = f"Reserve {service} via Kayak. Details: {details}"
        
        # Rigorously trigger approval check prior to commits
        if global_approval_manager.requires_approval("bookings", details):
            # Create safety proposal
            return {
                "status": "requires_approval",
                "summary": booking_summary,
                "needs_gateway": True,
                "payload": details
            }
            
        return {
            "status": "reserved_dry_run",
            "summary": booking_summary,
            "needs_gateway": False,
            "payload": details
        }

    def execute_secured_submit(self, checkout_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes final booking submit post-approval."""
        return {
            "success": True,
            "confirmation_code": f"CONF-TRS-{int(time.time())}",
            "receipt_total": checkout_payload.get("price", 395.0),
            "timestamp": time.time()
        }

global_booking_engine = BookingEngine()
