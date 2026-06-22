"""
Monitoring Service — Instruments validation requests, logs execution latencies, tracks model failures, and formats audit logs.
"""
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Global in-memory metrics store (resets on server reboot, persistent per process)
_metrics = {
    "total_requests": 0,
    "failed_requests": 0,
    "total_processing_time": 0.0,
    "agent_audit_trail": [],
    "recent_warnings": []
}

class MonitoringService:
    """Tracks latency, performance scores, audit logs, and runtime stability"""
    
    @staticmethod
    def record_request(duration: float, success: bool = True):
        """Logs high-level request parameters"""
        _metrics["total_requests"] += 1
        if not success:
            _metrics["failed_requests"] += 1
        _metrics["total_processing_time"] += duration

    @staticmethod
    def record_agent_trail(audit_log: Dict[str, Any]):
        """Logs individual agent execution checkpoints"""
        # Cap audit trail cache size to prevent memory leaks
        if len(_metrics["agent_audit_trail"]) > 500:
            _metrics["agent_audit_trail"].pop(0)
            
        _metrics["agent_audit_trail"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            **audit_log
        })

    @staticmethod
    def record_warning(message: str):
        """Tracks warnings for health dashboards"""
        if len(_metrics["recent_warnings"]) > 50:
            _metrics["recent_warnings"].pop(0)
        _metrics["recent_warnings"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "warning": message
        })

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Compiles metric snapshots for monitoring dashboards"""
        total = _metrics["total_requests"]
        avg_time = (_metrics["total_processing_time"] / total) if total > 0 else 0.0
        success_rate = ((total - _metrics["failed_requests"]) / total * 100) if total > 0 else 100.0
        
        return {
            "total_analyses_run": total,
            "success_rate_percentage": round(success_rate, 2),
            "average_duration_seconds": round(avg_time, 3),
            "recent_audit_trail": _metrics["agent_audit_trail"][-20:],
            "system_warnings": _metrics["recent_warnings"]
        }

# Global monitoring instance
monitoring_service = MonitoringService()
