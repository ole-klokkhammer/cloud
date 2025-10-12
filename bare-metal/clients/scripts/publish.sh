#!/usr/bin/env bash
set -euo pipefail

PUBLISH_FILE=".publish"  
if [[ ! -f $PUBLISH_FILE ]]; then
  echo "$PUBLISH_FILE not found"; exit 1
fi
  
source "$PUBLISH_FILE"

if [[ -z "${IMAGE:-}" || -z "${TAG:-}" ]]; then
  echo "IMAGE or TAG missing in $PUBLISH_FILE"; exit 1
fi

echo "Current image: $IMAGE:$TAG"

# bump patch version (semver: MAJOR.MINOR.PATCH). Fallback to increment numeric TAG.
if [[ "$TAG" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
  major=${BASH_REMATCH[1]}
  minor=${BASH_REMATCH[2]}
  patch=${BASH_REMATCH[3]}
  patch=$((patch+1))
  newtag="${major}.${minor}.${patch}"
else
  # try numeric increment, otherwise append -1
  if [[ "$TAG" =~ ^[0-9]+$ ]]; then
    newtag=$((TAG+1))
  else
    newtag="${TAG}-1"
  fi
fi

echo "Bumping tag: $TAG -> $newtag"

# update .deployment (preserve IMAGE line)
# Use a temp file to be safe
tmp="$(mktemp)"
awk -v nt="$newtag" '
  /^TAG=/ { print "TAG=" nt; next }
  { print }
' "$PUBLISH_FILE" > "$tmp" && mv "$tmp" "$PUBLISH_FILE"

echo "Updated $PUBLISH_FILE"

# full image ref
IMAGE_FULL="${IMAGE}:${newtag}"
echo "Building ${IMAGE_FULL} with buildx..."

# ensure docker available
if ! command -v docker >/dev/null 2>&1; then
  echo "docker not installed or not in PATH" >&2
  exit 1
fi

# ensure buildx builder exists and is selected
BUILDER_NAME="${BUILDER_NAME:-mybuilder}"
if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
  echo "Creating buildx builder '${BUILDER_NAME}' and setting it as current"
  docker buildx create --name "$BUILDER_NAME" --use >/dev/null
else
  docker buildx use "$BUILDER_NAME"
fi

# default platforms (override by exporting BUILD_PLATFORMS)
BUILD_PLATFORMS="${BUILD_PLATFORMS:-linux/amd64}"

# perform buildx build + push
docker buildx build --platform "$BUILD_PLATFORMS" -t "${IMAGE_FULL}" --push .

echo "Built and pushed ${IMAGE_FULL} via buildx" 