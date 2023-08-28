import asyncio
import csv
import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse
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
from src.models.reports import ReportCreationRequestModel, ReportCreationResponseModel, ReportFileModel
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


def render_template_to_html(data: dict, template_folder: str, template_file: str):
    """
    Render html page using jinja based on template_file
    """

    template_loader = jinja2.FileSystemLoader(searchpath=template_folder)
    template_env = jinja2.Environment(loader=template_loader)

    template = template_env.get_template(template_file)
    output_text = template.render(data)
    return output_text

def create_csv(output_dict, csv_path, field_names):
    """ Crea un csv """
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_names, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(output_dict)


def create_html(output_text, html_path):
    """ crea un html """
    html_file = open(html_path, 'wb')
    html_file.write(output_text.encode("UTF-8"))
    html_file.close()

def html2pdf(html_path, pdf_path, config):
    """
    Convert html to pdf using pdfkit which is a wrapper of wkhtmltopdf
    """
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

    marcas_orm = punchs.get_by_employee(db, report.employee_id)
    await reports.update(db, report.id, 10)
    await asyncio.sleep(0.1)

    await asyncio.sleep(0.1)
    BASE_PATH = Path(__file__).resolve().parent
    now = get_datetime()
    marcas = [ PunchModel.model_validate(marca) for marca in marcas_orm]

    csv_path = f'{settings.RESULT_REPORTS_FOLDER}/{now}.csv'
    field_names = ['id', 'employee_id', 'punch_date','punch_hour']
    create_csv([marca.model_dump(include={f for f in field_names})
                for marca in marcas],
                csv_path, field_names
                )
    await reports.update(db, report.id, 30)

    data = {
        'marcas': marcas,
        'company_name': employee.company.name,
        'datetime_now': now,
        'employee_first_name':employee.first_name,
        'employee_last_name':employee.last_name,
        'employee_email':employee.email,

    }
    output_text = render_template_to_html(
        data=data,
        template_folder=settings.TEMPLATES_FOLDER,
        template_file=layout_name
    )

    await asyncio.sleep(0.1)
    html_path = f'{settings.RESULT_REPORTS_FOLDER}/{now}.html'
    create_html(output_text, html_path)
    await reports.update(db, report.id, 50)

    await asyncio.sleep(0.1)
    pdf_path = f'{settings.RESULT_REPORTS_FOLDER}/{now}.pdf'
    config_pdfkit = get_pdfkit_config()
    html2pdf(html_path, pdf_path, config_pdfkit)
    await reports.update(db, report.id, 80)

    await asyncio.sleep(0.1)
    await reports.update(db, report.id, 100, datetime.datetime.now(datetime.timezone.utc))

    await asyncio.sleep(0.1)
    with open(csv_path, 'rb') as file:
        binary_data = file.read()
    await report_file.create_file(db, report.id, "csv", binary_data)

    await asyncio.sleep(0.1)
    with open(html_path, 'rb') as file:
        binary_data_html = file.read()
    await report_file.create_file(db, report.id, "html", binary_data_html)

    await asyncio.sleep(0.1)
    with open(pdf_path, 'rb') as file:
        binary_data_pdf = file.read()
    await report_file.create_file(db, report.id, "pdf", binary_data_pdf)




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
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY, detail="Not report finished")

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