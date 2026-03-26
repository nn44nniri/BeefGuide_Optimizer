from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
LIGAPS_ROOT = PACKAGE_ROOT / "LiGAPS_Beef"


@dataclass
class LiGAPSRunResult:
    """Compact engine result extracted from LiGAPS-Beef.

    The original simulator prints a table to stdout. In this adapter we preserve
    that behaviour, but we also enable an additional JSON side output through an
    environment variable so BeefMPC_Guide can consume the engine deterministically.
    """

    case_number: int
    feed_efficiency_herd_g_beef_per_kg_dm: float
    feed_efficiency_repr_cow_g_beef_per_kg_dm: float
    feed_efficiency_bull_calf_g_beef_per_kg_dm: float
    feed_fraction_repr_cow: float
    beef_production_herd_kg: float
    beef_production_repr_cow_kg: float
    beef_production_bull_calf_kg: float
    slaughter_weight_bull_calf_kg: float
    stdout_tail: str


def climate_rows_to_dataframe(rows: Iterable[dict]) -> pd.DataFrame:
    """Build a weather DataFrame accepted by LiGAPS-Beef.

    LiGAPS-Beef expects the weather columns WTS, YR, DOY, RAD, MINT, MAXT, VPR,
    WIND, RAIN, AHA, and OKTA. The service receives the same structure through
    gRPC and converts it here.
    """

    df = pd.DataFrame(list(rows))
    required = ["WTS", "YR", "DOY", "RAD", "MINT", "MAXT", "VPR", "WIND", "RAIN", "AHA", "OKTA"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing climate columns for LiGAPS-Beef: {missing}")
    return df[required].copy()


def _repeat_weather_for_engine(df: pd.DataFrame, minimum_rows: int = 4500) -> pd.DataFrame:
    """Repeat the received history to a long daily trajectory for the legacy engine.

    The upstream LiGAPS-Beef herd script was written for long multi-year weather
    files. For the guidance service we receive only the observed timeline x_1 up to
    the present day. To keep the original main functionality intact, the adapter
    repeats the received segment until the legacy engine has enough rows to finish
    its herd simulation.
    """

    if df.empty:
        raise ValueError("The climate history x_1 is empty.")
    reps = int(math.ceil(minimum_rows / len(df)))
    tiled = pd.concat([df] * reps, ignore_index=True).iloc[:minimum_rows].copy()
    tiled["WTS"] = range(1, len(tiled) + 1)
    base_year = int(df["YR"].iloc[0]) if not df.empty else 1998
    tiled["YR"] = [base_year + (i // 365) for i in range(len(tiled))]
    tiled["DOY"] = [(i % 365) + 1 for i in range(len(tiled))]
    return tiled


def _write_temp_settings(settings_path: Path) -> None:
    """Create a one-case settings file for the engine adapter.

    The settings keep the original breed library and scenario definitions but make
    execution deterministic by selecting only case 1 during the engine call.
    """

    text = (LIGAPS_ROOT / "settings.json").read_text(encoding="utf-8")
    data = json.loads(_strip_json_comments(text))
    simulation = data.setdefault("simulation", {})
    simulation["case_ids"] = [1]
    settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _strip_json_comments(text: str) -> str:
    out: list[str] = []
    i = 0
    in_string = False
    escape = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == '/' and nxt == '/':
            i += 2
            while i < len(text) and text[i] not in '\r\n':
                i += 1
            continue
        if ch == '/' and nxt == '*':
            i += 2
            while i + 1 < len(text) and not (text[i] == '*' and text[i + 1] == '/'):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def run_ligaps_engine(history_df: pd.DataFrame, timeout_seconds: int = 300) -> LiGAPSRunResult:
    """Run the legacy LiGAPS-Beef herd simulator in an isolated working directory."""

    tiled = _repeat_weather_for_engine(history_df)
    with tempfile.TemporaryDirectory(prefix="beefguide_ligaps_") as tmpdir:
        tmp = Path(tmpdir)
        work_root = tmp / "LiGAPS_Beef"
        shutil.copytree(LIGAPS_ROOT, work_root)

        # Replace the default weather file with the request-specific time-line x_1.
        tiled.to_csv(work_root / "FRACHA19982012.csv", index=False)
        settings_path = work_root / "settings_runtime.json"
        _write_temp_settings(settings_path)
        output_json = work_root / "ligaps_output.json"

        env = os.environ.copy()
        env["LIGAPS_SETTINGS_FILENAME"] = str(settings_path)
        env["LIGAPS_OUTPUT_JSON"] = str(output_json)
        env["LIGAPS_SHOW_PROGRESS"] = "0"

        proc = subprocess.run(
            ["python3", str(work_root / "LiGAPSBeef_herd.py")],
            cwd=work_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=True,
        )

        payload = json.loads(output_json.read_text(encoding="utf-8"))
        return LiGAPSRunResult(
            case_number=int(payload["case_number"]),
            feed_efficiency_herd_g_beef_per_kg_dm=float(payload["feed_efficiency_herd_g_beef_per_kg_dm"]),
            feed_efficiency_repr_cow_g_beef_per_kg_dm=float(payload["feed_efficiency_repr_cow_g_beef_per_kg_dm"]),
            feed_efficiency_bull_calf_g_beef_per_kg_dm=float(payload["feed_efficiency_bull_calf_g_beef_per_kg_dm"]),
            feed_fraction_repr_cow=float(payload["feed_fraction_repr_cow"]),
            beef_production_herd_kg=float(payload["beef_production_herd_kg"]),
            beef_production_repr_cow_kg=float(payload["beef_production_repr_cow_kg"]),
            beef_production_bull_calf_kg=float(payload["beef_production_bull_calf_kg"]),
            slaughter_weight_bull_calf_kg=float(payload["slaughter_weight_bull_calf_kg"]),
            stdout_tail="\n".join(proc.stdout.splitlines()[-12:]),
        )
