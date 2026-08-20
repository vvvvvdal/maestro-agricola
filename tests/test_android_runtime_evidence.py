from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from collect_android_runtime_evidence import (  # noqa: E402
    build_runtime_evidence,
    parse_adb_devices,
)


class FakeQuery:
    def __init__(self, internal_files: str = "./files/state.json\n", external_files: str = "") -> None:
        self.responses = {
            ("get-state",): "device\n",
            ("shell", "getprop", "ro.product.manufacturer"): "motorola\n",
            ("shell", "getprop", "ro.product.model"): "motorola edge 40 neo\n",
            ("shell", "getprop", "ro.build.version.release"): "15\n",
            ("shell", "getprop", "ro.build.version.sdk"): "35\n",
            ("shell", "getprop", "ro.product.cpu.abilist"): "arm64-v8a,armeabi-v7a\n",
            ("shell", "dumpsys", "package", "br.org.agroturtles.maestro.mock"): (
                "versionCode=1 minSdk=26 targetSdk=36\nversionName=0.1.0-mock\n"
                "private diagnostic text that must not enter evidence\n"
            ),
            ("shell", "dumpsys", "battery"): (
                "level: 87\nstatus: 3\nplugged: 0\nvoltage: 4210\ntemperature: 315\n"
            ),
            ("shell", "dumpsys", "thermalservice"): "Thermal Status: 1\n",
            ("shell", "dumpsys", "meminfo", "br.org.agroturtles.maestro.mock"): "TOTAL PSS: 13,256\n",
            (
                "shell", "run-as", "br.org.agroturtles.maestro.mock", "find", ".", "-type", "f"
            ): internal_files,
            (
                "shell", "find", "/sdcard/Android/data/br.org.agroturtles.maestro.mock", "-type", "f"
            ): external_files,
        }

    def __call__(self, command: list[str]) -> str:
        return self.responses[tuple(command)]


