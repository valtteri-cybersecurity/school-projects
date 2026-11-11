from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictFloat, StrictInt


class CalculationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    a: StrictInt | StrictFloat
    b: StrictInt | StrictFloat
    operation: Literal["add", "subtract", "multiply", "divide"]


class CalculationResponse(BaseModel):
    result: float