# Reports-api

El sistema de Reports-API está creado con FASTAPI utilizando python 3.11.4

EL sistema Reports-api requiere ejecutarse utilizando una base de datos MySQL 8.

## Reports-API

La imagen de reports api requiere las siguientes variables de entorno:

**``DB_USER``**

Indica el nombre de usuario que se utilizará en MySQL

**``DB_PASS``**

Indica la contraseña del usuario que se utilizará en MySQL

**``DB_NAME``**

Indica el nombre de la base de datos que se utilizará en MySQL

**``DB_HOST``**

Indica la dirección de la base de datos que se utilizará en el sistema.

**``ENV``**

Indica el ambiente en que se ejecutará. Si se envía el valor `DEV`, al ejecutarse el sistema reportes-api se creará data dummy.

**``PORT``**

Indica el puerto en que se ejecutará el servicio Reports-api.

Ejemplo de .env

```env
DB_USER = "user"
DB_PASS = "password"
DB_NAME = "reports"
DB_HOST = "mysql"
ENV = "DEV"
PORT = 8000
```

## MYSQL

[Referencia MYSQL IMAGES DOCKER](https://hub.docker.com/_/mysql)

## MYSQL Environment Variables

Como minimo es requerido los siguientes variables de entorno para ejecutar la imagen de docker de mysql:

```env
MYSQL_DATABASE
MYSQL_USER
MYSQL_PASSWORD
```

Además es necesario alguno de los siguientes para establecer la contraseña de usuario root.

```env
MYSQL_ROOT_PASSWORD
MYSQL_ALLOW_EMPTY_PASSWORD
MYSQL_RANDOM_ROOT_PASSWORD
```
