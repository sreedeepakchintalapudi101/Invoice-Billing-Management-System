FROM tomcat:9.0-jdk17

# Copy all Flowable WAR files
ADD flowable-idm.war /usr/local/tomcat/webapps/
ADD flowable-modeler.war /usr/local/tomcat/webapps/
ADD flowable-task.war /usr/local/tomcat/webapps/
ADD flowable-admin.war /usr/local/tomcat/webapps/
ADD flowable-rest.war /usr/local/tomcat/webapps/

# Optional: copy custom config files

# Expose default Tomcat port
EXPOSE 8080

CMD ["catalina.sh", "run"]