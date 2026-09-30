"""
Reports & Evidence Route Handler.
GET /api/reports - Metadata of all 6 compliance artifacts.
GET /api/reports/download/{fmt} - Download specific artifact file.
GET /api/reports/preview/{fmt} - Preview report content.
"""
import os
import json
import tempfile
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse, HTMLResponse, PlainTextResponse

from backend.api.state import state
from app.reports.reporter import (
    export_html_report,
    export_pdf_report,
    export_sarif,
    export_inventory_csv,
    export_summary_md
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
def get_reports_metadata():
    assets = state.assets
    cbom = state.get_cbom()
    val = state.get_validation()

    return {
        "scan_id": state.scan_id,
        "target_path": state.scan_path,
        "total_deliverables": 6,
        "available_formats": [
            {"id": "json", "name": "CycloneDX 1.6 CBOM (JSON)", "filename": "cbom.json", "mime": "application/json", "available": True},
            {"id": "csv", "name": "Inventory Spreadsheet (CSV)", "filename": "inventory.csv", "mime": "text/csv", "available": True},
            {"id": "sarif", "name": "SARIF 2.1.0 Static Analysis (JSON)", "filename": "findings.sarif", "mime": "application/json", "available": True},
            {"id": "html", "name": "Executive Audit Report (HTML)", "filename": "report.html", "mime": "text/html", "available": True},
            {"id": "pdf", "name": "Executive Security Brief (PDF)", "filename": "report.pdf", "mime": "application/pdf", "available": True},
            {"id": "md", "name": "Technical Summary (Markdown)", "filename": "summary.md", "mime": "text/markdown", "available": True},
        ],
        "validation_status": "PASS (0 Errors)" if val.get("valid") else "FAIL",
        "total_assets": len(assets)
    }


@router.get("/download/{fmt}")
def download_report(fmt: str):
    assets = state.assets
    metrics = state.metrics
    val = state.get_validation()

    fmt = fmt.lower()
    with tempfile.TemporaryDirectory() as tmp_dir:
        if fmt == "json":
            cbom = state.get_cbom()
            return JSONResponse(
                content=cbom,
                headers={"Content-Disposition": 'attachment; filename="cbom.json"'}
            )
        elif fmt == "csv":
            df = pd.DataFrame([{
                "algorithm": a.algorithm,
                "key_size": a.key_size or "N/A",
                "mode": a.mode or "N/A",
                "type": a.asset_type.value,
                "usage": a.usage.value,
                "quantum": a.quantum_status.value,
                "threat": "HNDL" if a.hndl_risk else ("TNFL" if a.tnfl_risk else "None"),
                "risk_score": a.risk_score,
                "risk_band": a.risk_band,
                "confidence": a.confidence,
                "file": os.path.basename(a.file_path),
                "line": a.line_number,
                "rule_id": a.rule_id or "N/A",
                "recommendation": a.recommendation or "",
            } for a in assets])
            csv_str = df.to_csv(index=False)
            return Response(
                content=csv_str,
                media_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="inventory.csv"'}
            )
        elif fmt == "sarif":
            sarif_p = os.path.join(tmp_dir, "findings.sarif")
            export_sarif(assets, metrics, sarif_p)
            with open(sarif_p, "r", encoding="utf-8") as f:
                sarif_data = json.load(f)
            return JSONResponse(
                content=sarif_data,
                headers={"Content-Disposition": 'attachment; filename="findings.sarif"'}
            )
        elif fmt == "html":
            html_p = os.path.join(tmp_dir, "report.html")
            export_html_report(assets, metrics, val, html_p)
            with open(html_p, "r", encoding="utf-8") as f:
                html_content = f.read()
            return Response(
                content=html_content,
                media_type="text/html",
                headers={"Content-Disposition": 'attachment; filename="report.html"'}
            )
        elif fmt == "pdf":
            pdf_p = os.path.join(tmp_dir, "report.pdf")
            res_pdf = export_pdf_report(assets, metrics, val, pdf_p)
            if res_pdf and os.path.exists(res_pdf):
                with open(res_pdf, "rb") as f:
                    pdf_bytes = f.read()
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="report.pdf"'}
                )
            else:
                raise HTTPException(status_code=500, detail="PDF generation unavailable")
        elif fmt == "md":
            md_p = os.path.join(tmp_dir, "summary.md")
            export_summary_md(assets, metrics, val, md_p)
            with open(md_p, "r", encoding="utf-8") as f:
                md_content = f.read()
            return Response(
                content=md_content,
                media_type="text/markdown",
                headers={"Content-Disposition": 'attachment; filename="summary.md"'}
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown format: {fmt}")


@router.get("/preview/{fmt}")
def preview_report(fmt: str):
    assets = state.assets
    metrics = state.metrics
    val = state.get_validation()

    fmt = fmt.lower()
    with tempfile.TemporaryDirectory() as tmp_dir:
        if fmt == "html":
            html_p = os.path.join(tmp_dir, "report.html")
            export_html_report(assets, metrics, val, html_p)
            with open(html_p, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        elif fmt == "md":
            md_p = os.path.join(tmp_dir, "summary.md")
            export_summary_md(assets, metrics, val, md_p)
            with open(md_p, "r", encoding="utf-8") as f:
                return PlainTextResponse(content=f.read())
        elif fmt == "sarif":
            sarif_p = os.path.join(tmp_dir, "findings.sarif")
            export_sarif(assets, metrics, sarif_p)
            with open(sarif_p, "r", encoding="utf-8") as f:
                return JSONResponse(content=json.load(f))
        else:
            raise HTTPException(status_code=400, detail=f"Preview not supported for: {fmt}")
