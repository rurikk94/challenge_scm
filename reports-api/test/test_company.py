import sys
import os
from typing import List

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, '..'))

sys.path.append(parent_directory)

from sqlalchemy.orm import Session
from src.db import Session as Sesion

from src.db.models import Company as CompanySchema
from src.db.models import Employee as EmployeeSchema
from src.db.models import Location as LocationSchema
from src.db.models import Punch as PunchSchema


from faker import Faker
from datetime import date, datetime, timedelta

fake = Faker(['es-ES'])


def lista_dias(start_dt: date, end_dt: date) -> list:
    """ genera una lista de días """

    add_td = timedelta(days=1)

    dates_lt = []

    while start_dt <= end_dt:
        dates_lt.append(start_dt.isoformat())
        start_dt += add_td

    return dates_lt

def create_company(db: Session, count: int = 2):
    lst_company = []
    for idx in range(count):
        company = CompanySchema(
            name=fake.company()
        )
        lst_company.append(company)

    db.add_all(lst_company)
    db.commit()
    return lst_company

def create_employees(db: Session, companys: List[CompanySchema], count: int = 5):
    lst_employee= []
    for c in companys:
        for idx in range(count):
            employee = EmployeeSchema(
                first_name=fake.name(),
                last_name=fake.last_name(),
                email=fake.ascii_free_email(),
                company_id=c.id
            )
            lst_employee.append(employee)

    db.add_all(lst_employee)
    db.commit()
    return lst_employee

def create_location(db: Session, companys: List[CompanySchema], count: int = 3):
    lst_location= []
    for c in companys:
        for idx in range(count):
            location = LocationSchema(
                name=fake.name(),
                address=fake.street_address(),
                company_id=c.id
            )
            lst_location.append(location)

    db.add_all(lst_location)
    db.commit()
    return lst_location

def create_punches(db: Session, employees: List[EmployeeSchema], start_date: date = None, end_date: date = None, cant_punches: int = 50):
    start_dt = datetime.fromisoformat('2023-01-01T00:00:00').date() if not start_date else start_date
    end_dt = date.today() if not end_date else end_date

    punches = []

    for e in employees:

        marcas_dt = []

        for dia in lista_dias(start_dt, end_dt):

            entrada_str = f'{dia}T{fake.time()}'
            entrada_dt = datetime.fromisoformat(entrada_str)

            minutos = fake.pyint(min_value=420, max_value=520)
            salida_dt = entrada_dt + timedelta(minutes=minutos)

            marcas_dt.append(entrada_dt)
            marcas_dt.append(salida_dt)

        marcas_dt.sort()


        for marca_dt in marcas_dt:
            marca = PunchSchema(
                employee_id= e.id,
                location_id=e.company.locations[0].id,
                company_id=e.company_id,
                punch_time= marca_dt
            )

            punches.append(marca)

    db.add_all(punches)
    db.commit()

    return punches

db: Session = Sesion()
if (
        os.environ.get('ENV', None) == 'DEV' and
        len(db.query(CompanySchema).all())<1
    ):
    print("Ambiente ENV detectado")
    print("Creando data dummy")

    cant_comp = 3
    print(f"Se crearán {cant_comp} compañias.")
    companys = create_company(db, cant_comp)
    print(f"Creadas {len(companys)} compañias")

    cant_employees = 25
    print(f"Se crearán {cant_employees} empleados por cada compañia.")
    employees = create_employees(db, companys, cant_employees)
    print(f"Creadas {len(employees)} empleados")

    cant_locations = 3
    print(f"Se crearán {cant_locations} locations por cada compañia.")
    locations = create_location(db, companys, cant_locations)
    print(f"Creadas {len(locations)} ubicaciones")

    print("Se crearán 2 marcas de pruebas para cada empleado por cada dia en lo que va de este año.")
    punches = create_punches(db, employees)
    print(f"Creadas {len(punches)} marcas de prueba")



