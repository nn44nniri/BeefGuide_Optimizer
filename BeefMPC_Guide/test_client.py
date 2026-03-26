from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import grpc
import pandas as pd

from . import guide_pb2, guide_pb2_grpc


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = PACKAGE_ROOT / "LiGAPS_Beef" / "FRACHA19982012.csv"


def build_random_request(csv_path: Path, request_id: str, scenario_id: int, window_days: int, seed: int) -> guide_pb2.GuideRequest:
    rng = random.Random(seed)
    df = pd.read_csv(csv_path)
    if len(df) <= window_days:
        start = 0
    else:
        start = rng.randint(0, len(df) - window_days)
    chunk = df.iloc[start:start + window_days].copy()
    days = [
        guide_pb2.ClimateDay(
            wts=int(row.WTS),
            yr=int(row.YR),
            doy=int(row.DOY),
            rad=float(row.RAD),
            mint=float(row.MINT),
            maxt=float(row.MAXT),
            vpr=float(row.VPR),
            wind=float(row.WIND),
            rain=float(row.RAIN),
            aha=float(row.AHA),
            okta=float(row.OKTA),
        )
        for row in chunk.itertuples(index=False)
    ]
    return guide_pb2.GuideRequest(request_id=request_id, scenario_id=scenario_id, climate_history=days)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a random FRACHA climate window to BeefMPC_Guide.")
    parser.add_argument("--socket-path", default="/tmp/beefguide/guide-interface.sock")
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument("--request-id", default="random-window-1")
    parser.add_argument("--scenario-id", type=int, default=1)
    parser.add_argument("--window-days", type=int, default=45)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    request = build_random_request(Path(args.csv), args.request_id, args.scenario_id, args.window_days, args.seed)
    channel = grpc.insecure_channel(f"unix://{args.socket_path}")
    stub = guide_pb2_grpc.BeefGuideServiceStub(channel)
    response = stub.GetDailyGuide(request)

    payload = {
        "request_id": response.request_id,
        "scenario_id": response.scenario_id,
        "target_demands": {
            "air_temperature_c": [response.air_temperature_c.lower, response.air_temperature_c.upper],
            "relative_humidity_pct": [response.relative_humidity_pct.lower, response.relative_humidity_pct.upper],
            "air_velocity_mps": [response.air_velocity_mps.lower, response.air_velocity_mps.upper],
        },
        "priority": response.priority,
        "expected_effect": {
            "beef_gain_kg_next_24h": response.expected_effect.beef_gain_kg_next_24h,
            "feed_intake_kg_dm_next_24h": response.expected_effect.feed_intake_kg_dm_next_24h,
            "feed_efficiency_change_g_beef_per_kg_dm": response.expected_effect.feed_efficiency_change_g_beef_per_kg_dm,
        },
        "dominant_limiting_factor": response.dominant_limiting_factor,
        "risk_level": response.risk_level,
        "economic_score": response.economic_score,
        "engine": response.engine,
        "notes": response.notes,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
