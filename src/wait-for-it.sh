#!/usr/bin/env bash
# wait-for-it.sh - Wait until a service is ready
# Usage: ./wait-for-it.sh host:port -- command_to_run

set -e

HOSTPORT="$1"
shift
CMD="$@"

HOST=$(echo $HOSTPORT | cut -d ':' -f 1)
PORT=$(echo $HOSTPORT | cut -d ':' -f 2)

echo "Waiting for $HOST:$PORT..."

while ! nc -z $HOST $PORT; do
  sleep 1
done

echo "$HOST:$PORT is available, starting command..."
exec $CMD
