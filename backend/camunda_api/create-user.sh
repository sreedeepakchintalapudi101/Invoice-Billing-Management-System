#!/bin/bash
# create-user.sh

echo "Creating Camunda admin user..."

$CATALINA_HOME/bin/camunda.sh create admin admin 1234

# Start Tomcat
exec $CATALINA_HOME/bin/catalina.sh run