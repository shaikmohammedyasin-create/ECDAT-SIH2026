"""
CycloneDX 1.6 CBOM Route Handler.
GET /api/cbom - Returns the validated CycloneDX 1.6 Cryptographic Bill of Materials document and schema report.
GET /api/cbom/download - Downloads cbom.json as an attachment.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.api.state import state
from backend.api.schemas import CBOMResponse

router = APIRouter(prefix="/api/cbom", tags=["cbom"])


@router.get("", response_model=CBOMResponse)
def get_cbom_data():
    cbom = state.get_cbom()
    val = state.get_validation()
    return CBOMResponse(
        cbom=cbom,
        validation=val,
        component_count=len(cbom.get("components", []))
    )


@router.get("/download")
def download_cbom_json():
    cbom = state.get_cbom()
    headers = {
        "Content-Disposition": 'attachment; filename="cbom.json"'
    }
    return JSONResponse(content=cbom, headers=headers)
