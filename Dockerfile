FROM python:3

WORKDIR /root

ADD cease_and_desist cease_and_desist

RUN pip install --upgrade pip setuptools wheel
RUN pip install -e cease_and_desist

CMD serve-cease-and-desist-sans /tmp/fonts/*.woff2 --port 8080
