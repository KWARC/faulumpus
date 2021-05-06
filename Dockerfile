FROM python:3.9

WORKDIR /app/
ADD faulumpus /app/
VOLUME /app/saved

ENV HOST 0.0.0.0
ENV PORT 8000
EXPOSE 8000
CMD [ "python", "/app/server.py" ]