from fastapi import APIRouter

router = APIRouter()


@router.get("/users/test",
            summary='TEST',
            description='Get message ok',
            response_description='OK',
            tags=["get_test"])
async def get_test_response():
    return {"message": "ok"}


@router.get("/users/get_sum",
            summary='PARAMETER_TEST',
            description='Get PARAMETERS SUM',
            response_description='SUM',
            tags=["get_sum"])
async def get_test_response(x: int, y: int):
    return {"message": f"{x + y}"}
