#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build aggregated RRDCS gate report from job results.",
    )
    parser.add_argument(
        "--enforcement-mode",
        default="required",
        choices=("audit", "required"),
        help="Effective enforcement mode for gate decision.",
    )
    parser.add_argument("--linux-status", required=True, help="Result of linux check-all job")
    parser.add_argument("--windows-status", required=True, help="Result of windows check-all job")
    parser.add_argument("--linux-artifact", default="rrdcs-check-all-linux-evidence", help="Linux evidence artifact name")
    parser.add_argument("--windows-artifact", default="rrdcs-check-all-windows-evidence", help="Windows evidence artifact name")
    parser.add_argument("--output-json", required=True, help="Path to output JSON report")
    parser.add_argument("--output-md", required=True, help="Path to output markdown report")
    return parser.parse_args()


def normalize_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def quality_status(linux_status: str, windows_status: str) -> str:
    if linux_status == "success" and windows_status == "success":
        return "pass"
    return "fail"


def gate_status(enforcement_mode: str, quality_status_value: str) -> str:
    if enforcement_mode == "audit":
        return "pass"
    return quality_status_value


def error_code_for_status(status: str) -> str:
    if status == "success":
        return ""
    if status == "cancelled":
        return "RRDCS-CI-JOB-CANCELLED"
    if status == "skipped":
        return "RRDCS-CI-JOB-SKIPPED"
    return "RRDCS-CI-JOB-FAILED"


def build_payload(args: argparse.Namespace) -> dict:
    quality_state = quality_status(args.linux_status, args.windows_status)
    overall = gate_status(args.enforcement_mode, quality_state)
    checks = [
        {
            "job": "rrdcs-check-all-linux",
            "status": args.linux_status,
            "artifact": args.linux_artifact,
            "error_code": error_code_for_status(args.linux_status),
            "source_step": "Run local pre-check plan",
            "log_ref": "check-all-linux.log",
        },
        {
            "job": "rrdcs-check-all-windows",
            "status": args.windows_status,
            "artifact": args.windows_artifact,
            "error_code": error_code_for_status(args.windows_status),
            "source_step": "Run local pre-check plan",
            "log_ref": "check-all-windows.log",
        },
    ]

    payload = {
        "report_version": "1.0",
        "enforcement_mode": args.enforcement_mode,
        "quality_status": quality_state,
        "overall_status": overall,
        "blocking": overall == "fail",
        "checks": checks,
        "failed_jobs": [item["job"] for item in checks if item["status"] != "success"],
    }
    return payload


def build_markdown(payload: dict) -> str:
    lines: list[str] = []
    lines.append("## RRDCS Gate Decision Report")
    lines.append("")
    lines.append(f"- enforcement mode: `{payload['enforcement_mode']}`")
    lines.append(f"- quality status: `{payload['quality_status']}`")
    lines.append(f"- overall status: `{payload['overall_status']}`")
    lines.append("")
    lines.append("| job | status | error_code | source_step | log_ref | artifact |")
    lines.append("|---|---|---|---|---|---|")
    for item in payload["checks"]:
        error_code = item["error_code"] if item["error_code"] else "-"
        lines.append(
            f"| `{item['job']}` | `{item['status']}` | `{error_code}` | `{item['source_step']}` | `{item['log_ref']}` | `{item['artifact']}` |"
        )
    return "\n".join(lines) + "\n"


def write_text(path_value: str, content: str) -> None:
    target = normalize_path(path_value)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    write_text(args.output_json, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    write_text(args.output_md, build_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
