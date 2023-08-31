from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, func
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship
from src.db import Base


class Company(Base):
    __tablename__ = "company"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(250), nullable=False)


class Employee(Base):
    __tablename__ = "employee"

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    company_id = Column(BigInteger, ForeignKey("company.id"), nullable=False)
    company = relationship("Company", uselist=False)

class Location(Base):
    __tablename__ = "location"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    company_id = Column(BigInteger, ForeignKey("company.id"), nullable=False)
    company = relationship("Company", backref="locations")


class Punch(Base):
    __tablename__ = "punch"

    id = Column(BigInteger, primary_key=True)
    employee_id = Column(BigInteger, ForeignKey("employee.id"), nullable=False)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    company_id = Column(BigInteger, ForeignKey("company.id"), nullable=False)
    punch_time = Column(DateTime, nullable=False)

    employee = relationship("Employee", uselist=False)
    location = relationship("Location", uselist=False)
    company = relationship("Company", uselist=False)

class Report(Base):
    __tablename__ = "report"

    id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    employee_id = Column(BigInteger, ForeignKey("employee.id"), nullable=False)
    status = Column(String(250), nullable=False)
    finish_at = Column(DateTime, nullable=True)

class ReportFile(Base):
    __tablename__ = "report_file"

    id = Column(BigInteger, primary_key=True)
    report_id = Column(BigInteger, ForeignKey("report.id"), nullable=False)
    format = Column(String(5), nullable=False)
    binary = Column(mysql.MEDIUMBLOB(2**24), nullable=True)
    size = Column(BigInteger, nullable=True, default=0)