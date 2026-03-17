from PIL import Image, ImageDraw
import math

def create_trumpet_icon(size, background_color=(0, 0, 0, 0)):
    """
    创建一个指定大小的喇叭形状图标。
    :param size: 图标大小（宽度和高度）
    :param background_color: 背景颜色，默认为透明
    :return: PIL Image对象
    """
    # 创建新图像，带有透明背景
    img = Image.new('RGBA', (size, size), background_color)
    draw = ImageDraw.Draw(img)
    
    # 计算喇叭形状的参数
    center = size // 2
    # 喇叭的开口大小（椭圆的长半轴和短半轴）
    ellipse_width = size // 2
    ellipse_height = size // 3
    # 喇叭的管长
    tube_length = size // 4
    # 喇叭的颜色：金黄色
    trumpet_color = (255, 215, 0, 255)  # 金黄色，不透明
    
    # 绘制喇叭的开口（椭圆部分）
    # 椭圆位于图像的右侧
    left = center + tube_length
    top = center - ellipse_height
    right = size - 1
    bottom = center + ellipse_height
    draw.ellipse([left, top, right, bottom], fill=trumpet_color)
    
    # 绘制喇叭的管子（梯形或矩形，逐渐变细）
    # 使用多边形来绘制梯形
    # 梯形的四个点：左侧中心点，左侧上下两点，连接到椭圆
    tube_left = center - tube_length // 2
    tube_top = center - ellipse_height // 2
    tube_bottom = center + ellipse_height // 2
    # 连接到椭圆的点（椭圆左侧中间点）
    ellipse_left = left
    ellipse_center_top = center - ellipse_height // 4
    ellipse_center_bottom = center + ellipse_height // 4
    
    # 绘制梯形（管子）
    draw.polygon([
        (tube_left, tube_top),
        (tube_left, tube_bottom),
        (ellipse_left, ellipse_center_bottom),
        (ellipse_left, ellipse_center_top)
    ], fill=trumpet_color)
    
    # 可选：绘制喇叭的嘴（一个小圆圈或椭圆，表示吹口）
    mouth_size = size // 8
    mouth_left = tube_left - mouth_size
    mouth_top = center - mouth_size // 2
    mouth_right = tube_left
    mouth_bottom = center + mouth_size // 2
    draw.ellipse([mouth_left, mouth_top, mouth_right, mouth_bottom], fill=trumpet_color)
    
    return img

def generate_ico_file():
    """
    生成包含多个分辨率的ICO文件。
    """
    # 定义需要生成的分辨率
    sizes = [16, 24, 32, 48, 64, 128, 256]
    
    # 为每个分辨率创建图像
    images = []
    for size in sizes:
        img = create_trumpet_icon(size)
        images.append(img)
    
    # 保存为ICO文件
    # 注意：Pillow库在保存ICO时，会自动处理多个图像作为多个分辨率
    images[0].save('app_icon.ico', format='ICO', sizes=[(size, size) for size in sizes], append_images=images[1:])

if __name__ == "__main__":
    generate_ico_file()
    print("ICO文件已生成：app_icon.ico")