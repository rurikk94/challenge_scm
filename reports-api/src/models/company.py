from pydantic import ConfigDict, BaseModel

class CompanyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str