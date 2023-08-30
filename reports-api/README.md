# challenge_scm

## API

### Endpoints

- POST Crear un reporte
- GET Obtener un reporte

#### POST Crear un reporte

`POST` `http://127.0.0.1:8000/v1/reports/`

**Body**
```json
{
    "employee_id": 2,
    "start_date": "2023-01-01",
    "end_date": "2023-01-24"
}
```

##### Response

###### 200 - Success

```json
{
  "status": "string",
  "data": {
    "employee_id": 0,
    "start_date": "2023-08-29",
    "end_date": "2023-08-29",
    "report_id": 0,
    "status": "string"
  }
}
```
###### 404 - Not Found
```json
{
    "detail": "Employee not found"
}
```

#### GET Obtener un reporte

`GET` `http://127.0.0.1:8000/v1/reports/{report_id}?format=html`

|Parámetro|Valor|Ejemplos|
|-|-|-|
|report_id|int|123|
|format|str|html, csv, pdf|

##### Ejemplo

`http://127.0.0.1:8000/v1/reports/5?format=html`



Challenge SCM
