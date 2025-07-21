# motion detection
* https://github.com/rajasreevg11/Motion-Detection-and-Tracking-with-python-OpenCV/blob/main/Movement_Detection.py

* https://learnopencv.com/moving-object-detection-with-opencv/


## setup
tensorflowlite needs a specific python version
* /usr/bin/python3.10 -m venv venv
* source venv/bin/activate
* pip install --upgrade pip
* pip install -r requirements.txt
* python app/main.py

## kubernetes
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

## google coral
* https://github.com/google-coral/tflite/blob/master/python/examples/classification/classify_image.py
* https://medium.com/star-gazers/running-tensorflow-lite-at-the-edge-with-raspberry-pi-google-coral-and-docker-83d01357469c
* https://www.diyengineers.com/2024/05/18/setup-coral-tpu-usb-accelerator-on-raspberry-pi-5/
* https://blog.stackademic.com/google-coral-usb-accelerator-on-linux-a3201e7936a8
* https://github.com/google-coral/example-object-tracker?tab=readme-ov-file#contents
* https://coral.ai/examples/
* https://ai.google.dev/edge/litert/migration
* https://ai.google.dev/edge/litert/inference#run-python

## frame differencing
* https://medium.com/@itberrios6/introduction-to-motion-detection-part-1-e031b0bb9bb2

## optical flow
* https://medium.com/@itberrios6/introduction-to-motion-detection-part-2-6ec3d6b385d4

## background substraction
* https://medium.com/@itberrios6/introduction-to-motion-detection-part-3-025271f66ef9
* https://github.com/itberrios/CV_projects/blob/main/motion_detection/detection_with_background_subtraction.ipynb

* ffplay rtsp://127.0.0.1:8554/mystream

## advanced: unsupervised motion detection on moving cameras
* https://python.plainenglish.io/unsupervised-motion-detection-8b523c53c49b

### models
* https://github.com/google-coral/edgetpu/raw/master/test_data
* https://www.coral.ai/models/object-detection/