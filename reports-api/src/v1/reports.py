import asyncio
import csv
import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from io import BytesIO
import jinja2
import pdfkit
from pydantic import ValidationError
from pathlib import Path
from sqlalchemy.orm import Session

from src.db.models import Report as ReportSchema
from src.db.models import Employee as EmployeeSchema
from src.config import settings
from src.models import reports, employee, punchs, report_file
from src.models.punchs import PunchModel
from src.models.reports import ReportCreationRequestModel, ReportCreationResponseModel, ReportFileModel, ReportCreationModel
from src.v1 import deps

reports_routes = APIRouter()

@reports_routes.post("/", status_code=201, response_model=ReportCreationResponseModel)
async def create_report(
    report_in: ReportCreationRequestModel,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)):
    """ Endpoint para crear un reporte """

    e = await employee.get_by_id(db, report_in.employee_id)

    if e is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Employee not found")

    report: ReportSchema = await reports.create(
        db,
        employee_id=report_in.employee_id,
        start_date=report_in.start_date,
        end_date=report_in.end_date,
        status='Generado'
    )

    background_tasks.add_task(creando_reporte, db, report, e, "layout.html")

    return {
        "status": "success",
        "data": {
            "report_id": report.id,
            "status": report.status,
            "employee_id": report_in.employee_id,
            "start_date": report_in.start_date,
            "end_date": report_in.end_date,
        }
    }


async def render_template_to_html(data: dict, template_folder: str, template_file: str):
    """
    Render html page using jinja based on template_file
    """
    await asyncio.sleep(0.1)

    template_loader = jinja2.FileSystemLoader(searchpath=template_folder)
    template_env = jinja2.Environment(loader=template_loader)

    template = template_env.get_template(template_file)
    output_text = template.render(data)
    return output_text

async def create_csv(output_dict, csv_path, field_names):
    """ Crea un csv """
    await asyncio.sleep(0.1)
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_names, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(output_dict)


async def create_html(output_text, html_path):
    """ crea un html """
    await asyncio.sleep(0.1)
    html_file = open(html_path, 'wb')
    html_file.write(output_text.encode("UTF-8"))
    html_file.close()

async def html2pdf(html_path, pdf_path, config):
    """
    Convert html to pdf using pdfkit which is a wrapper of wkhtmltopdf
    """
    await asyncio.sleep(0.1)
    options = {
        'page-size': 'Letter',
        'margin-top': '0.35in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    with open(html_path, encoding="UTF-8") as f:
        pdfkit.from_file(f, pdf_path, options=options, configuration=config)

def get_datetime(format: str = "%Y.%m.%d.%H.%M.%S") -> str:
    "Get today's datetime in format"
    today = datetime.datetime.now()
    return today.strftime(format)

def get_date(format: str = "%Y.%m.%d") -> str:
    "Get today's date"
    today = datetime.datetime.now()
    return today.strftime(format)

def get_pdfkit_config():
    """ Obtiene una configuracion para pdfkit """
    try:
        config = pdfkit.configuration()
    except OSError:
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files (x86)\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    return config

async def creando_reporte(db, report: ReportSchema, employee: EmployeeSchema, layout_name: str):
    """ Crea un reporte en los formatos ``html``, ``csv``, ``pdf``"""

    await reports.update(db, report.id, "En proceso")

    marcas_orm = punchs.get_by_filter(db, employee_ids=[report.employee_id],
                                      start_punch_date=report.start_date,
                                      end_punch_date=report.end_date)
    await asyncio.sleep(0.1)

    now = get_datetime()
    marcas = [ PunchModel.model_validate(marca) for marca in marcas_orm]

    csv_path = f'{settings.RESULT_REPORTS_FOLDER}/{now}.csv'
    field_names = ['id', 'employee_id', 'punch_date','punch_hour']
    await create_csv([marca.model_dump(include={f for f in field_names})
                for marca in marcas],
                csv_path, field_names
                )

    data = {
        'marcas': marcas,
        'company_name': employee.company.name,
        'datetime_now': now,
        'employee_first_name':employee.first_name,
        'employee_last_name':employee.last_name,
        'employee_email':employee.email,

    }
    output_text = await render_template_to_html(
        data=data,
        template_folder=settings.TEMPLATES_FOLDER,
        template_file=layout_name
    )

    html_path = f'{settings.RESULT_REPORTS_FOLDER}/{now}.html'
    await create_html(output_text, html_path)

    pdf_path = f'{settings.RESULT_REPORTS_FOLDER}/{now}.pdf'
    await html2pdf(html_path, pdf_path, get_pdfkit_config())

    await report_file.create_file(db, report.id, "csv", await get_file(csv_path))
    await report_file.create_file(db, report.id, "html", await get_file(html_path))
    await report_file.create_file(db, report.id, "pdf", await get_file(pdf_path))

    await reports.update(db, report.id, "Finalizado", datetime.datetime.now(datetime.timezone.utc))

async def get_file(pdf_path):
    await asyncio.sleep(0.1)
    with open(pdf_path, 'rb') as file:
        data = file.read()
    return data

@reports_routes.get("/{report_id}", status_code=201)
async def download_report(
    report_id: int,
    format: str = None,
    db: Session = Depends(deps.get_db)):
    """ Descarga un reporte segun `report_id` y el `format` """

    try:
        ReportFileModel(report_id=report_id, format=format)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(e))

    reporte = await reports.get_by_id(db, report_id)
    if reporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found report")

    if reporte.finish_at is None:
        return JSONResponse(content=jsonable_encoder(ReportCreationModel.model_validate(reporte)), status_code=status.HTTP_425_TOO_EARLY)

    reporte_file = await report_file.get_by_id_format(db, report_id, format)
    if reporte_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found report file")

    mime = {
        'html':'text/html',
        'csv':'text/csv',
        'pdf':'application/pdf'
    }
    mime_type = mime[format]
    file_name = f'report_{report_id}.{format}'

    return StreamingResponse(
        BytesIO(reporte_file.binary),
        headers={
            "Content-Disposition": f"inline; filename={file_name}",
            "Content-Length": f"{reporte_file.size}",
        },
        media_type=mime_type
    )