#!/bin/bash
export DOCKER_BUILDKIT=1

# If building the standalone Docker version we won't have OKD variables set
# so we need to play with the version tag string appropriately to get the latest version
if [[ -z ${RUCIO_AMS_VERSION} ]]; then
    tag_str="latest"
else
    tag_str="${RUCIO_AMS_VERSION}"
fi

echo "Building with tag: ${tag_str}"

docker build --no-cache \
    -t rucio-autotransfer \
    --build-arg rucio_version=${tag_str} \
    ${PWD}
