#!/bin/bash

uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

if [[ -n "$PROXY_USER" && -n "$PROXY_PASSWORD" ]]; then
  until curl --silent --fail http://localhost:8000/docs > /dev/null; do
    sleep 1
  done

  echo "Create user $PROXY_USER"
  curl -X POST http://localhost:8000/api/users/create \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${PROXY_USER}\", \"password\": \"${PROXY_PASSWORD}\", \"email\": \"test@example.com\"}"
fi

wait $SERVER_PID
