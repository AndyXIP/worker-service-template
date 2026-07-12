from fastapi import APIRouter

router = APIRouter(prefix="/utils", tags=["utils"])


# No readiness endpoint: with no external dependency (DB, cache, etc.) to
# check, a /ready probe would just be boilerplate. Add one once this service
# actually depends on something that can be unready.
@router.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "healthy"}
