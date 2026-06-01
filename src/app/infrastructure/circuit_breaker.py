from time import time


class CircuitBreaker:
    def __init__(self, failure_limit: int = 2, recovery_seconds: int = 20):
        self.failure_limit = failure_limit
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.opened_at = 0.0

    def is_open(self) -> bool:
        if self.failures < self.failure_limit:
            return False
        if time() - self.opened_at >= self.recovery_seconds:
            self.failures = 0
            self.opened_at = 0.0
            return False
        return True

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = 0.0

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_limit:
            self.opened_at = time()
