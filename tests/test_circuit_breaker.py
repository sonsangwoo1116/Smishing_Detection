import time
from src.core.circuit_breaker import CircuitBreaker, CircuitState


def test_initial_state():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True


def test_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False


def test_success_resets():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_half_open_after_timeout():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    time.sleep(0.15)
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN
