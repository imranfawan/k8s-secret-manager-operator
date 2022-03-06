FROM python

WORKDIR /app

RUN pip3 install --upgrade \
    boto3==1.21.13 \
    kubernetes

COPY k8s-secret-from-aws-secret-mgr.py .

CMD [ "python3", "--version"]