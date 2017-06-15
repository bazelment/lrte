# This script will install the prebuilt release deb packages hosted by
# github.

# Make sure apt support pulling package using https
apt-get update
# apt-add-repository belongs to software-properties-common
apt-get install -y apt-transport-https software-properties-common curl
apt-add-repository 'deb https://github.com/mzhaom/lrte/releases/download/v3.0_0 ./'
apt-get update
apt-get install -y --force-yes lrtev3-crosstoolv2-gcc-4.9 lrtev3-crosstoolv2-clang-4.0
