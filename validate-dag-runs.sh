#!/usr/bin/env bash
AIRFLOW_UI_PORT=8080
AIRFLOW_ADMIN_USR="airflow"
AIRFLOW_ADMIN_PWD="airflow"
AIRFLOW_API_BASE_URI="api/v2"

set -ex
detect_potential_dag() {
  test "$(find "${CHAPTER}"/dags "${CHAPTER}"/*/dags -type f -name '*.py' -maxdepth 1 -o -name '*.zip' | wc -l)" -gt 0
}

check_next_dagrun_scheduled_today() {
  local DAG_ID=$1
  echo "Checking next dagrun for ${DAG_ID}" >&2
  result=$(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}" | jq '.next_dagrun // (now | todate) | split("T") | .[0] | strptime("%Y-%m-%d") | strftime("%Y%m%d") | tonumber - (now | strftime("%Y%m%d") | tonumber)')
  echo "Result of checking next dagrun for ${DAG_ID} is ${result} (days from now)" >&2
  if [ "${result}" -le 0 ]; then
    true
  else
    false
  fi
}

trigger_dagrun() {
  local DAG_ID=$1
  echo "Manually triggering dagrun for ${DAG_ID}" >&2
  result=$(curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}/dagRuns" -d "{\"logical_date\": \"$(date +%FT%T%z)\"}" | jq)
  echo "Result of triggering dagrun for ${DAG_ID} is ${result}" >&2
  sleep 5;
}

