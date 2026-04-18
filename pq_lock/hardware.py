from __future__ import annotations

from abc import ABC, abstractmethod


class LockHardware(ABC):
    """Abstraction for the physical actuator behind the lock."""

    @abstractmethod
    def engage_lock(self) -> None:
        """Move hardware into the locked state."""

    @abstractmethod
    def actuate_unlock(self) -> None:
        """Trigger the physical unlock action."""


class MockLockHardware(LockHardware):
    """Laptop-safe hardware implementation used by the software demo."""

    def __init__(self) -> None:
        self.is_locked = True
        self.unlock_count = 0

    def engage_lock(self) -> None:
        self.is_locked = True

    def actuate_unlock(self) -> None:
        self.is_locked = False
        self.unlock_count += 1


class ServoLockHardware(LockHardware):
    """
    Placeholder for a future servo-backed actuator.

    GPIO and PWM code should stay isolated inside this class when hardware
    support is added on Raspberry Pi or similar targets.
    """

    def __init__(self, pin: int, unlock_angle: float = 90.0, locked_angle: float = 0.0) -> None:
        self.pin = pin
        self.unlock_angle = unlock_angle
        self.locked_angle = locked_angle

    def engage_lock(self) -> None:
        raise NotImplementedError("Servo GPIO control is not implemented yet.")

    def actuate_unlock(self) -> None:
        raise NotImplementedError("Servo GPIO control is not implemented yet.")
