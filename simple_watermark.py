import os
from PIL import Image, ImageDraw, ImageFont

def get_position(img_width, img_height, text_width, text_height, position):
    """计算水印位置"""
    margin = 20
    if position == 'top_left':
        return margin, margin
    elif position == 'top_center':
        return (img_width - text_width) // 2, margin
    elif position == 'top_right':
        return img_width - text_width - margin, margin
    elif position == 'middle_left':
        return margin, (img_height - text_height) // 2
    elif position == 'center':
        return (img_width - text_width) // 2, (img_height - text_height) // 2
    elif position == 'middle_right':
        return img_width - text_width - margin, (img_height - text_height) // 2
    elif position == 'bottom_left':
        return margin, img_height - text_height - margin
    elif position == 'bottom_center':
        return (img_width - text_width) // 2, img_height - text_height - margin
    elif position == 'bottom_right':
        return img_width - text_width - margin, img_height - text_height - margin
    else:
        # 默认右下角
        return img_width - text_width - margin, img_height - text_height - margin

def apply_text_watermark(image_path, output_path, text, font_size=50, color='white', 
                        position='bottom_right', opacity=255, rotation=0, effects=None):
    """应用文本水印 - 使用图层合成方法"""
    try:
        print(f"开始应用文本水印: {text}")
        
        # 处理effects参数
        if effects is None:
            effects = {'shadow': False, 'outline': False}
        
        # 打开原图
        base_img = Image.open(image_path)
        print(f"原图模式: {base_img.mode}, 尺寸: {base_img.size}")
        
        # 确保原图是RGBA模式
        if base_img.mode != 'RGBA':
            base_img = base_img.convert('RGBA')
        
        # 创建水印图层，与原图同样大小
        watermark_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 加载字体 - 优先使用支持中文的字体
        font = None
        font_paths = [
            # 中文字体优先
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/simsun.ttc",    # 宋体
            "C:/Windows/Fonts/simkai.ttf",    # 楷体
            "C:/Windows/Fonts/simfang.ttf",   # 仿宋
            # 英文字体备选
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            # 相对路径尝试
            "msyh.ttc",
            "simhei.ttf",
            "arial.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                print(f"成功加载字体: {font_path}")
                break
            except (IOError, OSError):
                continue
        
        if font is None:
            # 尝试加载系统默认字体，但指定编码
            try:
                # 在Windows上尝试加载系统默认中文字体
                import platform
                if platform.system() == 'Windows':
                    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
                    print("使用微软雅黑字体")
                else:
                    font = ImageFont.load_default()
                    print("使用默认字体")
            except:
                font = ImageFont.load_default()
                print("使用默认字体")
        
        # 计算文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        print(f"文本尺寸: {text_width} x {text_height}")
        
        # 处理颜色
        if isinstance(color, str):
            if color.startswith('#'):
                # 处理十六进制颜色（优先处理）
                rgb_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            else:
                # 处理颜色名称
                color_map = {
                    'white': (255, 255, 255),
                    'black': (0, 0, 0),
                    'red': (255, 0, 0),
                    'blue': (0, 0, 255),
                    'green': (0, 255, 0),
                    'yellow': (255, 255, 0),
                    'cyan': (0, 255, 255),
                    'magenta': (255, 0, 255)
                }
                rgb_color = color_map.get(color.lower(), (255, 255, 255))
        elif isinstance(color, tuple) and len(color) >= 3:
            rgb_color = color[:3]
        else:
            rgb_color = (255, 255, 255)
        
        # 添加透明度
        text_color = rgb_color + (opacity,)
        print(f"文本颜色: {text_color}")
        
        # 计算位置
        x, y = get_position(base_img.width, base_img.height, text_width, text_height, position)
        print(f"文本位置: ({x}, {y})")
        
        # 处理旋转
        if rotation != 0:
            print(f"应用旋转: {rotation}度")
            # 创建临时图片用于旋转文本
            temp_size = max(text_width, text_height) + 100
            temp_img = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 在临时图片中心绘制文本
            temp_x = (temp_size - text_width) // 2
            temp_y = (temp_size - text_height) // 2
            
            # 绘制阴影和描边效果
            if effects.get('shadow', False):
                # 绘制阴影（偏移2像素，颜色为半透明黑色）
                shadow_color = (0, 0, 0, opacity // 2)
                print(f"应用阴影效果(旋转)，颜色: {shadow_color}")
                temp_draw.text((temp_x + 2, temp_y + 2), text, fill=shadow_color, font=font)
            
            if effects.get('outline', False):
                # 绘制描边效果（在周围8个方向绘制黑色文本）
                outline_color = (0, 0, 0, opacity)
                print(f"应用描边效果(旋转)，颜色: {outline_color}")
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            temp_draw.text((temp_x + dx, temp_y + dy), text, fill=outline_color, font=font)
            
            # 绘制主文本
            temp_draw.text((temp_x, temp_y), text, fill=text_color, font=font)
            
            # 旋转临时图片
            rotated = temp_img.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
            
            # 计算旋转后的位置
            rotated_width, rotated_height = rotated.size
            final_x, final_y = get_position(base_img.width, base_img.height, rotated_width, rotated_height, position)
            
            # 将旋转后的文本粘贴到水印图层
            watermark_layer.paste(rotated, (final_x, final_y), rotated)
        else:
            # 直接在水印图层上绘制文本
            # 绘制阴影和描边效果
            if effects.get('shadow', False):
                # 绘制阴影（偏移2像素，颜色为半透明黑色）
                shadow_color = (0, 0, 0, opacity // 2)
                print(f"应用阴影效果(无旋转)，颜色: {shadow_color}")
                draw.text((x + 2, y + 2), text, fill=shadow_color, font=font)
            
            if effects.get('outline', False):
                # 绘制描边效果（在周围8个方向绘制黑色文本）
                outline_color = (0, 0, 0, opacity)
                print(f"应用描边效果(无旋转)，颜色: {outline_color}")
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, fill=outline_color, font=font)
            
            # 绘制主文本
            draw.text((x, y), text, fill=text_color, font=font)
        
        # 使用alpha_composite合成图层
        print("合成图层...")
        result_img = Image.alpha_composite(base_img, watermark_layer)
        
        # 保存图片
        print(f"保存到: {output_path}")
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            # JPEG不支持透明度，转换为RGB
            rgb_img = Image.new('RGB', result_img.size, (255, 255, 255))
            rgb_img.paste(result_img, mask=result_img.split()[-1])
            rgb_img.save(output_path, 'JPEG', quality=95)
        else:
            # PNG等格式保持透明度
            result_img.save(output_path)
        
        print(f"文本水印已成功应用并保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"应用文本水印时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_image_watermark(image_path, output_path, watermark_path, position='bottom_right', 
                         opacity=255, rotation=0, scale=1.0):
    """应用图片水印 - 使用图层合成方法"""
    try:
        print(f"开始应用图片水印: {watermark_path}")
        
        # 打开主图片
        base_img = Image.open(image_path)
        print(f"主图模式: {base_img.mode}, 尺寸: {base_img.size}")
        
        # 确保主图是RGBA模式
        if base_img.mode != 'RGBA':
            base_img = base_img.convert('RGBA')
        
        # 打开水印图片
        watermark = Image.open(watermark_path)
        print(f"水印图模式: {watermark.mode}, 尺寸: {watermark.size}")
        
        # 确保水印是RGBA模式
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
        
        # 缩放水印
        if scale != 1.0:
            new_width = int(watermark.width * scale)
            new_height = int(watermark.height * scale)
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"缩放后水印尺寸: {watermark.size}")
        
        # 应用透明度
        if opacity < 255:
            print(f"应用透明度: {opacity}/255")
            # 创建透明度蒙版
            alpha = watermark.split()[-1]
            alpha = alpha.point(lambda p: int(p * opacity / 255))
            watermark.putalpha(alpha)
        
        # 处理旋转
        if rotation != 0:
            print(f"应用旋转: {rotation}度")
            watermark = watermark.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
        
        # 创建水印图层
        watermark_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
        
        # 计算位置
        wm_width, wm_height = watermark.size
        x, y = get_position(base_img.width, base_img.height, wm_width, wm_height, position)
        print(f"水印位置: ({x}, {y})")
        
        # 将水印粘贴到水印图层
        watermark_layer.paste(watermark, (x, y), watermark)
        
        # 使用alpha_composite合成图层
        print("合成图层...")
        result_img = Image.alpha_composite(base_img, watermark_layer)
        
        # 保存图片
        print(f"保存到: {output_path}")
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            # JPEG不支持透明度，转换为RGB
            rgb_img = Image.new('RGB', result_img.size, (255, 255, 255))
            rgb_img.paste(result_img, mask=result_img.split()[-1])
            rgb_img.save(output_path, 'JPEG', quality=95)
        else:
            # PNG等格式保持透明度
            result_img.save(output_path)
        
        print(f"图片水印已成功应用并保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"应用图片水印时出错: {e}")
        import traceback
        traceback.print_exc()
        return False