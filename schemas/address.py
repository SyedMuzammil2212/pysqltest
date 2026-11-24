from pydantic import BaseModel, ConfigDict


class AddressCreate(BaseModel):
    address_line: str
    city: str
    state: str
    postal_code: str


class AddressUpdate(BaseModel):
    address_line: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    address_line: str
    city: str
    state: str
    postal_code: str