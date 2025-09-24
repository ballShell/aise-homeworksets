import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ExifTags

def get_exif_date(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal':
                    return value.split(' ')[0].replace(':', '-')
    except Exception as e:
        print(f"Error reading EXIF data for {os.path.basename(image_path)}: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description='为图片批量添加水印。')
    parser.add_argument('--text', type=str, help='自定义水印文本。如果未提供，则尝试读取拍摄日期。')
    parser.add_argument('--font_size', type=int, default=50, help='水印字体大小，默认为 50。')
    parser.add_argument('--color', type=str, default='white', help='水印颜色，默认为 \'white\'。')
    parser.add_argument('--position', type=str, default='bottom_right', 
                        choices=['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'],
                        help='水印位置，默认为右下角 (bottom_right)。')
    args = parser.parse_args()

    image_dir = input("请输入图片所在目录的路径: ")

    if not os.path.isdir(image_dir):
        print(f"错误: \'{image_dir}\' 不是一个有效的目录。")
        return

    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("目录中未找到任何图片文件。")
        return

    for image_file in image_files:
        image_path = os.path.join(image_dir, image_file)
        
        watermark_text = args.text
        if not watermark_text:
            watermark_text = get_exif_date(image_path)
        
        if not watermark_text:
            print(f"无法获取 \'{image_file}\' 的水印文本，已跳过。")
            continue

        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", args.font_size)
        except IOError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x, y = get_position(img.width, img.height, text_width, text_height, args.position)

        draw.text((x, y), watermark_text, fill=args.color, font=font)

        output_dir = os.path.join(image_dir, os.path.basename(image_dir) + "_watermark")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, image_file)
        img.save(output_path)
        print(f"已将带水印的图片保存至: {output_path}")

def get_position(img_width, img_height, text_width, text_height, position):
    margin = 10
    if position == 'top_left':
        return margin, margin
    elif position == 'top_right':
        return img_width - text_width - margin, margin
    elif position == 'bottom_left':
        return margin, img_height - text_height - margin
    elif position == 'bottom_right':
        return img_width - text_width - margin, img_height - text_height - margin
    elif position == 'center':
        return (img_width - text_width) / 2, (img_height - text_height) / 2

if __name__ == '__main__':
    main()