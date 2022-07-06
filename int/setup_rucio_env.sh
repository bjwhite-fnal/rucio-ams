# Environtment set up file for the int testing "experiment" 

deactivate () {
    # with reference from python's venv activate

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "${BASH:-}" -o -n "${ZSH_VERSION:-}" ] ; then
        hash -r
    fi

    if [ -n "${_OLD_PS1:-}" ] ; then
        PS1="${_OLD_PS1:-}"
        export PS1
        unset _OLD_PS1
    fi


    if [ ! "$1" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate
    fi

}

deactivate nondestructive

# always use 'latest' tag when building docker images
export RUCIO_AMS_DEV=true

# I love parallel builds!
export DOCKER_BUILDKIT=1
#export RUCIO_AMS_VERSION=1.23.11.post2
#export RUCIO_AMS_VERSION=1.23.14
#export RUCIO_AMS_VERSION=1.24.5.post1
#export RUCIO_AMS_VERSION=1.25.7
#export RUCIO_AMS_VERSION=1.26.1.post1
#export RUCIO_AMS_VERSION=1.26.5
#export RUCIO_AMS_VERSION=1.26.6
#export RUCIO_AMS_VERSION=1.26.7
#export RUCIO_AMS_VERSION=1.26.8
#export RUCIO_AMS_VERSION=1.26.9
export RUCIO_AMS_VERSION=1.26.13

if [ -z ${RUCIO_AMS_DEV} ]; then
    export RUCIO_AMS_VERSION_TAG=${RUCIO_AMS_VERSION}
else
    export RUCIO_AMS_VERSION_TAG="latest"
fi

# Make sure to set EXPERIMENT, RUCIO_AMS_DIR, AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE
# Optionally set RUCIO_AMS_EXT_SERVER_IP, RUCIO_AMS_EXT_AUTH_IP, RUCIO_AMS_EXT_WEBUI_IP, RUCIO_AMS_EXT_MSG_IP
# For AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE only the filenames are needed.
#   The files should be resident in $AMS_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export EXPERIMENT=int
export RUCIO_AMS_DIR=/nashome/b/bjwhite/dev/rucio/rucio-ams
export AMS_RUCIO_CERT=int-rucio.okd.fnal.gov-cert.pem
export AMS_RUCIO_KEY=int-rucio.okd.fnal.gov-key.pem
export AMS_RUCIO_CA_BUNDLE=ca_bundle.pem

#export RUCIO_AMS_EXT_SERVER_IP=131.225.218.134
#export RUCIO_AMS_EXT_AUTH_IP=131.225.218.147
#export RUCIO_AMS_EXT_WEBUI_IP=131.225.218.148
#export RUCIO_AMS_EXT_MSG_IP=131.225.218.149

_OLD_PS1="${PS1:-}"
PS1="[rucio-$EXPERIMENT $RUCIO_AMS_VERSION] ${PS1:-}"
export PS1

# This should detect bash and zsh, which have a hash command that must
# be called to get it to forget past commands.  Without forgetting
# past commands the $PATH changes we made may not be respected
if [ -n "${BASH:-}" -o -n "${ZSH_VERSION:-}" ] ; then
    hash -r
fi
