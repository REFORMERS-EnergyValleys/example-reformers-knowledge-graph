#!/bin/bash

GRAPHDB_HOST=${GRAPHDB_HOST:-graphdb}
GRAPHDB_PORT=${GRAPHDB_PORT:-7200}
GRAPHDB_REPO_NAME=${GRAPHDB_REPO_NAME}

REPO_HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" -i "${GRAPHDB_HOST}:${GRAPHDB_PORT}/rest/repositories/${GRAPHDB_REPO_NAME}")

if [ "${REPO_HTTP_STATUS}" -eq "404" ]; then

    # Create repository definition file
    sed "s/__GRAPHDB_REPO_NAME__/${GRAPHDB_REPO_NAME}/g" /api/repo-config.ttl.template > /tmp/repo-config.ttl

    echo ">>> Create new repository"
    curl -s -X POST "${GRAPHDB_HOST}:${GRAPHDB_PORT}/rest/repositories" -H "Content-Type: multipart/form-data" -F "config=@/tmp/repo-config.ttl"

    # List files to be imported to the repository
    mapfile -d '' entries < <(find "/imports" -maxdepth 1 -mindepth 1 -printf '%f\0' | sort -z)

    # Create JSON-formatted file list
    { printf '{"fileNames":['
      for i in "${!entries[@]}"; do
        (( i > 0 )) && printf ','
        printf '"%s"' "${entries[i]}"
      done
      printf ']}\n'
    } > "/tmp/repo-import.json"

    echo ">>> Import data"
    curl -s -X POST "${GRAPHDB_HOST}:${GRAPHDB_PORT}/rest/repositories/${GRAPHDB_REPO_NAME}/import/server" -H 'Content-Type: application/json' -d '@/tmp/repo-import.json'

elif [ "${REPO_HTTP_STATUS}" -eq "200" ]; then

  echo ">>> Repository already exixts"

else

  echo ">>> Error creating repository - Server returned ${REPO_HTTP_STATUS}"
  exit 1

fi
