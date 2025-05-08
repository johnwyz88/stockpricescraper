FROM public.ecr.aws/lambda/python:3.9

# Copy function code and requirements
COPY ../scraper/*.py ${LAMBDA_TASK_ROOT}/
COPY ../scraper/requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler
CMD [ "lambda_handler.lambda_handler" ]
