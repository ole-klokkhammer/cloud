# https://github.com/YugaByte/yugabyte-db/releases
# https://gruchalski.com/posts/2021-06-15-yugabytedb-docker-image/
# https://github.com/radekg/yugabyte-db-build-infrastructure/blob/master/.docker/yugabyte-db/Dockerfile

FROM ubuntu:22.04
ARG GID=1060
ARG GROUPNAME=yugabyte
ARG UID=1060
ARG USERNAME=yugabyte

ARG VERSION=2.11.1.0
ARG BUILD=${VERSION}-b305
ARG BUILDPLATFORM
ARG TARGETPLATFORM

RUN echo "I am running on $BUILDPLATFORM, building for $TARGETPLATFORM"

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget python-is-python3 libatomic1 libssl-dev

RUN if [ "$TARGETPLATFORM" = "linux/amd64" ] ; \
    then wget https://downloads.yugabyte.com/releases/${VERSION}/yugabyte-${BUILD}-linux-x86_64.tar.gz -O /yugabyte.tar.gz --no-check-certificate ; \
    else wget https://downloads.yugabyte.com/releases/${VERSION}/yugabyte-${BUILD}-el8-aarch64.tar.gz -O /yugabyte.tar.gz --no-check-certificate ; \
    fi

RUN groupadd -g ${GID} ${GROUPNAME} \
    && useradd -m -d /home/${USERNAME} -g ${GID} -u ${UID} -s /bin/bash ${USERNAME}

RUN mkdir -p /home/${USERNAME} \
    && tar xvfz /yugabyte.tar.gz -C /home/${USERNAME} --strip 1

RUN /home/${USERNAME}/bin/post_install.sh \
    && chown -R ${USERNAME}:${GROUPNAME} /home/${USERNAME} \
    && ln -s /home/${USERNAME}/bin/yb-admin /usr/local/bin/yb-admin \
    && ln -s /home/${USERNAME}/bin/yb-ts-cli /usr/local/bin/yb-ts-cli \
    && ln -s /home/${USERNAME}/bin/ycqlsh /usr/local/bin/ycqlsh \
    && ln -s /home/${USERNAME}/bin/ysqlsh /usr/local/bin/ysqlsh \
    && ln -s /home/${USERNAME}/bin/yugabyted /usr/local/bin/yugabyted \
    && chown -R ${USERNAME}:${GROUPNAME} /usr/local/bin
EXPOSE
USER ${USERNAME}