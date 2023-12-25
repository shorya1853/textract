FROM public.ecr.aws/lambda/python:3.12

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

COPY tesse.sh /tmp/tesse.sh
RUN chmod +x /tmp/tesse.sh
Run sh /tmp/tesse.sh

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ENV TESSERACT_PATH=/usr/local/bin/tesseract
ENV TESSDATA_PREFIX=/root/tesseract-ocr/tessdata
#export TESSDATA_PREFIX = "/usr/share/tessdata"

CMD [ "lambda_function.lambda_handler" ]



