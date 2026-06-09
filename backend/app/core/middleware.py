from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.metrics import REQUEST_COUNT, REQUEST_LATENCY


logger = logging.getLogger("anomalyx.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", uuid4().hex)
        request.state.request_id = request_id
        start_time = time.perf_counter()
        status_code = 500
        response: Response | None = None

        try:
            response = await call_next(request)
            status_code = response.status_code
        finally:
            if response is not None:
                response.headers["X-Request-ID"] = request_id
            latency_ms = round((time.perf_counter() - start_time) * 1000, 3)
            route_path = request.scope.get("route").path if request.scope.get("route") else request.url.path
            REQUEST_COUNT.labels(
                method=request.method,
                path=route_path,
                status_code=str(status_code),
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                path=route_path,
            ).observe(latency_ms / 1000)
            logger.info(
                "http_request",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": route_path,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                },
            )
        return response
