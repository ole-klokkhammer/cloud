#
IMAGE = registry.linole.org/lidarr-feeder
TAG = 1.0.36

# Default target: build and push
all: build push

# Build the Docker image
build:
	docker build -t $(IMAGE):$(TAG) -f Dockerfile .

# Push the tagged image to the remote registry
push:
	docker push $(IMAGE):$(TAG)

# Update the version in Makefile and job.hcl (increments the last digit of the TAG)
bump:
	@echo "Bumping version..."
	@VERSION=$$(grep 'TAG =' Makefile | cut -d '=' -f 2 | tr -d ' '); \
	  LAST_DIGIT=$${VERSION##*.} ; \
	  NEW_DIGIT=$$((LAST_DIGIT + 1)) ; \
	  NEW_VERSION=$${VERSION%.*}.$$NEW_DIGIT ; \
	  sed -i "s/^TAG = .*/TAG = $$NEW_VERSION/" Makefile ; \
	  sed -i "s/image       = \".*:\".*/image       = \"$(IMAGE):$$NEW_VERSION\"/" job.hcl
	@echo "Updated version to: $$(grep 'TAG =' Makefile | cut -d '=' -f 2 | tr -d ' ')"

# Deploy the job to the Nomad cluster
deploy:
	nomad job run job.hcl

# Full pipeline: bump version, build, push, and deploy
release: bump build push deploy

# Remove the local image to force a clean build
clean:
	docker rmi $(IMAGE):$(TAG)

.PHONY: all build push bump clean