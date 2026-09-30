"""
Global State Management for ECDAT Backend.
Encapsulates active scan results, in-memory cache, telemetry logs, and Mosca settings.
Air-gapped local execution only.
"""
import os
import time
import uuid
from typing import List, Dict, Any, Optional

from app.models.crypto_asset import CryptoAsset
from app.pipeline import run_full_scan
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom

DEFAULT_CORPUS = os.path.abspath("test_corpus")


class ECDATStateManager:
    def __init__(self):
        self.scan_id: str = str(uuid.uuid4())
        self.scan_path: str = DEFAULT_CORPUS
        self.scenario_year: int = 2035
        self.x_lifetime: float = 10.0
        self.y_migration: float = 3.0
        self.assets: List[CryptoAsset] = []
        self.metrics: Dict[str, Any] = {}
        self.scan_logs: List[Dict[str, str]] = []
        self.scan_in_progress: bool = False
        self.current_stage: str = "IDLE"
        self._cbom_cache: Optional[Dict[str, Any]] = None
        self._validation_cache: Optional[Dict[str, Any]] = None

        # Auto-initialize with default controlled corpus if present
        self.initialize_default()

    def log_event(self, level: str, message: str):
        t_str = time.strftime("%H:%M:%S")
        self.scan_logs.append({
            "timestamp": t_str,
            "level": level,
            "message": message
        })

    def initialize_default(self):
        if os.path.exists(DEFAULT_CORPUS):
            try:
                self.log_event("INFO", f"Pre-loading default controlled corpus: {DEFAULT_CORPUS}")
                self.run_scan(DEFAULT_CORPUS, self.scenario_year, self.x_lifetime, self.y_migration)
            except Exception as e:
                self.log_event("WARN", f"Could not auto-load default corpus: {e}")

    def run_scan(
        self,
        directory: str,
        scenario_year: Optional[int] = None,
        x_lifetime: Optional[float] = None,
        y_migration: Optional[float] = None
    ) -> Dict[str, Any]:
        if scenario_year is not None:
            self.scenario_year = scenario_year
        if x_lifetime is not None:
            self.x_lifetime = x_lifetime
        if y_migration is not None:
            self.y_migration = y_migration

        self.scan_path = os.path.abspath(directory)
        self.scan_id = str(uuid.uuid4())
        self.scan_in_progress = True
        self.current_stage = "INITIALIZING"

        def _pipeline_log(lvl, msg):
            self.log_event(lvl, msg)
            if "source" in msg.lower():
                self.current_stage = "DISCOVERY"
            elif "dependency" in msg.lower():
                self.current_stage = "DEPENDENCIES"
            elif "certificate" in msg.lower():
                self.current_stage = "CERTIFICATES"
            elif "configuration" in msg.lower():
                self.current_stage = "CONFIGURATION"
            elif "deduplicat" in msg.lower():
                self.current_stage = "NORMALIZATION"
            elif "quantum" in msg.lower():
                self.current_stage = "QUANTUM_ANALYSIS"
            elif "complete" in msg.lower():
                self.current_stage = "COMPLETE"

        try:
            self.log_event("INFO", f"Starting cryptographic scan on: {self.scan_path}")
            assets, metrics = run_full_scan(
                self.scan_path,
                scenario_year=self.scenario_year,
                x_lifetime=self.x_lifetime,
                y_migration=self.y_migration,
                log_callback=_pipeline_log
            )
            self.assets = assets
            self.metrics = metrics
            self._cbom_cache = None
            self._validation_cache = None
            self.current_stage = "COMPLETE"
            self.scan_in_progress = False
            return {
                "scan_id": self.scan_id,
                "status": "COMPLETED",
                "total_assets": len(assets),
                "metrics": metrics
            }
        except Exception as e:
            self.scan_in_progress = False
            self.current_stage = "ERROR"
            self.log_event("ERROR", f"Scan execution failed: {str(e)}")
            raise e

    def get_cbom(self) -> Dict[str, Any]:
        if self._cbom_cache is None:
            self._cbom_cache = generate_cyclonedx_cbom(self.assets)
        return self._cbom_cache

    def get_validation(self) -> Dict[str, Any]:
        if self._validation_cache is None:
            cbom = self.get_cbom()
            self._validation_cache = validate_cbom(cbom)
        return self._validation_cache


# Global singleton instance
state = ECDATStateManager()
