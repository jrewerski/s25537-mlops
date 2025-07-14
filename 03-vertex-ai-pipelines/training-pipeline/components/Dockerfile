FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./evaluate_svc_model.py .
COPY ./get_data.py .
COPY ./get_parent_model.py .
COPY ./preprocess_data.py .
COPY ./register_model.py .
COPY ./train_svc_model.py .