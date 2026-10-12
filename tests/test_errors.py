
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

error_test_app = FastAPI()


@error_test_app.exception_handler(Exception)
async def safe_error(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@error_test_app.get("/crash")
def crash():
    raise RuntimeError("Internal database detail")


def test_unexpected_error_returns_safe_response():
    with TestClient(
        error_test_app, raise_server_exceptions=False
    ) as client:
        response = client.get("/crash")
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error"
    }
    assert "Internal database detail" not in response.text


