FROM nginx:alpine

COPY ./templates /usr/share/nginx/html/templates
COPY ./styles /usr/share/nginx/html/styles
COPY ./scripts /usr/share/nginx/html/scripts

COPY ./templates/login.html /usr/share/nginx/html/index.html

EXPOSE 8079
