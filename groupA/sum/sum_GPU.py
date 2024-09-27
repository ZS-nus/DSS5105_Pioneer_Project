import torch

print(torch.cuda.is_available())  # 确认是否检测到GPU
print(torch.cuda.current_device())  # 当前使用的GPU设备
print(torch.cuda.get_device_name(torch.cuda.current_device()))  # 打印GPU名称
