FROM amazon/aws-lambda-python:3.12

RUN /var/lang/bin/python3.12 -m pip install --upgrade pip

COPY lambda_function.py ./
COPY requirements.txt ./
COPY model_pt ./model_pt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["lambda_function.handler"]
