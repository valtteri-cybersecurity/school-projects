from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.config import SERVE_FRONTEND
from api.schemas import CalculationRequest,CalculationResponse
from operations.math_functions import add, subtract, multiply, divide


app = FastAPI(
    title="Calculator API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/calculate", response_model=CalculationResponse)
def calculate(data: CalculationRequest):
    operations = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
    }

    operation = operations[data.operation]

    try:
        result = operation(data.a, data.b)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    return CalculationResponse(result=result)

if SERVE_FRONTEND:
    FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

    app.mount(
        "/ui",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend"
    )
