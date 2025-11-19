#!/bin/bash

set -euo pipefail

APPLY=true
SRC_DIR="${SRC_DIR:-src}"

usage() {
  echo "Usage: $0 [--no-apply|-n] [--src|-s <dir>] [-h|--help]"
  echo "  --no-apply, -n     Build/push only; skip kubectl apply"
  echo "  --src, -s <dir>    Source directory to docker build (default: ${SRC_DIR})"
  echo "  -h, --help         Show this help"
  exit "${1:-0}"
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-apply|-n) APPLY=false; shift ;;
    --src|-s)
      [[ $# -ge 2 ]] || { echo "Error: --src requires a value" >&2; usage 1; }
      SRC_DIR="$2"; shift 2 ;;
    -h|--help) usage 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage 1 ;;
  esac
done

# Read APP_NAME from the first 'app:' label in deployment.yaml
APP_NAME=$(grep -m1 'app:' deployment.yaml | awk '{print $2}')
if [[ -z "${APP_NAME:-}" ]]; then
  echo "Error: could not determine APP_NAME from deployment.yaml" >&2
  exit 1
fi

# Step 1: Auto-bump the patch version
PREV_VERSION=$(grep -m1 -oP "ole-klokkhammer/${APP_NAME}:\K[0-9]+\.[0-9]+\.[0-9]+" deployment.yaml || true)
if [[ -z "${PREV_VERSION}" ]]; then
  echo "Error: could not find existing image tag for ${APP_NAME} in deployment.yaml" >&2
  exit 1
fi
IFS='.' read -r major minor patch <<< "${PREV_VERSION}"
NEW_VERSION="${major}.${minor}.$((patch + 1))"

echo "${PREV_VERSION}"

# Step 2: Update the Docker image version in the Kubernetes deployment configuration
sed -i "s#ghcr.io/ole-klokkhammer/${APP_NAME}:${PREV_VERSION}#ghcr.io/ole-klokkhammer/${APP_NAME}:${NEW_VERSION}#g" deployment.yaml

# Step 3: Build and push the new Docker image
if [[ ! -d "${SRC_DIR}" ]]; then
  echo "Error: source directory not found: ${SRC_DIR}" >&2
  exit 1
fi
pushd "${SRC_DIR}" >/dev/null
docker buildx build --push --platform linux/amd64 -t "ghcr.io/ole-klokkhammer/${APP_NAME}:${NEW_VERSION}" .
popd >/dev/null

# Step 4: Optionally apply the updated deployment configuration
if [[ "${APPLY}" == "true" ]]; then
  kubectl apply -f deployment.yaml
else
  echo "Skipping kubectl apply (--no-apply)."
fi