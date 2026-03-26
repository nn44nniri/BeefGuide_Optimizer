FROM python:3.11-slim

WORKDIR /opt/BeefGuide_Optimizer

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY BeefMPC_Guide ./BeefMPC_Guide
COPY LiGAPS_Beef ./LiGAPS_Beef

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/BeefGuide_Optimizer

CMD ["python", "-m", "BeefMPC_Guide.service", "--socket-path", "/tmp/beefguide/guide-interface.sock"]
