import onnx

# elem_type: 1 = FP32, 10 = FP16 (the triton config's data_type must
# match the ONNX's boundary dtype - quantize=16 keeps it FP32, but
# always check after changing the export)
m=onnx.load('rtdetr-x.onnx')
[print(n.name,
       [d.dim_value if d.HasField("dim_value") else d.dim_param for d in n.type.tensor_type.shape.dim],
       "elem_type", n.type.tensor_type.elem_type)
   for n in list(m.graph.input)+list(m.graph.output)]
