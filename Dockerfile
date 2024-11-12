FROM python:3.12

WORKDIR /usr/src/app
COPY . .
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libgl1
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 7860

CMD ["python", "gradio_demo.py"]