from pydantic import ConfigDict, BaseModel

class LocationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    company_id: int