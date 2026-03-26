from __future__ import annotations

import argparse
import os
import stat
from concurrent import futures

import grpc

from . import guide_pb2, guide_pb2_grpc
from .optimizer import BeefMPCGuideOptimizer


class BeefGuideService(guide_pb2_grpc.BeefGuideServiceServicer):
    def __init__(self) -> None:
        self.optimizer = BeefMPCGuideOptimizer()

    def GetDailyGuide(self, request: guide_pb2.GuideRequest, context: grpc.ServicerContext) -> guide_pb2.GuideResponse:
        rows = [
            {
                "WTS": day.wts,
                "YR": day.yr,
                "DOY": day.doy,
                "RAD": day.rad,
                "MINT": day.mint,
                "MAXT": day.maxt,
                "VPR": day.vpr,
                "WIND": day.wind,
                "RAIN": day.rain,
                "AHA": day.aha,
                "OKTA": day.okta,
            }
            for day in request.climate_history
        ]
        guide, engine = self.optimizer.optimize_from_rows(rows)
        return guide_pb2.GuideResponse(
            request_id=request.request_id,
            scenario_id=request.scenario_id,
            air_temperature_c=guide_pb2.TargetBand(lower=guide.air_temperature_c[0], upper=guide.air_temperature_c[1]),
            relative_humidity_pct=guide_pb2.TargetBand(lower=guide.relative_humidity_pct[0], upper=guide.relative_humidity_pct[1]),
            air_velocity_mps=guide_pb2.TargetBand(lower=guide.air_velocity_mps[0], upper=guide.air_velocity_mps[1]),
            priority=guide.priority,
            expected_effect=guide_pb2.ExpectedEffect(
                beef_gain_kg_next_24h=guide.beef_gain_kg_next_24h,
                feed_intake_kg_dm_next_24h=guide.feed_intake_kg_dm_next_24h,
                feed_efficiency_change_g_beef_per_kg_dm=guide.feed_efficiency_change_g_beef_per_kg_dm,
            ),
            dominant_limiting_factor=guide.dominant_limiting_factor,
            risk_level=guide.risk_level,
            economic_score=guide.economic_score,
            engine=f"{guide.engine}; case={engine.case_number}",
            notes=guide.notes,
        )


def _prepare_socket_parent(socket_path: str) -> None:
    parent = os.path.dirname(socket_path) or "."
    os.makedirs(parent, exist_ok=True)
    # Service-mode UDS compatibility: when the container is started with sudo, the
    # bind-mounted directory and socket can otherwise end up owned by root. Make the
    # directory traversable and writable so a non-root host Python client can reach
    # the socket file without needing a root-owned virtual environment.
    os.chmod(parent, 0o777)


def _relax_socket_permissions(socket_path: str) -> None:
    # gRPC creates the Unix domain socket on server.start(). After that, widen the
    # socket mode to rw for user/group/other so host-side test clients can connect
    # even when docker itself was launched with sudo.
    if os.path.exists(socket_path):
        os.chmod(socket_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)


def serve(socket_path: str) -> None:
    _prepare_socket_parent(socket_path)
    if os.path.exists(socket_path):
        os.remove(socket_path)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    guide_pb2_grpc.add_BeefGuideServiceServicer_to_server(BeefGuideService(), server)
    server.add_insecure_port(f"unix://{socket_path}")
    server.start()
    _relax_socket_permissions(socket_path)
    print(f"BeefMPC_Guide service listening on unix://{socket_path}")
    server.wait_for_termination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the BeefMPC_Guide gRPC UDS service.")
    parser.add_argument("--socket-path", default="/tmp/beefguide/guide-interface.sock")
    args = parser.parse_args()
    serve(args.socket_path)
