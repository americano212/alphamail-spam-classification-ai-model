# Use the Amazon Linux base image for AWS Lambda with Python 3.12
FROM amazon/aws-lambda-python:3.12

# Upgrade pip to the latest version
RUN /var/lang/bin/python3.12 -m pip install --upgrade pip

# Copy the lambda function script and requirements file to the container
COPY lambda_function.py ./
COPY requirements.txt ./
COPY model_pt ./model_pt

# Install the Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Define the Lambda handler
CMD ["lambda_function.handler"]
