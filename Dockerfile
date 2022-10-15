FROM python:alpine3.15

WORKDIR root
ADD cease_and_desist cease_and_desist
RUN pip install -e cease_and_desist
VOLUME ["./bad-fonts/", "/bad-fonts"]

CMD serve-cease-and-desist-sans /fonts/*.woff2