class AndroidRuntimeEvidenceTest(unittest.TestCase):
    def create_artifacts(self, directory: str) -> tuple[Path, Path]:
        apk = Path(directory) / "app.apk"
        model = Path(directory) / "model.json"
        apk.write_bytes(b"apk-fixture")
        model.write_text('{"model": true}', encoding="utf-8")
        return apk, model

    def test_collects_only_sanitized_technical_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            apk, model = self.create_artifacts(directory)
            evidence = build_runtime_evidence(
                FakeQuery(),
                "br.org.agroturtles.maestro.mock",
                "before",
                apk,
                model,
                recorded_at="2026-08-19T18:00:00-03:00",
            )

        self.assertEqual("COMPLETE", evidence["collection_status"])
        self.assertEqual(87, evidence["battery"]["level_percent"])
        self.assertEqual(31.5, evidence["battery"]["temperature_c"])
        self.assertEqual("LIGHT", evidence["thermal"]["status"]["name"])
        self.assertEqual(13256, evidence["memory"]["total_pss_kb"])
        self.assertFalse(evidence["privacy"]["stores_device_serial"])
        serialized = json.dumps(evidence)
        self.assertNotIn("private diagnostic text", serialized)
        self.assertNotIn("serial", serialized.lower().replace("stores_device_serial", ""))

    def test_flags_media_filename_without_reading_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            apk, model = self.create_artifacts(directory)
            evidence = build_runtime_evidence(
                FakeQuery(internal_files="./files/captured_frame.jpg\n"),
                "br.org.agroturtles.maestro.mock",
                "after",
                apk,
                model,
            )

        self.assertEqual("REVIEW_REQUIRED", evidence["collection_status"])
        audit = evidence["storage_audit"]["internal"]
        self.assertEqual(1, audit["suspicious_file_count"])
        self.assertEqual(["./files/captured_frame.jpg"], audit["suspicious_paths"])

    def test_rejects_unsafe_package_and_phase(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            apk, model = self.create_artifacts(directory)
            with self.assertRaisesRegex(ValueError, "package"):
                build_runtime_evidence(FakeQuery(), "pkg;rm", "before", apk, model)
            with self.assertRaisesRegex(ValueError, "phase"):
                build_runtime_evidence(FakeQuery(), "valid.package", "before now", apk, model)

    def test_parses_ready_and_blocked_devices(self) -> None:
        devices = parse_adb_devices(
            "List of devices attached\nABC123\tdevice\nOLD456\tunauthorized\n\n"
        )
        self.assertEqual({"ABC123": "device", "OLD456": "unauthorized"}, devices)

    def test_privacy_audit_separates_four_processors(self) -> None:
        audit = json.loads(
            (ROOT / "shared" / "evidence" / "privacy_audit.json").read_text(encoding="utf-8")
        )
        self.assertEqual("PARTIAL", audit["status"])
        self.assertEqual(
            {"MAESTRO", "ANDROID", "DAT_META", "BRIDGE_EXTERNAL"},
            {processor["id"] for processor in audit["data_processors"]},
        )
        self.assertFalse(audit["runtime_collection"]["captures_logcat"])
        self.assertFalse(audit["runtime_collection"]["reads_file_contents"])

    def test_recorded_before_snapshot_is_sanitized(self) -> None:
        snapshot = json.loads(
            (ROOT / "shared" / "evidence" / "android_runtime_before.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("before", snapshot["phase"])
        self.assertEqual("PARTIAL", snapshot["collection_status"])
        self.assertEqual("motorola edge 40 neo", snapshot["device"]["model"])
        self.assertEqual(0, snapshot["storage_audit"]["internal"]["suspicious_file_count"])
        self.assertTrue(all(value is False for value in snapshot["privacy"].values()))
        self.assertNotIn("serial", snapshot["device"])
        self.assertNotIn("adb_serial", snapshot)

    def test_qa03_pair_and_comparison_are_traceable_and_sanitized(self) -> None:
        evidence_dir = ROOT / "shared" / "evidence"
        before = json.loads(
            (evidence_dir / "android_runtime_qa03_before.json").read_text(encoding="utf-8")
        )
        after = json.loads(
            (evidence_dir / "android_runtime_qa03_after.json").read_text(encoding="utf-8")
        )
        comparison = json.loads(
            (evidence_dir / "android_runtime_qa03_comparison.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual("qa03_before", before["phase"])
        self.assertEqual("qa03_after", after["phase"])
        self.assertEqual(before["build"], after["build"])
        self.assertEqual(before["build"]["apk_sha256"], comparison["traceability"]["apk_sha256"])
        self.assertEqual(5, comparison["protocol"]["cycles"])
        self.assertEqual(0, comparison["protocol"]["confirmed_commands"])
        self.assertFalse(comparison["protocol"]["uses_microphone"])
        self.assertEqual(596, comparison["protocol"]["snapshot_interval_seconds"])
        self.assertEqual(0, comparison["comparison"]["suspicious_internal_file_count"]["after"])
        self.assertEqual("CHARGING", comparison["comparison"]["battery_status"]["after_name"])
        self.assertEqual("PARTIAL", comparison["status"])
        self.assertTrue(all(value is False for value in comparison["privacy"].values()))
        self.assertTrue(comparison["human_observation"]["tts_audible"])
        self.assertEqual(
            "alto-falante inferior do telefone",
            comparison["human_observation"]["output_route"],
        )
        self.assertFalse(comparison["human_observation"]["audio_recording_created"])

        serialized = json.dumps({"before": before, "after": after, "comparison": comparison})
        self.assertNotIn("adb_serial", serialized)
        self.assertNotIn("captured_frame", serialized)

    def test_privacy_audit_points_to_qa03_pair(self) -> None:
        audit = json.loads(
            (ROOT / "shared" / "evidence" / "privacy_audit.json").read_text(
                encoding="utf-8"
            )
        )
        runtime = audit["runtime_collection"]
        self.assertEqual(
            "shared/evidence/android_runtime_qa03_before.json", runtime["before_snapshot"]
        )
        self.assertEqual(
            "shared/evidence/android_runtime_qa03_after.json", runtime["after_snapshot"]
        )
        self.assertEqual(
            "shared/evidence/android_runtime_qa03_comparison.json", runtime["comparison"]
        )


if __name__ == "__main__":
    unittest.main()
