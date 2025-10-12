FROM alexxit/go2rtc:master-hardware

RUN apt update && apt install -y \
  gettext \
  wget \
  unzip \
  libgstrtspserver-1.0-0 \
  libgstreamer1.0-0 \
  libgstreamer-plugins-bad1.0-0 \
  gstreamer1.0-x \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  libssl-dev && \
  rm -rf /var/lib/apt/lists/*

# Install dependencies for neolink
RUN mkdir -p /config/neolink 
RUN wget https://github.com/QuantumEntangledAndy/neolink/releases/download/v0.6.3.rc.2/neolink_linux_x86_64_ubuntu.zip && \
  unzip neolink_linux_x86_64_ubuntu.zip && \
  mv neolink_linux_x86_64_ubuntu/* /config/neolink/ && \
  chmod +x /config/neolink/neolink && \
  rm -rf neolink_linux_x86_64_ubuntu.zip neolink_linux_x86_64_ubuntu

# setup neolink scripts
COPY ./config/neolink/* /config/neolink/  
RUN chmod +x /config/neolink/neolink_talk.sh   
RUN chmod +x /config/neolink/neolink_talk_test.sh
RUN chmod +x /config/neolink/neolink_talk_rtsp.sh

# setup go2rtc stuff
COPY ./config/go2rtc/* /config/go2rtc/

# log files
RUN touch /tmp/neolink_talk.log
RUN chmod 777 /tmp/neolink_talk.log

# make so that we can use environment variables in configs
COPY ./config/entrypoint.sh /config/entrypoint.sh
RUN chmod +x /config/entrypoint.sh

ENTRYPOINT [ "/config/entrypoint.sh" ]
CMD [ "go2rtc", "-c", "/config/go2rtc/go2rtc.yaml" ]