FROM continuumio/miniconda3

ENV PATH="/opt/conda/envs/myenv/bin:$PATH"

WORKDIR /app

COPY . /app

RUN conda create --name myenv python=3.8 -y && \
    conda run -n myenv pip install --no-cache-dir -r /app/requirements.txt && \
    conda run -n myenv conda install -y -c conda-forge rdkit

EXPOSE 8000

CMD ["conda", "run", "-n", "myenv", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]