#####################################################################
### DEPENDENCIES INSTALLATION
#####################################################################
FROM python:3.11.4-slim-bullseye AS build-stage

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install --upgrade wheel

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN pip uninstall wheel -y
RUN pip uninstall pip -y

WORKDIR /opt/venv
RUN find . -name *.pyc -delete

################################################
FROM python:3.11.4-slim-bullseye AS deploy-stage
LABEL maintainer="sergio.mora@scmlatam.com"

COPY --from=build-stage /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./ /opt/

WORKDIR /opt/

RUN apt-get update && apt-get install -y wkhtmltopdf

RUN groupadd -r my_grupo && useradd -r -g my_grupo my_user

RUN chown -R my_user:my_grupo /opt/src/res/
RUN chmod -R u+rwx /opt/src/res/

USER my_user

EXPOSE ${PORT}

CMD alembic upgrade head && python ./test/test_company.py && uvicorn src.main:app --host=0.0.0.0 --port=${PORT}