#!/bin/bash
# create-user.sh

echo "Creating Camunda Admin user..."
curl -X POST "http://localhost:8080/engine-rest/user/create" \
        -H "Content-Type: application/json" \
        -d '{
              "id": "admin",
              "firstName": "Admin",
              "lastName": "User",
              "password": "admin",
                "email": "chsdgoi101@gmail,com"
            }'

echo "User created successfully..."