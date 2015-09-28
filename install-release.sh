# This script will install the prebuilt release deb packages hosted by
# github.

# Make sure apt support pulling package using https
apt-get install -y apt-transport-https
apt-add-repository 'deb https://github.com/mzhaom/lrte/releases/download/v2.0_0 ./'
apt-get update
apt-get install lrtev2-crosstoolv2-gcc-4.9 lrtev2-crosstoolv2-clang-3.7
