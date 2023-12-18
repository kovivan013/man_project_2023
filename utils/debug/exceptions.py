from starlette import status
from fastapi import HTTPException

ItemExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Item already exists"
)

ItemNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not fount"
)