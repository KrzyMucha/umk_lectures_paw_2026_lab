#!/usr/bin/env sh
set -eu

ENTITY="user"
IMAGE_NAME="${ENTITY}-service"
CONTAINER_NAME="${ENTITY}-service-local"
HOST_PORT="8081"
CONTAINER_PORT="8080"

start() {
	if [ -z "${DATABASE_URL:-}" ]; then
		echo "DATABASE_URL is required to start user-service" >&2
		exit 1
	fi

	docker build -t "${IMAGE_NAME}" .

	if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
		docker rm -f "${CONTAINER_NAME}" >/dev/null
	fi

	docker run -d \
		--name "${CONTAINER_NAME}" \
		-p "${HOST_PORT}:${CONTAINER_PORT}" \
		-e PORT="${CONTAINER_PORT}" \
		-e DATABASE_URL="${DATABASE_URL}" \
		"${IMAGE_NAME}" >/dev/null

	echo "Service running at http://localhost:${HOST_PORT}"
}

stop() {
	if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
		docker rm -f "${CONTAINER_NAME}" >/dev/null
		echo "Stopped ${CONTAINER_NAME}"
	else
		echo "Container ${CONTAINER_NAME} is not running"
	fi
}

logs() {
	docker logs -f "${CONTAINER_NAME}"
}

case "${1:-start}" in
	start)
		start
		;;
	stop)
		stop
		;;
	logs)
		logs
		;;
	*)
		echo "Usage: $0 [start|stop|logs]"
		exit 1
		;;
esac
