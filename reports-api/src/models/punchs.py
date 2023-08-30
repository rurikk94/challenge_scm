
from typing import List
from pydantic import BaseModel, ConfigDict, computed_field
from src.models.location import LocationModel
from src.models.employee import EmployeeModel
from src.models.company import CompanyModel
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from src.db.models import Punch as PunchSchema

class PunchModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    location_id: int
    company_id: int
    punch_time: datetime

    employee: EmployeeModel
    location: LocationModel
    company: CompanyModel

    @computed_field
    @property
    def punch_date(self) -> str:
        return self.punch_time.strftime("%Y.%m.%d")

    @computed_field
    @property
    def punch_hour(self) -> str:
        return self.punch_time.strftime("%H.%M.%S")


class Punchs():

    @classmethod
    def get_by_id(cls, db: Session,
                    punch_id: int
                ):
        return db.query(PunchSchema).get(punch_id)

    @classmethod
    def get_by_employee(cls, db: Session,
                    employee_id: int
                ):
        return db.query(PunchSchema).filter_by(employee_id = employee_id).all()

    @classmethod
    def get_by_filter(cls, db: Session,
                    punch_ids: List[int] = None,
                    employee_ids: List[int] = None,
                    location_ids: List[int] = None,
                    company_id: List[int] = None,
                    start_punch_date: date = None,
                    end_punch_date: date = None,
                ):
        query = db.query(PunchSchema)
        if punch_ids:
            query = query.filter(PunchSchema.id.in_(punch_ids))
        if employee_ids:
            query = query.filter(PunchSchema.employee_id.in_(employee_ids))
        if location_ids:
            query = query.filter(PunchSchema.location_id.in_(location_ids))
        if company_id:
            query = query.filter(PunchSchema.company_id.in_(company_id))
        if start_punch_date:
            query = query.filter(PunchSchema.punch_time > start_punch_date)
        if end_punch_date:
            query = query.filter(PunchSchema.punch_time < end_punch_date + timedelta(days=1))
        return query.all()

punchs = Punchs()