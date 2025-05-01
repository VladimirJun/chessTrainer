from fastapi import APIRouter, HTTPException

from API.services.assistant_service import analyze_position

router = APIRouter()

@router.post("/analyze-position")
async def analyze_position_endpoint(fen: str):
    try:
        result = analyze_position(fen)
        return {"message": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
