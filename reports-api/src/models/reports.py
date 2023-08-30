from enum import Enum
from pydantic import BaseModel, ConfigDict, model_validator
import datetime

from sqlalchemy.orm import Session

from src.db.models import Report as ReportSchema

class FormatEnum(str, Enum):
    csv = 'csv'
    html = 'html'
    pdf = 'pdf'

class ReportFileModel(BaseModel):
    report_id: int
    format: FormatEnum

class ReportCreationRequestModel(BaseModel):
    employee_id: int
    start_date: datetime.date
    end_date: datetime.date

    @model_validator(mode='after')
    def end_date_major_than_start(self) -> 'ReportCreationRequestModel':
        start = self.start_date
        end = self.end_date
        if start > end:
            raise ValueError('start date is major than end')
        return self

class ReportCreationResultModel(ReportCreationRequestModel):
    report_id: int
    status: str

class ReportCreationModel(ReportCreationRequestModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str

class ResponseModel(BaseModel):
    status: str

class ReportCreationResponseModel(ResponseModel):
    data: ReportCreationResultModel

class Report():

    @classmethod
    async def get_by_id(cls, db: Session, report_id: int) -> ReportSchema:
        return db.query(ReportSchema).get(report_id)

    @classmethod
    async def update(cls, db: Session, report_id:int, status: str, finish_at: datetime.date = None):
        reporte: ReportSchema  = await cls.get_by_id(db, report_id)

        reporte.status = status
        reporte.finish_at = finish_at

        db.add(reporte)
        db.commit()

        return reporte


    @classmethod
    async def create(cls, db: Session, employee_id: int, start_date: datetime.date, end_date: datetime.date, status: str):
        reporte = ReportSchema(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status
        )

        db.add(reporte)
        db.commit()

        return reporte

reports = Report()