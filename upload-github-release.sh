#!/bin/bash

# Upload generated packages as github release
#
# Prerequisites:
# 1. github-release tool(https://github.com/aktau/github-release) is available in path.
# 2. Environment variables are set:
#  - GITHUB_USER
#  - GITHUB_TOKEN
#  - RELEASE_TAG

function upload() {
    local fname=$1
    local name=$(basename ${fname})
    echo "upload $fname"
    github-release upload -r lrte -t ${RELEASE_TAG} -n ${name} -f ${fname}
}

function error() {
    echo "$@"
    exit 1
}

if [ -z $RELEASE_TAG ]; then
    error "RELEASE_TAG environment variable needs to be set, like v2.0_0"
fi

set -e

for fname in $@; do
    upload ${fname}
done
github-release info -r lrte -t ${RELEASE_TAG}
