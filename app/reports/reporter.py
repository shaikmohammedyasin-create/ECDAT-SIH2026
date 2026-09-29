"""
Reporting Engine for ECDAT.

Generates dynamically from real scan results:
  - cbom.json        (CycloneDX 1.6 CBOM)
  - inventory.csv    (CSV export of cryptographic assets)
  - findings.sarif   (SARIF 2.1.0 static analysis interchange format)
  - report.html      (Self-contained styled executive and technical report)
  - report.pdf       (A4 executive risk report via ReportLab)
  - summary.md       (Executive markdown summary)

Never hardcodes metrics, counts, or findings.
"""
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from app.models.crypto_asset import CryptoAsset

# ReportLab imports for PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def export_inventory_csv(assets: List[CryptoAsset], filepath: str) -> str:
    """Exports inventory of cryptographic assets to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = [
        "asset_id", "rule_id", "algorithm", "primitive", "key_size", "mode",
        "usage", "confidence", "provenance", "quantum_status", "quantum_vuln_class",
        "hndl_risk", "tnfl_risk", "risk_score", "risk_band", "mosca_at_risk",
        "recommendation", "file_path", "line_number"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for a in assets:
            writer.writerow({
                "asset_id": a.asset_id,
                "rule_id": a.rule_id or "ECDAT-GEN-001",
                "algorithm": a.algorithm,
                "primitive": a.primitive,
                "key_size": a.key_size if a.key_size is not None else "",
                "mode": a.mode or "",
                "usage": a.usage.value,
                "confidence": a.confidence,
                "provenance": a.provenance,
                "quantum_status": a.quantum_status.value,
                "quantum_vuln_class": a.quantum_vuln_class.value,
                "hndl_risk": a.hndl_risk,
                "tnfl_risk": a.tnfl_risk,
                "risk_score": a.risk_score,
                "risk_band": a.risk_band,
                "mosca_at_risk": a.mosca_at_risk,
                "recommendation": a.recommendation or "",
                "file_path": a.file_path,
                "line_number": a.line_number,
            })
    return filepath


def export_sarif(assets: List[CryptoAsset], metrics: Dict, filepath: str) -> str:
    """Generates schema-compliant SARIF 2.1.0 output."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    level_map = {
        "Critical": "error",
        "High": "error",
        "Medium": "warning",
        "Low": "note",
        "Info": "note",
    }

    rules: Dict[str, dict] = {}
    results = []

    for a in assets:
        rule_id = a.rule_id or f"ECDAT-{a.algorithm}-001"
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": f"Cryptographic finding: {a.algorithm}",
                "shortDescription": {"text": f"Cryptographic primitive {a.algorithm} ({a.quantum_vuln_class.value})"},
                "fullDescription": {"text": a.why_risky or f"Detected {a.algorithm} usage with quantum status {a.quantum_status.value}"},
                "helpUri": "https://cyclonedx.org/capabilities/cbom/",
                "properties": {
                    "quantum_class": a.quantum_vuln_class.value,
                    "hndl_applicable": a.hndl_risk,
                    "tnfl_applicable": a.tnfl_risk,
                }
            }

        rel_loc = a.file_path.replace("\\", "/")
        res_obj = {
            "ruleId": rule_id,
            "level": level_map.get(a.risk_band, "warning"),
            "message": {"text": f"{a.algorithm} ({a.quantum_status.value}) - Risk Score: {a.risk_score:.1f}. Recommendation: {a.recommendation or 'N/A'}"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": rel_loc},
                    "region": {
                        "startLine": max(1, a.line_number),
                        "snippet": {"text": a.source_snippet[:200]}
                    }
                }
            }],
            "properties": {
                "risk_score": a.risk_score,
                "risk_band": a.risk_band,
                "quantum_status": a.quantum_status.value,
                "mosca_at_risk": a.mosca_at_risk,
                "provenance": a.provenance,
            }
        }
        results.append(res_obj)

    sarif_doc = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "ECDAT",
                    "version": "1.0.0",
                    "informationUri": "https://sih.gov.in/sih2026PS",
                    "rules": list(rules.values()),
                }
            },
            "results": results,
            "properties": {
                "scan_metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }]
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sarif_doc, f, indent=2)
    return filepath


