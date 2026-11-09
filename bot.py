
#!/usr/bin/env python3
"""
MOONX AUTOTRADER
XAU/USD - M15
Mode simulation uniquement.
Aucun ordre réel n'est envoyé.
"""

import json
import argparse
from pathlib import Path


RISK_PERCENT = 1.0
DAILY_MAX_LOSS_PERCENT = 2.0
REWARD_RISK = 2.0
TIME_EXIT_MINUTES = 60

ALLOWED_SESSIONS = [
    ("09:00", "12:00"),
    ("14:30", "18:00"),
]


def analyze(candles, stop_buffer=0.0):
    """
    candles : liste chronologique de bougies M15.
    Chaque bougie contient open, high, low, close.
    """

    if len(candles) < 5:
        return {"status": "INSUFFICIENT_DATA"}

    previous = candles[-5:-1]
    signal = candles[-1]

    previous_low = min(float(c["low"]) for c in previous)

    signal_low = float(signal["low"])
    signal_close = float(signal["close"])

    liquidity_sweep = signal_low < previous_low
    reclaim = signal_close > previous_low

    if not (liquidity_sweep and reclaim):
        return {
            "status": "NO_SIGNAL",
            "reason": "Aucun sweep de liquidité confirmé"
        }

    entry = signal_close
    stop_loss = signal_low - max(0.0, stop_buffer)

    risk = entry - stop_loss

    if risk <= 0:
        return {"status": "INVALID_SETUP"}

    take_profit = entry + (risk * REWARD_RISK)

    return {
        "status": "SIMULATED_SIGNAL",
        "market": "XAUUSD",
        "timeframe": "M15",
        "side": "BUY",
        "reference_entry": round(entry, 3),
        "stop_loss": round(stop_loss, 3),
        "take_profit": round(take_profit, 3),
        "risk_distance": round(risk, 3),
        "risk_percent": RISK_PERCENT,
        "reward_risk": REWARD_RISK,
        "time_exit_minutes": TIME_EXIT_MINUTES,
        "execution": "DISABLED"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candles", type=Path)
    parser.add_argument("--stop-buffer", type=float, default=0.0)
    args = parser.parse_args()

    if not args.candles:
        parser.print_help()
        return

    candles = json.loads(
        args.candles.read_text(encoding="utf-8")
    )

    result = analyze(candles, args.stop_buffer)

    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ))


if __name__ == "__main__":
    main()
