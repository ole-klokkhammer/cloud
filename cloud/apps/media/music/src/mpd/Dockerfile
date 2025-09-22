
# -------- builder --------
FROM debian:12-slim AS build

ARG MPD_VERSION

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates 

# https://mpd.readthedocs.io/en/latest/user.html
RUN apt-get install -y \
    meson g++ pkgconf \
    libfmt-dev \
    libpcre2-dev \
    libmad0-dev libmpg123-dev libid3tag0-dev \
    libflac-dev libvorbis-dev libopus-dev libogg-dev \
    libadplug-dev libaudiofile-dev libsndfile1-dev libfaad-dev \
    libfluidsynth-dev libgme-dev libmikmod-dev libmodplug-dev \
    libmpcdec-dev libwavpack-dev libwildmidi-dev \
    libsidplay2-dev libsidutils-dev libresid-builder-dev \
    libavcodec-dev libavformat-dev \
    libmp3lame-dev libtwolame-dev libshine-dev \
    libsamplerate0-dev libsoxr-dev \
    libbz2-dev libcdio-paranoia-dev libiso9660-dev libmms-dev \
    libzzip-dev \
    libcurl4-gnutls-dev libexpat1-dev \
    nlohmann-json3-dev \
    libasound2-dev libao-dev libjack-jackd2-dev libopenal-dev \
    libpulse-dev libshout3-dev \
    libsndio-dev \
    libmpdclient-dev \
    libnfs-dev \
    libupnp-dev \
    libavahi-client-dev \
    libsqlite3-dev \
    libsystemd-dev \
    libgtest-dev \
    libicu-dev \
    libchromaprint-dev \
    libgcrypt20-dev \
    libsystemd-dev \
    libpipewire-0.3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    curl -fsSL "https://github.com/MusicPlayerDaemon/MPD/archive/refs/tags/v${MPD_VERSION}.tar.gz" -o mpd.tar.xz; \
    tar -xf mpd.tar.xz; \
    cd "MPD-${MPD_VERSION}"; \
    meson setup build --buildtype=release; \ 
    ninja -C build; \
    ninja -C build install;

FROM debian:12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tini ca-certificates

# bring in binaries and libs
COPY --from=build /usr/local/ /usr/local/
RUN apt-get update && apt-get install -y --no-install-recommends apt-file && apt-file update && \
    missing="$(ldd /usr/local/bin/mpd | awk '/not found/{print $1}')" && \
    for so in $missing; do \
    pkg="$(apt-file search -x "/.*/$so$" | head -n1 | cut -d: -f1)"; \
    [ -n "$pkg" ] && apt-get install -y --no-install-recommends "$pkg"; \
    done && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /var/cache/debconf/*

# refresh the dynamic linker cache so newly added shared libraries are found at runtime.
RUN ldconfig 

RUN mkdir -p /var/lib/mpd \
    /media/music \
    /media/playlists \
    /var/cache/mpd \
    /var/log/mpd

# Default config (override via ConfigMap/volume in k8s)
COPY mpd.conf /etc/mpd.conf

EXPOSE 6600/tcp
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["mpd", "--no-daemon"]