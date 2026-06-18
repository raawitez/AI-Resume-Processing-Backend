import time
from collections import defaultdict
from threading import Lock

class MetricsTracker:

    def __init__(self):
        self._lock           = Lock()
        self.total_requests  = 0
        self.total_errors    = 0
        self.requests_by_path = defaultdict(int)
        self.errors_by_path   = defaultdict(int)
        self.response_times   = []
        self.start_time       = time.time()

    def record(self, path: str, status: int, duration_ms: float):
        with self._lock:
            self.total_requests += 1
            self.requests_by_path[path] += 1
            self.response_times.append(duration_ms)
            if len(self.response_times) > 100:
                self.response_times.pop(0)
            if status >= 400:
                self.total_errors += 1
                self.errors_by_path[path] += 1

    def summary(self) -> dict:
        with self._lock:
            avg = (
                sum(self.response_times) / len(self.response_times)
                if self.response_times else 0
            )
            error_rate = (
                self.total_errors / self.total_requests * 100
                if self.total_requests > 0 else 0
            )
            top = sorted(
                self.requests_by_path.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            return {
                "uptime_seconds":     int(time.time() - self.start_time),
                "total_requests":     self.total_requests,
                "total_errors":       self.total_errors,
                "error_rate_percent": round(error_rate, 2),
                "avg_response_ms":    round(avg, 2),
                "top_endpoints":      dict(top),
                "errors_by_endpoint": dict(self.errors_by_path)
            }

metrics = MetricsTracker()