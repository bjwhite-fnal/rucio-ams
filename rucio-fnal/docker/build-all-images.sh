# Build all Docker images associated with Rucio.
# Use NO_CACHE_DOCKER_BUILD=<any value that is not 0/False> to signify a "from scratch" rebuild of the image

if [[ -z $NO_CACHE_DOCKER_BUILD ]]; then
    echo "********************* Building Docker images using cached layers *********************"
else
    echo "********************* Building Docker images from scratch (--no-cache) *********************"
    
fi
    ./build-daemons-base.sh && ./build-daemons.sh && ./build-server-base.sh && ./build-server.sh && ./build-cache.sh && ./build-messenger.sh
