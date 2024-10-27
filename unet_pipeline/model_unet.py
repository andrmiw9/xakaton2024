import segmentation_models_pytorch as smp
import torch
from torch import nn

def create_unet_with_10_channels():
    ''' 
    Архитектура нейросети.
    '''
    # Загружаем предобученную модель UNet с энкодером resnet34
    model = smp.Unet(
        encoder_name="resnet34",      # энкодер на основе resnet34
        encoder_weights="imagenet",   # используем предобученные веса
        in_channels=3,                # временно указываем 3 канала
        classes=1,
        activation = 'sigmoid'                   
    )
    
    # Модифицируем первый сверточный слой для работы с 10 каналами
    # Получаем текущий первый слой (3 канала)
    original_conv1 = model.encoder.conv1
    
    # Создаем новый слой с 10 каналами и тем же количеством выходов
    new_conv1 = nn.Conv2d(
        in_channels=10,
        out_channels=original_conv1.out_channels,
        kernel_size=original_conv1.kernel_size,
        stride=original_conv1.stride,
        padding=original_conv1.padding,
        bias=original_conv1.bias
    )
    
    # Копируем веса первых трех каналов из старого слоя в новый
    with torch.no_grad():
        new_conv1.weight[:, :3, :, :] = original_conv1.weight
        if new_conv1.weight.size(1) > 3:
            for i in range(3, 10):
                new_conv1.weight[:, i, :, :] = original_conv1.weight[:, i % 3, :, :]
    
    # Заменяем первый слой модели
    model.encoder.conv1 = new_conv1
    return model

def load_unet_model(path_to_state_dict = 'best_model_dice.pth'):
    ''' 
    Загружает модель по пути.
    '''
    m = create_unet_with_10_channels()
    m.load_state_dict(torch.load(path_to_state_dict, weights_only=True))
    return m
    