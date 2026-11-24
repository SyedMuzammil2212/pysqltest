from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    address_line_1: str = Field(min_length=1)
    address_line_2: str | None = None
    city: str = Field(min_length=1)
    state: str = Field(min_length=1)
    postal_code: str = Field(min_length=1)


class AddressUpdate(BaseModel):
    address_line_1: str | None = Field(default=None, min_length=1)
    address_line_2: str | None = None
    city: str | None = Field(default=None, min_length=1)
    state: str | None = Field(default=None, min_length=1)
    postal_code: str | None = Field(default=None, min_length=1)


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address_line_1: str
    address_line_2: str | None
    city: str
    state: str
    postal_code: str