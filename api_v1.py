"""
This program is free software: you can redistribute it under the terms
of the GNU General Public License, v. 3.0. If a copy of the GNU General
Public License was not distributed with this file, see <https://www.gnu.org/licenses/>.
"""

from typing import Annotated
import requests
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from data_retriever import get_summary
from api_data_schemas import SummaryResponse, ErrorResponse, SummaryParams

router = APIRouter(prefix="/v1", tags=["API V1"])


def get_security_headers() -> dict:
    """
    Return a dictionary of security headers.
    """
    return {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "Content-Security-Policy": "default-src 'self';",
        "Permissions-Policy": "geolocation=(self)",
    }


@router.get(
    "/summary",
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    response_model=SummaryResponse,
)
def summary(query: Annotated[SummaryParams, Query()]) -> SummaryResponse:
    """Fetch metrics summary."""

    try:
        params = {
            "start_date": query.start_date,
            "end_date": query.end_date,
            "country_code": query.country_code,
        }

        summary_data = get_summary(params)

        response_data = {
            "summary": {
                "total_signup_users": summary_data["total_signup_users"],
                "total_retained_users": summary_data["total_retained_users"],
            }
        }

        return JSONResponse(content=response_data, headers=get_security_headers())
    except requests.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail=e.response.json()
        ) from e
