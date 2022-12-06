FROM python:3-slim

WORKDIR /root

COPY cease_and_desist/requirements.txt cease_and_desist/requirements.txt

RUN pip install -r cease_and_desist/requirements.txt

COPY cease_and_desist cease_and_desist

RUN pip install -e cease_and_desist

CMD serve-cease-and-desist-sans /tmp/fonts/*.woff2 --port 8080
