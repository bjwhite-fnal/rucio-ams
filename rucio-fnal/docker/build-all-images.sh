#export NO_CACHE_DOCKER_BUILD=1
./build-daemons-base.sh && ./build-daemons.sh && ./build-server-base.sh && ./build-server.sh
#unset NO_CACHE_DOCKER_BUILD
