from ultralytics import YOLO;

#model = YOLO("yolo26x.pt");
#print("downloaded")


from ultralytics import RTDETR

# Load a COCO-pretrained RT-DETR-l model
model = RTDETR("rtdetr-x.pt")

model.export(format="onnx", quantize=16)
