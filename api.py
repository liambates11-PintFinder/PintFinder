
from dataclasses import asdict, fields
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from models.pub import Pub
from occasions import OCCASION_TEMPLATES
from recommendation_engine import calculate_recommendations


app = FastAPI(title="PintFinder Recommendation API")


class RecommendationRequest(BaseModel):
    occasion: str
    preferences: dict[str, Any] = Field(default_factory=dict)
    maximum_distance: float = 30
    pubs: list[dict[str, Any]]


@app.get("/health")
def health():
    return {"status": "ok", "service": "pintfinder"}


@app.post("/recommend")
def recommend(request: RecommendationRequest):
    occasion = OCCASION_TEMPLATES.get(request.occasion)

    if occasion is None:
        raise HTTPException(
            status_code=400,
            detail="Unknown occasion. Use a template ID from 1 to 6.",
        )

    allowed_fields = {field.name for field in fields(Pub)}
    pubs = []

    for index, raw_pub in enumerate(request.pubs):
        try:
            pub_data = {
                key: value
                for key, value in raw_pub.items()
                if key in allowed_fields
            }
            pubs.append(Pub(**pub_data))
        except (TypeError, ValueError) as error:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid pub at index {index}: {error}",
            )

    try:
        results = calculate_recommendations(
            pubs=pubs,
            occasion=occasion,
            preferences=request.preferences,
            maximum_distance=request.maximum_distance,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Recommendation calculation failed.",
        ) from error

    # Remove the raw Python Pub object and return serialisable data.
    serialisable_results = []

    for result in results:
        clean_result = {
            key: value
            for key, value in result.items()
            if key != "pub"
        }
        serialisable_results.append(clean_result)

    return {
        "occasion": occasion["name"],
        "count": len(serialisable_results),
        "recommendations": serialisable_results,
    }

