FROM python:3.8-alpine
WORKDIR /root
COPY revoke_aws_access_key.py /root/revoke_aws_access_key.py
COPY requirements.txt /root/requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "/root/revoke_aws_access_key.py"]
