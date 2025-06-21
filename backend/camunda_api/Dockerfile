FROM camunda/camunda-bpm-platform:run-latest

# COPY ./processes/*.bpmn /camunda_api/configuration/resources/
COPY create-user.sh /camunda_api/create-user.sh
RUN chmod +x /camunda_api/create-user.sh

CMD ["/camunda_api/create-user.sh"]