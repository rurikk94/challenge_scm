from pydantic import ConfigDict, BaseModel

from sqlalchemy.orm import Session
from src.db.models import ReportFile as ReportFileSchema

class ReportFileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    format: str
    binary: bytes
    size: int

class ReportFile():

    @classmethod
    async def get_by_id_format(cls, db: Session, report_id: int, format: str) -> ReportFileSchema:
        return db.query(ReportFileSchema).filter_by(report_id = report_id, format = format).first()

    @classmethod
    async def create_file(cls, db: Session, report_id: int, format:str , binary: bytes, size: int =None):
        if size is None:
            size = len(binary)
        file = ReportFileSchema(
            report_id=report_id,
            format=format,
            binary=binary,
            size=size
        )
        db.add(file)
        db.commit()
        return file

report_file = ReportFile()