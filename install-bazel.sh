#!/bin/bash

# Guarantee that if any statement fails, the script bails immediate. 
set -e

# Add the Google Bazel PPA; can only be done after we have curl
echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list
curl -L https://bazel.build/bazel-release.pub.gpg | apt-key add -

# Magical apt-get update incantation to only update a single source from here:
# https://askubuntu.com/questions/65245/apt-get-update-only-for-a-specific-repository/65250
apt-get update -o Dir::Etc::sourcelist="sources.list.d/bazel.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"

apt-get install -y bazel
