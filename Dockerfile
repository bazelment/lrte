FROM ubuntu:16.04

ADD ./install-*.sh /tmp/

RUN /tmp/install-release.sh
RUN /tmp/install-bazel.sh
