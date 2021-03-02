FROM rackspacedot/python37
RUN  apt-get update && apt-get install -y --force-yes jq

RUN pip3 install --upgrade pip

WORKDIR /api

COPY . /api

RUN pip --no-cache-dir install -r requirements.txt

WORKDIR /api/src
EXPOSE 443

#CMD ["uvicorn", "main:app", "--reload"]
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "443", "--ssl-certfile", "./certs/cert1.pem", "--ssl-keyfile", "./certs/privkey1.pem", "main:app" ]