FROM nginx:alpine

# Copy frontend assets into nginx's public directory
COPY ./templates /usr/share/nginx/html/templates
COPY ./styles /usr/share/nginx/html/styles
COPY ./scripts /usr/share/nginx/html/scripts

# Set the login page as the default entry point
COPY ./templates/login.html /usr/share/nginx/html/index.html

# Expose port 80
EXPOSE 80
