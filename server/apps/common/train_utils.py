from pathlib import Path
from typing import Tuple


def ppo_loop(weights: Path, data: Path, steps: int, lr: float) -> Tuple[float, float, float, float, float]:
    """Simulated PPO loop returning dummy metrics."""
    delta = 0.0
    reward = 0.0
    for _ in range(steps):
        delta += 0.01 * lr
        reward += 0.1
    reward /= steps
    kl = 0.01 * lr
    loss_before = 1.0
    loss_after = loss_before - delta * 0.1
    return delta, reward, kl, loss_before, loss_after
