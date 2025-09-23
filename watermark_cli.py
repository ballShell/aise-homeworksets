import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import piexif

def get_shooting_time(image_path):
    try:
        exif_dict = piexif.load(image_path)
        if piexif.ImageIFD.DateTime in exif_dict["0th"]:
            date_time = exif_dict["0th"][piexif.ImageIFD.DateTime].decode("utf-8")
            return date_time.split(" ")[0].replace(":", "-")
    except Exception as e:
        print(f"Error reading EXIF data from {image_path}: {e}")
    return None

def add_watermark(image_path, output_path, text, font_size, font_color, position):
    try:
        image = Image.open(image_path).convert("RGBA")
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(txt_layer)
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x, y = 0, 0
        if "left" in position:
            x = 10
        elif "center" in position:
            x = (image.width - text_width) // 2
        elif "right" in position:
            x = image.width - text_width - 10

        if "top" in position:
            y = 10
        elif "middle" in position:
            y = (image.height - text_height) // 2
        elif "bottom" in position:
            y = image.height - text_height - 10
            
        draw.text((x, y), text, font=font, fill=font_color)
        
        watermarked_image = Image.alpha_composite(image, txt_layer)
        watermarked_image.convert("RGB").save(output_path)
    except Exception as e:
        print(f"Error adding watermark to {image_path}: {e}")

def main():
    # 提示用户输入文件夹路径
    input_dir = input("请输入需要添加水印的图片文件夹路径: ").strip()
    
    # 验证输入的路径是否存在且是文件夹
    if not os.path.isdir(input_dir):
        print(f"错误: 输入的文件夹路径 '{input_dir}' 不存在或不是一个有效的文件夹。")
        return
    
    # 获取其他参数
    font_size = input("请输入水印字体大小 (直接回车默认36): ").strip()
    font_size = int(font_size) if font_size else 36
    
    font_color = input("请输入水印颜色的十六进制代码 (直接回车默认白色#FFFFFF): ").strip()
    font_color = font_color if font_color else "#FFFFFF"
    
    positions = ["top-left", "top-center", "top-right", 
                "middle-left", "middle-center", "middle-right", 
                "bottom-left", "bottom-center", "bottom-right"]
    print("\n可选的水印位置:")
    for i, pos in enumerate(positions, 1):
        print(f"{i}. {pos}")
    
    while True:
        position_input = input("\n请选择水印位置 (输入数字1-9, 直接回车默认bottom-right): ").strip()
        if not position_input:
            position = "bottom-right"
            break
        try:
            idx = int(position_input)
            if 1 <= idx <= 9:
                position = positions[idx-1]
                break
            else:
                print("请输入1-9之间的数字!")
        except ValueError:
            print("请输入有效的数字!")

    # 创建输出目录
    output_dir = f"{os.path.basename(os.path.normpath(input_dir))}_watermark"
    output_path = os.path.join(os.path.dirname(input_dir), output_dir)
    os.makedirs(output_path, exist_ok=True)

    # 处理图片文件
    supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    
    for filename in os.listdir(input_dir):
        if any(filename.lower().endswith(ext) for ext in supported_formats):
            image_path = os.path.join(input_dir, filename)
            shooting_time = get_shooting_time(image_path)
            
            if shooting_time:
                new_filename = f"{os.path.splitext(filename)[0]}_wm{os.path.splitext(filename)[1]}"
                output_file_path = os.path.join(output_path, new_filename)
                add_watermark(image_path, output_file_path, shooting_time, font_size, font_color, position)
                print(f"已为 {filename} 添加水印并保存至 {output_file_path}")

if __name__ == "__main__":
    main()