test_dag_state() {
  local DAG_ID=$1
  local STATE=$2
  local SHOW_RESULT=${3:-false}
  echo "Checking dag state(${STATE}) for ${DAG_ID}" >&2
  result=$(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}/dagRuns" | jq ".dag_runs | map(select(.state == \"${STATE}\")) | length")
  echo "Result of checking dag state(${STATE}) for ${DAG_ID} is ${result}" >&2
  if [ "${SHOW_RESULT}" == true ]; then
    output=$(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}/dagRuns" | jq ".dag_runs" )
    echo "Dagruns: $output" >&2
    sleep 5 # Wait for the task states to be up to date
    output=$(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}/dagRuns/~/taskInstances" | jq ".task_instances" )
    echo "Tasks: $output" >&2
    sleep 5 # Wait for the logs to be available
    # shellcheck disable=SC2207
    log_urls=($(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}/dagRuns/~/taskInstances" | jq -r '.task_instances[] | select(.state!="success" and .try_number>0) | .dag_run_id + "/taskInstances/" + .task_id + "/logs/" + (.try_number|tostring)'))
    for uri in "${log_urls[@]}"; do
      output=$(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}/dagRuns/${uri}")
      echo "Tasks Instance: $uri" >&2
      echo "    Log Output: " >&2
      echo "" >&2
      echo "$output" >&2
    done
  else
    echo "$result"
  fi
}

test_dag_errors() {
  local DAG_ID=$1
  local SHOW_RESULT=${2:-false}
  echo "Checking dag ${DAG_ID} for errors." >&2
  result=$(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/importErrors" | jq ".total_entries")
  echo "Result of checking dag errors for ${DAG_ID} is ${result}" >&2
  if [ "${SHOW_RESULT}" == true ]; then
    output=$(curl -s -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/importErrors" | jq )
    echo "ImportErrors: $output" >&2
  else
    echo "$result"
  fi
}

debug_log_airflow() {
  echo "Available dags:"
  curl -X GET -H 'Content-Type: application/json' -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags" || true
  echo "Dag Import Errors:"
  curl -X GET -H 'Content-Type: application/json' -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/importErrors" || true
  echo "Docker containers running:"
  docker ps
  echo "Airflow container logs:"
  services=$(docker compose -f "${CHAPTER}/compose.yaml" -f "${CHAPTER}/compose.override.yaml" config --services)
  for svc in ${services}; do
    echo "Showing logs of service ${svc}"
    docker compose -f "${CHAPTER}/compose.yaml" -f "${CHAPTER}/compose.override.yaml" logs "${svc}"
  done
}

check_dagrun_result() {
  local DAG_ID=${1}
  local RETRY=${2:-true}

  while [ "$(test_dag_state "${DAG_ID}" "running")" -gt 0 ]; do
    echo "Dag '${DAG_ID}' is (still) running..."
    sleep 5;
  done
  SUCCES_STATE="success"
  FAILURE_STATE="failed"
  if [ "${CI_EXPECT_FAILURE}" == true ]; then
    SUCCES_STATE="failed"
    FAILURE_STATE="success"
  fi
  if [ "$(test_dag_state "${DAG_ID}" "${SUCCES_STATE}")" -ge 1 ]; then
    echo "Dag '${DAG_ID}' run(s) successfully finished"
    # stop
    return 0
  fi
  if [ "$(test_dag_state "${DAG_ID}" "${FAILURE_STATE}")" -ge 1 ]; then
    echo "Dag '${DAG_ID}' run(s) failed"
    # output dagrun result
    test_dag_state "${DAG_ID}" "${FAILURE_STATE}" true
    return 1
  else
    echo "Dag '${DAG_ID}' neither success nor failed!!!"
    if ${RETRY}; then
      echo "Maybe there was no dagrun for dag ${DAG_ID}. Retry after manual trigger"
      trigger_dagrun "${DAG_ID}"
      check_dagrun_result "${DAG_ID}" false
    else
      # output dagrun result
      test_dag_state "${DAG_ID}" "${FAILURE_STATE}" true
      debug_log_airflow
      return 7
    fi
  fi
}

start() {
    echo "Starting chapter run for chapter ${CHAPTER}"

    if [ -z "${DAG_IDS}" ]; then
      DAG_IDS=$(grep -Eo "dag_id=['\"](.*)['\"]" "${CHAPTER}"/dags/*.py | sed -E "s/.*=['\"](.*)['\"]/\1/")
      if [ -z "${DAG_IDS}" ]; then
        echo "Unable to determine dag ids for CI_MODE and DAG_ID not provided on commandline."
        exit 4
      else
        echo "Found dag_id(s): ${DAG_IDS} in dag files."
      fi
    fi
    set -o allexport && source "${CHAPTER}"/.env && set +o allexport

    docker compose -f "${CHAPTER}/compose.yaml" -f "${CHAPTER}/compose.override.yaml" up -d --build --force-recreate

    wait_period=0
    while [[ "$(curl -s -o /dev/null -w %\{http_code\} http://localhost:${AIRFLOW_UI_PORT})" != "200" ]]; do
      echo "Waiting for Airflow UI to come up..."
      if [ $wait_period -ge 600 ]; then
        status_code="$(curl -s -o /dev/null -w %\{http_code\} http://localhost:${AIRFLOW_UI_PORT} || true)"
        echo "Been waiting for airflow to start for 10 minutes. Aborting now..."
        echo "Current HTTP status of http://localhost:${AIRFLOW_UI_PORT} is ${status_code}"
        debug_log_airflow
        stop
        exit 3
      else
        wait_period=$((wait_period+10))
        sleep 10;
      fi
    done
    sleep 10;
    AIRFLOW_API_TOKEN=$(curl -s -X POST -H "Accept: application/json" -H "Content-Type: application/json" "http://localhost:${AIRFLOW_UI_PORT}/auth/token" -d "{\"username\": \"${AIRFLOW_ADMIN_USR}\", \"password\": \"${AIRFLOW_ADMIN_PWD}\"}"  | jq -r ".access_token")

    sleep 10; # wait for dags to be available.

    for DAG_ID in ${DAG_IDS}; do
      wait_dagparse_period=0
      echo "Unpausing dag with id ${DAG_ID}."
      while [[ "$(curl -s -o /dev/null -w %\{http_code\} -X PATCH  -H 'Content-Type: application/json' -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}?update_mask=is_paused" -d '{ "is_paused": false }')" != "200" ]]; do
        echo "Unpausing failed. Trying again ..."
        if [ $wait_dagparse_period -ge 60 ]; then
          status_code="$(curl -s -o /dev/null -w %\{http_code\} -X PATCH  -H 'Content-Type: application/json' -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}?update_mask=is_paused" -d '{ "is_paused": false }')"
          echo "Command: curl -X PATCH  -H 'Content-Type: application/json' -H \"Authorization: Bearer *****\"  \"http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}?update_mask=is_paused\" -d '{ \"is_paused\": false }' has status ${status_code}"
          echo "Output:"
          curl -X PATCH  -H 'Content-Type: application/json' -H "Authorization: Bearer ${AIRFLOW_API_TOKEN}" "http://localhost:${AIRFLOW_UI_PORT}/${AIRFLOW_API_BASE_URI}/dags/${DAG_ID}?update_mask=is_paused" -d '{ "is_paused": false }'
          debug_log_airflow
          stop
          exit 5
        else
          wait_dagparse_period=$((wait_dagparse_period+10))
          sleep 10;
        fi
      done
      echo "Unpaused dag with id ${DAG_ID}."
      sleep 5;
      if ! check_next_dagrun_scheduled_today "${DAG_ID}"; then
          echo "Need to trigger the dag ${DAG_ID} since first scheduled time is later than today and unpause is not enough to start running"
          trigger_dagrun "${DAG_ID}"
      fi

      check_dagrun_result "${DAG_ID}"
      dag_status=${?}
      if [ $dag_status -ne 0 ]; then
        echo "Dag unexpectedly failed or succeeded. Aborting validation..."
        exit ${dag_status}
      fi
    done
    stop
}

stop() {
  echo "Closing down the environment"
  docker compose -f "${CHAPTER}/compose.yaml" -f "${CHAPTER}/compose.override.yaml" down --volumes --rmi local --remove-orphans
}

usage() {
  echo "usage: ${BASH_SOURCE[0]} [-h|--help] [-c|--chapter chapter]"
  echo "  -h|--help                          display usage"
  echo "  -c|--chapter chapter               specify chapter to validate"
  echo "  -i|--dag_id dag_id                 specify the dag_id to check (only in ci mode)"
  echo "  -x|--expect_failure true/false     expect dag to fail"
  exit 21
}

function read_arguments() {
  while [[ $# -gt 0 ]]
  do
      key="${1}"
      case ${key} in
      -c|--chapter)
          CHAPTER="${2}"
          shift # past argument
          shift # past value
          ;;
      -i|--dag_id)
          DAG_IDS="${2}"
          shift # past argument
          shift # past value
          ;;
      -x|--expect_failure)
          CI_EXPECT_FAILURE="${2}"
          shift # past argument
          shift # past value
          ;;
      -h|--help)
          usage
          ;;
      *)  # unknown option
          echo "WARNING: Skipping unknown commandline argument: '${key}'"
          shift # past argument
          ;;
      esac
  done
}

function main() {
  read_arguments "$@"

  if detect_potential_dag; then

    start
  else
    echo "No .py or .zip files found in ${CHAPTER} that may contain an Apache Airflow DAG"
    echo "did you correctly specify the chapter directory?"
  fi
}

main "$@"
