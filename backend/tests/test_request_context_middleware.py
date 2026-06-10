from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.middleware import RequestContextMiddleware


def make_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/request-id")
    def request_id(request: Request) -> dict[str, str]:
        return {"request_id": request.state.request_id}

    return app


def test_request_context_middleware_adds_generated_request_id_header() -> None:
    client = TestClient(make_test_app())

    response = client.get("/request-id")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_request_context_middleware_preserves_incoming_request_id() -> None:
    client = TestClient(make_test_app())

    response = client.get("/request-id", headers={"X-Request-ID": "request-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "request-123"
    assert response.json() == {"request_id": "request-123"}
