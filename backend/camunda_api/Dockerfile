FROM camunda/camunda-bpm-platform:run-latest

COPY backend/camunda_api/processes/*.bpmn /camunda_api/configuration/resources/
COPY backend/camunda_api/create-user.sh /camunda_api/create-user.sh
RUN chmod +x /camunda_api/create-user.sh

CMD ["/camunda_api/create-user.sh"]