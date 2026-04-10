#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


DOCS_ONLY_PREFIXES = (
    "docs/",
    ".sources/",
    ".manifest/",
    ".tasks/",
    ".issues/",
)
DOCS_ONLY_FILES = {"README.md"}


@dataclass(frozen=True)
class DiffEntry:
    path: str
    added: int
    deleted: int
    binary: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Сформировать отчет по размеру PR (PR size policy).",
    )
    parser.add_argument("--base", default="", help="Базовый ref для diff.")
    parser.add_argument("--head", default="", help="Head ref для diff.")
    parser.add_argument(
        "--threshold-lines",
        type=int,
        default=100,
        help="Порог churn в строках для code PR.",
    )
    parser.add_argument(
        "--mode",
        choices=("warning-only", "blocking"),
        default="warning-only",
        help="Режим политики. На MVP используется warning-only.",
    )
    parser.add_argument("--output-json", required=True, help="Путь к JSON отчету.")
    parser.add_argument("--output-md", required=True, help="Путь к Markdown отчету.")
    return parser.parse_args()


def normalize_ref(raw_value: str, fallback: str) -> str:
    value = raw_value.strip()
    return value if value else fallback


def run_git_diff(repo_root: Path, base_ref: str, head_ref: str) -> list[DiffEntry]:
    command = [
        "git",
        "diff",
        "--numstat",
        f"{base_ref}...{head_ref}",
        "--",
    ]
    proc = subprocess.run(
        command,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()
        details = stderr if stderr else stdout
        message = details.splitlines()[0] if details else "git diff завершился с ошибкой"
        raise RuntimeError(message)

    entries: list[DiffEntry] = []
    for raw_line in proc.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added_raw, deleted_raw = parts[0], parts[1]
        path = "\t".join(parts[2:])
        binary = added_raw == "-" or deleted_raw == "-"
        added = 0 if added_raw == "-" else int(added_raw)
        deleted = 0 if deleted_raw == "-" else int(deleted_raw)
        entries.append(DiffEntry(path=path, added=added, deleted=deleted, binary=binary))
    return entries


def is_docs_only(path_value: str) -> bool:
    if path_value in DOCS_ONLY_FILES:
        return True
    return any(path_value.startswith(prefix) for prefix in DOCS_ONLY_PREFIXES)


def build_payload(
    entries: list[DiffEntry],
    base_ref: str,
    head_ref: str,
    threshold_lines: int,
    mode: str,
) -> dict:
    total_added = sum(item.added for item in entries)
    total_deleted = sum(item.deleted for item in entries)
    churn = total_added + total_deleted
    docs_only = bool(entries) and all(is_docs_only(item.path) for item in entries)
    status = "docs-only" if docs_only else ("warn" if churn > threshold_lines else "pass")

    payload = {
        "report_version": "1.0",
        "mode": mode,
        "base_ref": base_ref,
        "head_ref": head_ref,
        "threshold_lines": threshold_lines,
        "status": status,
        "docs_only": docs_only,
        "file_count": len(entries),
        "added_lines": total_added,
        "deleted_lines": total_deleted,
        "churn_lines": churn,
        "files": [
            {
                "path": item.path,
                "added": item.added,
                "deleted": item.deleted,
                "binary": item.binary,
            }
            for item in entries
        ],
        "notes": [],
    }

    if docs_only:
        payload["notes"].append("docs-only PR detected; size threshold is reported separately.")
    elif churn > threshold_lines:
        payload["notes"].append("PR size exceeds the warning threshold.")
    else:
        payload["notes"].append("PR size is within the warning threshold.")

    return payload


def write_text(path_value: str, content: str) -> None:
    target = Path(path_value).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_markdown(payload: dict) -> str:
    lines: list[str] = []
    lines.append("## RRDCS PR Size Report")
    lines.append("")
    lines.append(f"- mode: `{payload['mode']}`")
    lines.append(f"- status: `{payload['status']}`")
    lines.append(f"- base: `{payload['base_ref']}`")
    lines.append(f"- head: `{payload['head_ref']}`")
    lines.append(f"- threshold lines: `{payload['threshold_lines']}`")
    lines.append(f"- file count: `{payload['file_count']}`")
    lines.append(f"- churn lines: `{payload['churn_lines']}`")
    lines.append(f"- docs-only: `{str(payload['docs_only']).lower()}`")
    lines.append("")
    lines.append("| path | + | - | binary |")
    lines.append("|---|---:|---:|---|")
    for item in payload["files"]:
        binary = "yes" if item["binary"] else "no"
        lines.append(f"| `{item['path']}` | {item['added']} | {item['deleted']} | {binary} |")
    if payload["notes"]:
        lines.append("")
        lines.append("### Notes")
        for note in payload["notes"]:
            lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    base_ref = normalize_ref(args.base, "HEAD~1")
    head_ref = normalize_ref(args.head, "HEAD")

    try:
        entries = run_git_diff(repo_root=repo_root, base_ref=base_ref, head_ref=head_ref)
        payload = build_payload(
            entries=entries,
            base_ref=base_ref,
            head_ref=head_ref,
            threshold_lines=args.threshold_lines,
            mode=args.mode,
        )
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"[FAIL] ошибка расчета PR size: {exc}")
        return 1

    write_text(args.output_json, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    write_text(args.output_md, build_markdown(payload))

    print(f"[PASS] PR size report generated: {payload['status']}")
    print(f"  base: {payload['base_ref']}")
    print(f"  head: {payload['head_ref']}")
    print(f"  threshold_lines: {payload['threshold_lines']}")
    print(f"  churn_lines: {payload['churn_lines']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
