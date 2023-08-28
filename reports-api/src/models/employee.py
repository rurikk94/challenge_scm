
from pydantic import ConfigDict, BaseModel
from sqlalchemy.orm import Session

from src.db.models import Employee as EmployeeSchema

class EmployeeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    company_id: int

class Employee():

    @classmethod
    async def get_by_id(cls, db: Session, employee_id: int):
        return db.query(EmployeeSchema).get(employee_id)

employee = Employee()