def export_html_report(assets: List[CryptoAsset], metrics: Dict, validation_result: Dict, filepath: str) -> str:
    """Generates a self-contained, cybersecurity-themed HTML report."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Group counts
    total = len(assets)
    shor = sum(1 for a in assets if a.quantum_vuln_class.value == "SHOR_BROKEN")
    grover = sum(1 for a in assets if a.quantum_vuln_class.value == "GROVER_WEAKENED")
    legacy = sum(1 for a in assets if a.quantum_vuln_class.value == "CLASSICALLY_BROKEN")
    safe = sum(1 for a in assets if a.quantum_vuln_class.value == "QUANTUM_SAFE")
    mosca = sum(1 for a in assets if a.mosca_at_risk)
    hndl = sum(1 for a in assets if a.hndl_risk)
    tnfl = sum(1 for a in assets if a.tnfl_risk)

    cbom_valid = validation_result.get("valid", False)
    cbom_badge = '<span class="badge badge-success">VALID (0 Errors)</span>' if cbom_valid else '<span class="badge badge-danger">FAILED</span>'

    # Build rows
    rows_html = []
    for a in sorted(assets, key=lambda x: -x.risk_score):
        band_class = {
            "Critical": "badge-danger",
            "High": "badge-warning",
            "Medium": "badge-info",
            "Low": "badge-secondary",
        }.get(a.risk_band, "badge-secondary")

        q_class = {
            "SHOR_BROKEN": "badge-danger",
            "GROVER_WEAKENED": "badge-warning",
            "CLASSICALLY_BROKEN": "badge-danger",
            "QUANTUM_SAFE": "badge-success",
        }.get(a.quantum_vuln_class.value, "badge-secondary")

        threat_tag = ""
        if a.hndl_risk:
            threat_tag += '<span class="tag tag-hndl">HNDL</span> '
        if a.tnfl_risk:
            threat_tag += '<span class="tag tag-tnfl">TNFL</span> '

        rows_html.append(f"""
        <tr>
            <td><code>{a.rule_id or 'ECDAT-GEN'}</code></td>
            <td><strong>{a.algorithm}</strong> {f'({a.key_size}-bit)' if a.key_size else ''}</td>
            <td><span class="badge {q_class}">{a.quantum_vuln_class.value}</span></td>
            <td>{threat_tag or '<span class="text-muted">None</span>'}</td>
            <td><span class="badge {band_class}">{a.risk_band} ({a.risk_score:.1f})</span></td>
            <td><code>{os.path.basename(a.file_path)}:{a.line_number}</code></td>
            <td>{a.recommendation or 'N/A'}</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECDAT Cryptographic Security & Post-Quantum Risk Report</title>
    <style>
        :root {{
            --bg-main: #0B1120;
            --bg-card: #1E293B;
            --bg-card-alt: #0F172A;
            --text-main: #F1F5F9;
            --text-muted: #94A3B8;
            --border: #334155;
            --accent: #38BDF8;
            --danger: #EF4444;
            --warning: #F59E0B;
            --success: #10B981;
            --info: #0284C7;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            margin: 0;
            padding: 30px;
            line-height: 1.5;
        }}
        .header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            color: var(--accent);
            font-size: 26px;
            letter-spacing: -0.5px;
        }}
        .meta-bar {{
            font-size: 13px;
            color: var(--text-muted);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }}
        .card-num {{
            font-size: 28px;
            font-weight: 700;
            margin-top: 5px;
            color: var(--text-main);
        }}
        .card-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }}
        .badge-success {{ background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }}
        .badge-info {{ background: rgba(2, 132, 199, 0.2); color: #38BDF8; border: 1px solid #0284C7; }}
        .badge-secondary {{ background: rgba(148, 163, 184, 0.2); color: #CBD5E1; border: 1px solid #64748B; }}
        .tag {{
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 700;
        }}
        .tag-hndl {{ background: #7F1D1D; color: #FECACA; }}
        .tag-tnfl {{ background: #78350F; color: #FDE68A; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            font-size: 13px;
        }}
        th, td {{
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: var(--bg-card-alt);
            color: var(--text-muted);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}
        code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 5px;
            border-radius: 4px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
            color: #E2E8F0;
        }}
        .section-title {{
            font-size: 18px;
            margin: 25px 0 15px 0;
            color: var(--text-main);
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ECDAT Cryptographic Risk & Post-Quantum Analysis Report</h1>
        <div class="meta-bar">
            Generated: <strong>{ts}</strong> | Tool: <strong>ECDAT v1.0 (SIH 2026 PS ID: 26164)</strong> | CycloneDX 1.6 CBOM: {cbom_badge}
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-label">Total Crypto Assets</div>
            <div class="card-num">{total}</div>
        </div>
        <div class="card">
            <div class="card-label">Shor-Broken (CRQC Vulnerable)</div>
            <div class="card-num" style="color: var(--danger);">{shor}</div>
        </div>
        <div class="card">
            <div class="card-label">Grover-Weakened</div>
            <div class="card-num" style="color: var(--warning);">{grover}</div>
        </div>
        <div class="card">
            <div class="card-label">Classically Broken</div>
            <div class="card-num" style="color: var(--danger);">{legacy}</div>
        </div>
        <div class="card">
            <div class="card-label">Harvest-Now-Decrypt-Later (HNDL)</div>
            <div class="card-num" style="color: #F87171;">{hndl}</div>
        </div>
        <div class="card">
            <div class="card-label">Mosca Violations (X + Y &gt; Z)</div>
            <div class="card-num" style="color: var(--danger);">{mosca}</div>
        </div>
    </div>

    <div class="section-title">Cryptographic Asset Inventory & Migration Guidance</div>
    <table>
        <thead>
            <tr>
                <th>Rule ID</th>
                <th>Algorithm</th>
                <th>Quantum Vulnerability</th>
                <th>Threat Surface</th>
                <th>Risk Band</th>
                <th>Source Location</th>
                <th>PQC Recommendation (NIST FIPS)</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows_html)}
        </tbody>
    </table>

    <div class="section-title" style="margin-top: 40px;">Methodology & Verification Controls</div>
    <div class="card" style="font-size: 13px; color: var(--text-muted);">
        <p><strong>Risk Engine Formulation:</strong> Explaining risk via NTRO formula: <code>100 × (0.35×QuantumExposure + 0.25×BusinessCriticality + 0.15×ExposureSurface + 0.15×DataSensitivity + 0.10×(1 - CryptoAgility))</code>.</p>
        <p><strong>Mosca Condition:</strong> Evaluates <code>X (Data Lifetime) + Y (Migration Time) &gt; Z (CRQC Horizon)</code> where Z is an explicitly parameterized scenario horizon (default: 2035).</p>
        <p><strong>CBOM Specification:</strong> CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) with strict schema validation against official specifications.</p>
    </div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filepath


def export_pdf_report(assets: List[CryptoAsset], metrics: Dict, validation_result: Dict, filepath: str) -> Optional[str]:
    """Generates an executive PDF report via ReportLab."""
    if not REPORTLAB_AVAILABLE:
        return None

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10)
    cell = ParagraphStyle("cell", parent=body, fontSize=7.5, leading=9)

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="ECDAT Cryptographic Security Report",
        author="ECDAT Core Team",
    )

    def _p(text: str, style=cell) -> Paragraph:
        clean = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return Paragraph(clean, style)

    story = [
        _p("ECDAT — Cryptographic Discovery & Post-Quantum Analysis Report", title_style),
        _p(f"Scan Completed: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | CycloneDX 1.6 CBOM: {'VALID (0 Errors)' if validation_result.get('valid') else 'INVALID'}", small),
        Spacer(1, 4 * mm),
        _p("Executive Summary & Risk Metrics", h2),
    ]

    # Metrics table
    total = len(assets)
    shor = sum(1 for a in assets if a.quantum_vuln_class.value == "SHOR_BROKEN")
    grover = sum(1 for a in assets if a.quantum_vuln_class.value == "GROVER_WEAKENED")
    legacy = sum(1 for a in assets if a.quantum_vuln_class.value == "CLASSICALLY_BROKEN")
    mosca = sum(1 for a in assets if a.mosca_at_risk)
    hndl = sum(1 for a in assets if a.hndl_risk)

    metric_rows = [
        ["Total Assets", "Shor-Broken", "Grover-Weakened", "Legacy Broken", "HNDL Risk", "Mosca Violations"],
        [str(total), str(shor), str(grover), str(legacy), str(hndl), str(mosca)],
    ]
    mt = Table([[_p(c, cell) for c in r] for r in metric_rows], colWidths=[30 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm])
    mt.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story += [mt, Spacer(1, 5 * mm)]

    story += [_p("Top Prioritized Findings & Post-Quantum Recommendations", h2)]
    finding_rows = [["Rule ID", "Algorithm", "Quantum Class", "Risk Band", "Location", "PQC Target"]]
    for a in sorted(assets, key=lambda x: -x.risk_score)[:30]:
        finding_rows.append([
            a.rule_id or "ECDAT-GEN",
            f"{a.algorithm} ({a.key_size or ''})".strip(),
            a.quantum_vuln_class.value,
            f"{a.risk_band} ({a.risk_score:.1f})",
            f"{os.path.basename(a.file_path)}:{a.line_number}",
            (a.recommendation or "N/A")[:35]
        ])

    ft = Table([[_p(c, cell) for c in r] for r in finding_rows], colWidths=[28 * mm, 28 * mm, 32 * mm, 24 * mm, 34 * mm, 36 * mm], repeatRows=1)
    ft.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#94A3B8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(ft)

    doc.build(story)
    return filepath


def export_summary_md(assets: List[CryptoAsset], metrics: Dict, validation_result: Dict, filepath: str) -> str:
    """Generates an executive markdown summary."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    md = f"""# ECDAT Executive Scan Summary
**Timestamp:** {ts}  
**CycloneDX 1.6 CBOM Status:** {"VALID (0 Errors)" if validation_result.get("valid") else "FAILED"}  

## Key Scan Metrics
- **Total Cryptographic Assets:** {len(assets)}
- **Shor-Broken (Asymmetric):** {metrics.get("quantum_vulnerable", 0)}
- **Grover-Weakened (Symmetric):** {metrics.get("grover_weakened", 0)}
- **Classically Broken (Legacy):** {metrics.get("classically_broken", 0)}
- **Mosca Violations (X + Y > Z):** {metrics.get("mosca_violations", 0)}
- **Critical Risk Assets:** {metrics.get("critical_risk", 0)}
- **High Risk Assets:** {metrics.get("high_risk", 0)}

## Top Findings
| Rule ID | Algorithm | Quantum Class | Risk Band | Location | Recommendation |
|---|---|---|---|---|---|
"""
    for a in sorted(assets, key=lambda x: -x.risk_score)[:15]:
        md += f"| `{a.rule_id}` | {a.algorithm} | {a.quantum_vuln_class.value} | {a.risk_band} ({a.risk_score:.1f}) | `{os.path.basename(a.file_path)}:{a.line_number}` | {a.recommendation} |\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)
    return filepath


def generate_all_reports(
    assets: List[CryptoAsset],
    metrics: Dict,
    validation_result: Dict,
    output_dir: str
) -> Dict[str, str]:
    """Generates all 5 standard report artifacts dynamically."""
    os.makedirs(output_dir, exist_ok=True)
    generated = {}

    csv_path = os.path.join(output_dir, "inventory.csv")
    generated["csv"] = export_inventory_csv(assets, csv_path)

    sarif_path = os.path.join(output_dir, "findings.sarif")
    generated["sarif"] = export_sarif(assets, metrics, sarif_path)

    html_path = os.path.join(output_dir, "report.html")
    generated["html"] = export_html_report(assets, metrics, validation_result, html_path)

    pdf_path = os.path.join(output_dir, "report.pdf")
    pdf_res = export_pdf_report(assets, metrics, validation_result, pdf_path)
    if pdf_res:
        generated["pdf"] = pdf_res

    md_path = os.path.join(output_dir, "summary.md")
    generated["summary"] = export_summary_md(assets, metrics, validation_result, md_path)

    return generated
