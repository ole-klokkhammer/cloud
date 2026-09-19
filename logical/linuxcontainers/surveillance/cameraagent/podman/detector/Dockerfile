FROM registry.linole.org/py312:cu13

COPY app/requirements.txt /app/requirements.txt

# torch is already in the base; this installs only the app-side packages
# (ultralytics, opencv, nats-py, ...). requirements.txt may keep a
# `torch>=X` line — pip no-ops it when the base already satisfies it.
#
# ultralytics pulls in the GUI flavor (opencv-python), whose cv2 .so
# links libxcb - which we don't have (headless base, no X11). Both
# flavors unpack into the same site-packages/cv2/, so last-installed
# wins. Purge both flavors after the batch install, then install
# opencv-python-headless on its own so it lands last and stays.
RUN pip install --no-cache-dir --break-system-packages -r /app/requirements.txt \
    && pip uninstall -y opencv-python opencv-python-headless \
    && pip install --no-cache-dir --break-system-packages opencv-python-headless

COPY app/detector.py /app/detector.py

WORKDIR /app

ENTRYPOINT ["python"]

CMD ["/app/detector.py"]
