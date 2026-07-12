from fastapi import FastAPI


def create_health_app() -> FastAPI:
    """A minimal HTTP surface for liveness probes - not part of the worker's
    request-flow chain, just what Docker `HEALTHCHECK` / k8s probes hit."""
    app = FastAPI(title="health")

    @app.get("/utils/health")
    def read_health() -> dict[str, str]:
        return {"status": "healthy"}

    return app
