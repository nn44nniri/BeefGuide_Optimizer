from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from .engine_adapter import LiGAPSRunResult, climate_rows_to_dataframe, run_ligaps_engine


@dataclass
class GuidanceResult:
    air_temperature_c: tuple[float, float]
    relative_humidity_pct: tuple[float, float]
    air_velocity_mps: tuple[float, float]
    priority: str
    beef_gain_kg_next_24h: float
    feed_intake_kg_dm_next_24h: float
    feed_efficiency_change_g_beef_per_kg_dm: float
    dominant_limiting_factor: str
    risk_level: str
    economic_score: float
    notes: str
    engine: str = "LiGAPS-Beef + BeefMPC-Guide"


class BeefMPCGuideOptimizer:
    """Lightweight Economic MPC guidance layer.

    The white-box LiGAPS-Beef herd simulator is used as the biological engine.
    Then a lightweight economic guidance layer computes x_2 as a daily target-
    demand package for the lower climate optimizer.
    """

    def __init__(self, lambda_feed: float = 1.0, lambda_beef: float = 1.5, lambda_stress: float = 0.8, lambda_control: float = 0.15) -> None:
        self.lambda_feed = lambda_feed
        self.lambda_beef = lambda_beef
        self.lambda_stress = lambda_stress
        self.lambda_control = lambda_control

    def optimize_from_rows(self, climate_rows: Iterable[dict]) -> tuple[GuidanceResult, LiGAPSRunResult]:
        history_df = climate_rows_to_dataframe(climate_rows)
        engine = run_ligaps_engine(history_df)
        guide = self._compute_guidance(history_df, engine)
        return guide, engine

    def _compute_guidance(self, history_df: pd.DataFrame, engine: LiGAPSRunResult) -> GuidanceResult:
        recent = history_df.tail(min(7, len(history_df))).copy()
        temp_mean = ((recent["MINT"] + recent["MAXT"]) / 2.0).mean()
        vpr_mean = recent["VPR"].mean()
        wind_mean = recent["WIND"].mean()
        rain_mean = recent["RAIN"].mean()

        # Lightweight stress surrogates inspired by the Economic MPC formulation.
        # Formula: heat_stress = max(0, T_mean - 22)^2 + 2 * max(0, VPR - 1.8)^2 - 0.25 * WIND
        # Variables: T_mean = recent mean dry-bulb temperature (°C), VPR = vapour pressure (kPa),
        # WIND = recent mean wind speed (m s-1). The wind term reduces heat stress because additional
        # air movement supports convective heat release.
        heat_stress = max(0.0, temp_mean - 22.0) ** 2 + 2.0 * max(0.0, vpr_mean - 1.8) ** 2 - 0.25 * wind_mean

        # Formula: cold_stress = max(0, 8 - T_mean)^2 + 0.15 * WIND + 0.02 * RAIN
        # Variables: T_mean = recent mean temperature (°C), WIND = wind speed (m s-1), RAIN = rainfall (mm day-1).
        # Wind and rain increase effective cold exposure and therefore raise the cold stress penalty.
        cold_stress = max(0.0, 8.0 - temp_mean) ** 2 + 0.15 * wind_mean + 0.02 * rain_mean

        # Formula: humidity_stress = max(0, VPR - 2.0)^2
        # Variable: VPR = recent mean vapour pressure (kPa). This term approximates the ventilation/humidity load
        # that the lower climate optimizer can counter with dampers and cooling.
        humidity_stress = max(0.0, vpr_mean - 2.0) ** 2

        if heat_stress >= cold_stress and heat_stress >= humidity_stress:
            dominant = "heat_stress"
            temp_band = (20.0, 24.0)
            rh_band = (55.0, 70.0)
            velocity_band = (1.2, 1.8)
            priority = "reduce_heat_stress_to_improve_feed_efficiency"
            control_cost = 1.0
        elif cold_stress >= humidity_stress:
            dominant = "cold_stress"
            temp_band = (14.0, 18.0)
            rh_band = (55.0, 70.0)
            velocity_band = (0.4, 0.9)
            priority = "reduce_cold_stress_to_preserve_energy_for_gain"
            control_cost = 0.8
        else:
            dominant = "humidity_load"
            temp_band = (18.0, 22.0)
            rh_band = (50.0, 65.0)
            velocity_band = (1.0, 1.6)
            priority = "use_ventilation_to_limit_vapour_load_with_low_energy_penalty"
            control_cost = 0.6

        total_stress = max(0.0, heat_stress) + max(0.0, cold_stress) + max(0.0, humidity_stress)

        # Economic-MPC-style score used by BeefMPC_Guide.
        # J = lambda_feed * FeedPenalty - lambda_beef * BeefReward + lambda_stress * Stress + lambda_control * U
        # Here FeedPenalty is inversely linked to herd feed efficiency from the LiGAPS engine, BeefReward is linked
        # to engine beef production, Stress is the climate surrogate above, and U is the expected actuator effort.
        feed_penalty = 1000.0 / max(engine.feed_efficiency_herd_g_beef_per_kg_dm, 1e-6)
        beef_reward = engine.beef_production_herd_kg / 100.0
        economic_score = (
            self.lambda_feed * feed_penalty
            - self.lambda_beef * beef_reward
            + self.lambda_stress * total_stress
            + self.lambda_control * control_cost
        )

        # The next-24h expected effect is a lightweight guidance estimate. It is intentionally simple because the
        # lower climate optimizer will close the loop with the sensors and actuators every day.
        stress_reduction = max(0.1, min(1.5, total_stress / 10.0 + 0.15))
        beef_gain_delta = 0.12 * stress_reduction
        feed_delta = -0.22 * stress_reduction
        fe_delta = 7.5 * stress_reduction

        if total_stress >= 9.0:
            risk = "high"
        elif total_stress >= 3.0:
            risk = "moderate"
        else:
            risk = "low"

        notes = (
            f"LiGAPS-Beef herd feed efficiency={engine.feed_efficiency_herd_g_beef_per_kg_dm:.2f} g beef/kg DM; "
            f"beef production={engine.beef_production_herd_kg:.2f} kg. "
            f"The target bands are daily demands x_2 for the lower heater/cooler/damper optimizer, not direct actuator commands."
        )

        return GuidanceResult(
            air_temperature_c=temp_band,
            relative_humidity_pct=rh_band,
            air_velocity_mps=velocity_band,
            priority=priority,
            beef_gain_kg_next_24h=round(beef_gain_delta, 3),
            feed_intake_kg_dm_next_24h=round(feed_delta, 3),
            feed_efficiency_change_g_beef_per_kg_dm=round(fe_delta, 3),
            dominant_limiting_factor=dominant,
            risk_level=risk,
            economic_score=round(economic_score, 3),
            notes=notes,
        )
