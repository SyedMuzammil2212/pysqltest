from pydantic import BaseModel


class AddressCreate(BaseModel):
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state: str
    postal_code: str

class AddressUpdate(BaseModel):

    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None


class AddressResponse(BaseModel):
    id: int
    user_id: int
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state: str
    postal_code: str

    model_config = {
        "from_attributes": True
    }