FROM mambaorg/micromamba:latest

RUN micromamba install -y -c conda-forge pdal python-pdal numpy boto3 awslambdaric && \
    micromamba clean --all --yes

COPY run.py ./run.py

CMD ["python", "run.py"]
