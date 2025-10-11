# 水印文件本地应用实现计划书

## 项目概述

本项目旨在开发一个功能完善的本地水印应用程序，允许用户为图片添加文本或图片水印，并提供丰富的自定义选项。应用程序将提供直观的图形用户界面，支持批量处理，并具有实时预览功能。

## 技术栈选择

- **编程语言**: Python 3.x
- **GUI框架**: PyQt5/PySide6 (提供现代化、跨平台的用户界面)
- **图像处理**: Pillow (PIL Fork，用于图像操作)
- **文件管理**: Python 标准库 (os, shutil)

## 功能模块设计

### 1. 文件处理模块

#### 1.1 导入图片
- **单张导入**: 实现文件选择器和拖放功能，支持单张图片导入
- **批量导入**: 支持多选文件和整个文件夹导入
- **预览列表**: 使用QListWidget显示缩略图和文件名
- **实现方式**: 
  ```python
  def import_images(self):
      # 使用QFileDialog实现文件选择
      # 支持多选和文件夹选择
      # 处理拖放事件
  ```

#### 1.2 支持格式
- **输入格式**: JPEG, PNG, BMP, TIFF (包括透明通道支持)
- **输出格式**: 用户可选JPEG或PNG
- **实现方式**:
  ```python
  # 使用Pillow库的Image模块处理不同格式
  # 检测和保留透明通道
  ```

#### 1.3 导出图片
- **输出目录**: 用户指定，默认禁止覆盖原目录
- **命名规则**: 实现三种命名选项（原名、前缀、后缀）
- **质量控制**: 对JPEG提供0-100质量滑块
- **尺寸调整**: 提供按宽度、高度或百分比缩放选项
- **实现方式**:
  ```python
  def export_images(self):
      # 获取用户设置的输出参数
      # 批量处理图片并保存
  ```

### 2. 水印类型模块

#### 2.1 文本水印
- **内容编辑**: 文本输入框，支持多行文本
- **字体设置**: 系统字体选择器，字号、粗体、斜体选项
- **颜色选择**: 使用QColorDialog提供调色板
- **透明度控制**: 0-100%滑块控制
- **特效选项**: 阴影和描边效果
- **实现方式**:
  ```python
  def apply_text_watermark(self, image, text, font, color, opacity, effects):
      # 使用Pillow的ImageDraw模块绘制文本
      # 应用透明度和特效
  ```

#### 2.2 图片水印
- **图片选择**: 文件选择器导入Logo等图片
- **透明支持**: 处理带Alpha通道的PNG
- **缩放控制**: 提供比例和自由缩放选项
- **透明度控制**: 0-100%滑块控制
- **实现方式**:
  ```python
  def apply_image_watermark(self, base_image, watermark_image, scale, opacity):
      # 调整水印图片大小
      # 处理透明度
      # 合成图片
  ```

### 3. 水印布局与样式模块

#### 3.1 实时预览
- **主预览窗口**: 显示当前选中图片的水印效果
- **切换预览**: 点击列表切换不同图片的预览
- **实现方式**:
  ```python
  def update_preview(self):
      # 应用当前水印设置到预览图
      # 实时更新显示
  ```

#### 3.2 位置控制
- **预设位置**: 九宫格布局按钮（四角、中心等）
- **手动拖拽**: 在预览窗口中实现鼠标拖拽定位
- **实现方式**:
  ```python
  def set_watermark_position(self, position_type, x=None, y=None):
      # 处理预设位置或自定义坐标
  ```

#### 3.3 旋转控制
- **角度调节**: 提供0-360度的滑块和输入框
- **实现方式**:
  ```python
  def rotate_watermark(self, angle):
      # 使用Pillow的旋转功能
  ```

### 4. 配置管理模块

#### 4.1 水印模板
- **保存模板**: 将当前所有设置保存为JSON格式
- **加载模板**: 从保存的模板中恢复设置
- **默认设置**: 程序启动时加载上次设置或默认模板
- **实现方式**:
  ```python
  def save_template(self, name):
      # 将当前设置序列化为JSON
      
  def load_template(self, name):
      # 从JSON加载设置并应用
  ```

## 用户界面设计

### 主界面布局
- **左侧**: 图片列表面板（缩略图+文件名）
- **中央**: 主预览区域
- **右侧**: 水印设置面板（选项卡式布局）
- **底部**: 状态栏和操作按钮

### 设置面板选项卡
1. **文件操作**: 导入/导出选项
2. **文本水印**: 文本、字体、颜色等设置
3. **图片水印**: 图片选择、缩放等设置
4. **布局样式**: 位置、旋转等设置
5. **模板管理**: 保存/加载模板

## 实现计划

### 阶段一：基础框架搭建
1. 创建主窗口和基本UI布局
2. 实现图片导入和预览功能
3. 设计数据结构存储图片和水印设置

### 阶段二：核心功能实现
1. 实现文本水印功能
2. 实现水印位置控制
3. 实现图片导出功能

### 阶段三：高级功能实现
1. 实现图片水印功能
2. 添加特效和旋转功能
3. 实现模板管理系统

### 阶段四：优化和测试
1. 性能优化（特别是大图片和批量处理）
2. 用户界面优化和美化
3. 多格式兼容性测试

## 代码结构设计

所有功能将在单个`main.py`文件中实现，主要类结构如下：

```python
# main.py

import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                            QListWidget, QColorDialog, QSlider, ...)
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QSize
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = []  # 存储导入的图片
        self.current_image_index = -1
        self.watermark_settings = {}  # 存储水印设置
        self.init_ui()
        
    def init_ui(self):
        # 创建主窗口和布局
        # 设置菜单栏、工具栏等
        
    def setup_image_list(self):
        # 创建图片列表面板
        
    def setup_preview_area(self):
        # 创建预览区域
        
    def setup_settings_panel(self):
        # 创建设置面板和选项卡
        
    # 文件处理方法
    def import_images(self):
        # 导入图片实现
        
    def export_images(self):
        # 导出图片实现
        
    # 水印处理方法
    def apply_text_watermark(self, image, text, font, color, opacity, effects):
        # 文本水印实现
        
    def apply_image_watermark(self, base_image, watermark_image, scale, opacity):
        # 图片水印实现
        
    # 布局控制方法
    def set_watermark_position(self, position_type, x=None, y=None):
        # 位置控制实现
        
    def rotate_watermark(self, angle):
        # 旋转控制实现
        
    # 配置管理方法
    def save_template(self, name):
        # 保存模板实现
        
    def load_template(self, name):
        # 加载模板实现
        
    # 辅助方法
    def update_preview(self):
        # 更新预览图
        
    def get_current_settings(self):
        # 获取当前所有设置
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_())
```

## 开发时间线

1. **基础框架搭建**: 3天
2. **核心功能实现**: 5天
3. **高级功能实现**: 4天
4. **优化和测试**: 3天

总计开发时间：约2周

## 可能的挑战和解决方案

1. **大图片处理性能**
   - 解决方案：预览时使用缩小的图片，导出时再处理原图

2. **多格式兼容性**
   - 解决方案：充分利用Pillow库的格式转换功能，对特殊格式进行专门处理

3. **复杂背景下水印可见性**
   - 解决方案：实现描边和阴影效果，增强水印在各种背景下的可读性

## 结论

本实现计划书详细描述了水印文件本地应用的开发方案，包括功能模块设计、用户界面设计、代码结构和开发时间线。通过PyQt5和Pillow的结合，可以实现一个功能完善、用户友好的水印应用程序，满足需求文档中的所有要求。
