import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QListWidget, QListWidgetItem,
                            QLabel, QPushButton, QSlider, QComboBox, QLineEdit, QColorDialog,
                            QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QTabWidget,
                            QGroupBox, QRadioButton, QCheckBox, QSpinBox, QMessageBox)
from PySide6.QtGui import QImage, QPixmap, QFont, QColor, QDrag, QIcon
from PySide6.QtCore import Qt, QSize, QPoint, QMimeData
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageColor

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = []  # 存储导入的图片路径
        self.current_image_index = -1
        self.watermark_settings = {
            'type': 'text',  # 'text' 或 'image'
            'text': '水印文本',
            'font': 'Arial',
            'font_size': 25,
            'color': 'white',
            'opacity': 70,  # 0-100
            'position': 'bottom_right',
            'custom_position': (0, 0),
            'rotation': 0,
            'effects': {
                'shadow': False,
                'outline': False
            },
            'image_path': '',
            'image_scale': 100  # 百分比
        }
        # 初始化导出设置
        self.export_settings = {
            'save_path': '',
            'quality': 95,
            'naming_rule': 'prefix',  # 'original', 'prefix', 'suffix'
            'prefix': 'wm_',
            'suffix': '_watermarked'
        }
        self.init_ui()
        
    def init_ui(self):
        # 设置主窗口
        self.setWindowTitle('水印文件本地应用')
        self.setGeometry(100, 100, 1600, 1000)  # 进一步增大窗口尺寸
        
        # 创建主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # 创建左侧图片列表面板
        self.setup_image_list_panel()
        
        # 创建中央预览区域
        self.setup_preview_area()
        
        # 创建右侧设置面板
        self.setup_settings_panel()
        
        # 添加三个主面板到主布局 - 调整比例以给预览区域更多空间
        main_layout.addWidget(self.image_list_panel, 1)    # 图片列表面板
        main_layout.addWidget(self.preview_panel, 5)       # 预览面板 - 进一步增加比例
        main_layout.addWidget(self.settings_panel, 2)      # 设置面板
        
        # 设置主布局
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 创建状态栏
        self.statusBar().showMessage('就绪')
        
    def setup_image_list_panel(self):
        # 创建图片列表面板
        self.image_list_panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('图片列表')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 12, QFont.Bold))
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.itemClicked.connect(self.on_image_selected)
        
        # 导入按钮
        import_btn_layout = QHBoxLayout()
        self.import_file_btn = QPushButton('导入图片')
        self.import_folder_btn = QPushButton('导入文件夹')
        self.import_file_btn.clicked.connect(self.import_files)
        self.import_folder_btn.clicked.connect(self.import_folder)
        import_btn_layout.addWidget(self.import_file_btn)
        import_btn_layout.addWidget(self.import_folder_btn)
        
        # 添加到布局
        layout.addWidget(title)
        layout.addWidget(self.image_list)
        layout.addLayout(import_btn_layout)
        
        self.image_list_panel.setLayout(layout)
        
    def setup_preview_area(self):
        # 创建预览区域
        self.preview_panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('预览')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 12, QFont.Bold))
        
        # 预览图像 - 增大最小尺寸并设置为可调整大小
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(800, 600)  # 进一步增大最小预览尺寸
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        self.preview_label.setText("导入图片后在此处显示预览")
        self.preview_label.setScaledContents(False)  # 确保保持长宽比
        
        # 添加到布局
        layout.addWidget(title)
        layout.addWidget(self.preview_label, 1)  # 设置拉伸因子为1，使预览区域可以扩展
        
        self.preview_panel.setLayout(layout)
        
    def setup_settings_panel(self):
        # 创建设置面板
        self.settings_panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('水印设置')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 12, QFont.Bold))
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 文本水印选项卡
        self.text_tab = self.create_text_watermark_tab()
        
        # 图片水印选项卡
        self.image_tab = self.create_image_watermark_tab()
        
        # 布局选项卡
        self.layout_tab = self.create_layout_tab()
        
        # 导出选项卡
        self.export_tab = self.create_export_tab()
        
        # 模板选项卡
        self.template_tab = self.create_template_tab()
        
        # 添加选项卡
        self.tabs.addTab(self.text_tab, "文本水印")
        self.tabs.addTab(self.image_tab, "图片水印")
        self.tabs.addTab(self.layout_tab, "布局样式")
        self.tabs.addTab(self.export_tab, "导出设置")
        self.tabs.addTab(self.template_tab, "模板管理")
        
        # 应用按钮
        self.apply_btn = QPushButton('应用水印')
        self.apply_btn.clicked.connect(self.apply_watermark)
        
        # 添加到布局
        layout.addWidget(title)
        layout.addWidget(self.tabs)
        layout.addWidget(self.apply_btn)
        
        self.settings_panel.setLayout(layout)
        
    def create_text_watermark_tab(self):
        # 创建文本水印选项卡
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 文本输入
        text_group = QGroupBox("水印文本")
        text_layout = QVBoxLayout()
        self.text_input = QLineEdit(self.watermark_settings['text'])
        self.text_input.textChanged.connect(self.update_text_watermark)
        text_layout.addWidget(self.text_input)
        text_group.setLayout(text_layout)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QGridLayout()
        
        font_layout.addWidget(QLabel("字体:"), 0, 0)
        self.font_combo = QComboBox()
        # 添加系统字体
        self.font_combo.addItems(["Arial", "Times New Roman", "Courier New", "SimSun", "SimHei", "Microsoft YaHei"])
        self.font_combo.currentTextChanged.connect(self.update_font)
        font_layout.addWidget(self.font_combo, 0, 1)
        
        font_layout.addWidget(QLabel("字号:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 200)
        self.font_size_spin.setValue(self.watermark_settings['font_size'])
        self.font_size_spin.valueChanged.connect(self.update_font_size)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        font_group.setLayout(font_layout)
        
        # 颜色设置
        color_group = QGroupBox("颜色设置")
        color_layout = QGridLayout()
        
        color_layout.addWidget(QLabel("颜色:"), 0, 0)
        self.color_btn = QPushButton()
        self.color_btn.setStyleSheet(f"background-color: {self.watermark_settings['color']};")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn, 0, 1)
        
        color_layout.addWidget(QLabel("透明度:"), 1, 0)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.watermark_settings['opacity'])
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        color_layout.addWidget(self.opacity_slider, 1, 1)
        
        color_group.setLayout(color_layout)
        
        # 特效设置
        effects_group = QGroupBox("特效设置")
        effects_layout = QVBoxLayout()
        
        self.shadow_check = QCheckBox("阴影效果")
        self.shadow_check.setChecked(self.watermark_settings['effects']['shadow'])
        self.shadow_check.stateChanged.connect(self.update_shadow_effect)
        
        self.outline_check = QCheckBox("描边效果")
        self.outline_check.setChecked(self.watermark_settings['effects']['outline'])
        self.outline_check.stateChanged.connect(self.update_outline_effect)
        
        effects_layout.addWidget(self.shadow_check)
        effects_layout.addWidget(self.outline_check)
        effects_group.setLayout(effects_layout)
        
        # 添加到布局
        layout.addWidget(text_group)
        layout.addWidget(font_group)
        layout.addWidget(color_group)
        layout.addWidget(effects_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_image_watermark_tab(self):
        # 创建图片水印选项卡
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 图片选择
        image_group = QGroupBox("水印图片")
        image_layout = QVBoxLayout()
        
        self.image_path_label = QLabel("未选择图片")
        self.select_image_btn = QPushButton("选择图片")
        self.select_image_btn.clicked.connect(self.select_watermark_image)
        
        image_layout.addWidget(self.image_path_label)
        image_layout.addWidget(self.select_image_btn)
        image_group.setLayout(image_layout)
        
        # 缩放设置
        scale_group = QGroupBox("缩放设置")
        scale_layout = QVBoxLayout()
        
        scale_layout.addWidget(QLabel("缩放比例:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 200)
        self.scale_slider.setValue(self.watermark_settings['image_scale'])
        self.scale_slider.valueChanged.connect(self.update_image_scale)
        scale_layout.addWidget(self.scale_slider)
        
        scale_group.setLayout(scale_layout)
        
        # 透明度设置
        opacity_group = QGroupBox("透明度设置")
        opacity_layout = QVBoxLayout()
        
        opacity_layout.addWidget(QLabel("透明度:"))
        self.image_opacity_slider = QSlider(Qt.Horizontal)
        self.image_opacity_slider.setRange(0, 100)
        self.image_opacity_slider.setValue(self.watermark_settings['opacity'])
        self.image_opacity_slider.valueChanged.connect(self.update_opacity)
        opacity_layout.addWidget(self.image_opacity_slider)
        
        opacity_group.setLayout(opacity_layout)
        
        # 添加到布局
        layout.addWidget(image_group)
        layout.addWidget(scale_group)
        layout.addWidget(opacity_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_layout_tab(self):
        # 创建布局选项卡
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 位置设置
        position_group = QGroupBox("位置设置")
        position_layout = QGridLayout()
        
        # 九宫格位置选择
        self.position_buttons = {}
        positions = [
            ('top_left', 0, 0), ('top_center', 0, 1), ('top_right', 0, 2),
            ('middle_left', 1, 0), ('center', 1, 1), ('middle_right', 1, 2),
            ('bottom_left', 2, 0), ('bottom_center', 2, 1), ('bottom_right', 2, 2)
        ]
        
        for pos_name, row, col in positions:
            btn = QPushButton()
            btn.setFixedSize(50, 50)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, p=pos_name: self.set_position(p))
            position_layout.addWidget(btn, row, col)
            self.position_buttons[pos_name] = btn
            
        # 设置默认选中
        if self.watermark_settings['position'] in self.position_buttons:
            self.position_buttons[self.watermark_settings['position']].setChecked(True)
        
        position_group.setLayout(position_layout)
        
        # 旋转设置
        rotation_group = QGroupBox("旋转设置")
        rotation_layout = QVBoxLayout()
        
        rotation_layout.addWidget(QLabel("旋转角度:"))
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(0, 360)
        self.rotation_slider.setValue(self.watermark_settings['rotation'])
        self.rotation_slider.valueChanged.connect(self.update_rotation)
        rotation_layout.addWidget(self.rotation_slider)
        
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 360)
        self.rotation_spin.setValue(self.watermark_settings['rotation'])
        self.rotation_spin.valueChanged.connect(self.rotation_slider.setValue)
        rotation_layout.addWidget(self.rotation_spin)
        
        # 连接旋转滑块和数值框
        self.rotation_slider.valueChanged.connect(self.rotation_spin.setValue)
        
        rotation_group.setLayout(rotation_layout)
        
        # 添加到布局
        layout.addWidget(position_group)
        layout.addWidget(rotation_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_export_tab(self):
        # 创建导出选项卡
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 输出目录
        output_group = QGroupBox("输出目录")
        output_layout = QVBoxLayout()
        
        # 默认保存路径选项
        default_path_layout = QHBoxLayout()
        self.output_path_label = QLabel("未选择输出目录")
        self.select_output_btn = QPushButton("选择目录")
        self.select_output_btn.clicked.connect(self.select_output_directory)
        
        default_path_layout.addWidget(self.output_path_label)
        default_path_layout.addWidget(self.select_output_btn)
        
        # 设为默认保存路径选项
        default_option_layout = QHBoxLayout()
        self.set_default_path_check = QCheckBox("设为默认保存路径")
        self.set_default_path_check.setChecked(True)
        default_option_layout.addWidget(self.set_default_path_check)
        
        output_layout.addLayout(default_path_layout)
        output_layout.addLayout(default_option_layout)
        output_group.setLayout(output_layout)
        
        # 命名规则
        naming_group = QGroupBox("命名规则")
        naming_layout = QVBoxLayout()
        
        self.naming_original = QRadioButton("保留原文件名")
        self.naming_prefix = QRadioButton("添加前缀")
        self.naming_suffix = QRadioButton("添加后缀")
        
        self.naming_original.setChecked(True)
        
        self.prefix_input = QLineEdit("wm_")
        self.suffix_input = QLineEdit("_watermarked")
        
        naming_layout.addWidget(self.naming_original)
        
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(self.naming_prefix)
        prefix_layout.addWidget(self.prefix_input)
        naming_layout.addLayout(prefix_layout)
        
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(self.naming_suffix)
        suffix_layout.addWidget(self.suffix_input)
        naming_layout.addLayout(suffix_layout)
        
        naming_group.setLayout(naming_layout)
        
        # 输出格式
        format_group = QGroupBox("输出格式")
        format_layout = QVBoxLayout()
        
        self.format_jpeg = QRadioButton("JPEG")
        self.format_png = QRadioButton("PNG")
        
        self.format_jpeg.setChecked(True)
        
        format_layout.addWidget(self.format_jpeg)
        format_layout.addWidget(self.format_png)
        
        # JPEG质量设置
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("JPEG质量:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(85)
        quality_layout.addWidget(self.quality_slider)
        format_layout.addLayout(quality_layout)
        
        format_group.setLayout(format_layout)
        
        # 导出按钮
        self.export_btn = QPushButton("导出图片")
        self.export_btn.clicked.connect(self.export_images)
        
        # 添加到布局
        layout.addWidget(output_group)
        layout.addWidget(naming_group)
        layout.addWidget(format_group)
        layout.addWidget(self.export_btn)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_template_tab(self):
        # 创建模板选项卡
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 保存模板
        save_group = QGroupBox("保存模板")
        save_layout = QHBoxLayout()
        
        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText("输入模板名称")
        self.save_template_btn = QPushButton("保存")
        self.save_template_btn.clicked.connect(self.save_template)
        
        save_layout.addWidget(self.template_name_input)
        save_layout.addWidget(self.save_template_btn)
        save_group.setLayout(save_layout)
        
        # 模板列表
        templates_group = QGroupBox("模板列表")
        templates_layout = QVBoxLayout()
        
        self.templates_list = QListWidget()
        self.templates_list.itemClicked.connect(self.on_template_selected)
        
        templates_btn_layout = QHBoxLayout()
        self.load_template_btn = QPushButton("加载")
        self.delete_template_btn = QPushButton("删除")
        self.load_template_btn.clicked.connect(self.load_template)
        self.delete_template_btn.clicked.connect(self.delete_template)
        templates_btn_layout.addWidget(self.load_template_btn)
        templates_btn_layout.addWidget(self.delete_template_btn)
        
        templates_layout.addWidget(self.templates_list)
        templates_layout.addLayout(templates_btn_layout)
        templates_group.setLayout(templates_layout)
        
        # 添加到布局
        layout.addWidget(save_group)
        layout.addWidget(templates_group)
        layout.addStretch()
        
        # 加载已保存的模板
        self.load_saved_templates()
        
        tab.setLayout(layout)
        return tab
    
    # 图片导入方法
    def import_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if file_paths:
            self.add_images(file_paths)
    
    def import_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            file_paths = []
            for file in os.listdir(folder_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    file_paths.append(os.path.join(folder_path, file))
            if file_paths:
                self.add_images(file_paths)
            else:
                QMessageBox.information(self, "提示", "所选文件夹中没有支持的图片文件")
    
    def add_images(self, file_paths):
        for path in file_paths:
            if path not in self.images:
                self.images.append(path)
                filename = os.path.basename(path)
                
                # 创建缩略图
                try:
                    img = Image.open(path)
                    img.thumbnail((80, 80))
                    img = img.convert("RGBA")
                    data = img.tobytes("raw", "RGBA")
                    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
                    pixmap = QPixmap.fromImage(qimg)
                    
                    # 添加到列表
                    item = QListWidgetItem(QIcon(pixmap), filename)
                    item.setData(Qt.UserRole, path)
                    self.image_list.addItem(item)
                except Exception as e:
                    print(f"Error creating thumbnail for {path}: {e}")
        
        # 如果这是第一张图片，选中它
        if self.current_image_index == -1 and self.images:
            self.image_list.setCurrentRow(0)
            self.on_image_selected(self.image_list.item(0))
    
    def on_image_selected(self, item):
        path = item.data(Qt.UserRole)
        self.current_image_index = self.images.index(path)
        self.update_preview()
    
    # 水印设置方法
    def update_text_watermark(self):
        self.watermark_settings['text'] = self.text_input.text()
        self.update_preview()
    
    def update_font(self, font_name):
        self.watermark_settings['font'] = font_name
        self.update_preview()
    
    def update_font_size(self, size):
        self.watermark_settings['font_size'] = size
        self.update_preview()
    
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.watermark_settings['color']), self)
        if color.isValid():
            self.watermark_settings['color'] = color.name()
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.update_preview()
    
    def update_opacity(self, value):
        self.watermark_settings['opacity'] = value
        self.update_preview()
    
    def update_shadow_effect(self, state):
        self.watermark_settings['effects']['shadow'] = state == Qt.Checked
        print(f"阴影效果设置: {self.watermark_settings['effects']['shadow']}")
        self.update_preview()
    
    def update_outline_effect(self, state):
        self.watermark_settings['effects']['outline'] = state == Qt.Checked
        print(f"描边效果设置: {self.watermark_settings['effects']['outline']}")
        self.update_preview()
    
    def select_watermark_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择水印图片", "", "图片文件 (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.watermark_settings['image_path'] = file_path
            self.image_path_label.setText(os.path.basename(file_path))
            self.update_preview()
    
    def update_image_scale(self, value):
        self.watermark_settings['image_scale'] = value
        self.update_preview()
    
    def set_position(self, position):
        self.watermark_settings['position'] = position
        # 取消其他按钮的选中状态
        for pos, btn in self.position_buttons.items():
            if pos != position:
                btn.setChecked(False)
        self.update_preview()
    
    def update_rotation(self, value):
        self.watermark_settings['rotation'] = value
        self.update_preview()
    
    # 导出方法
    def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            # 检查是否与原目录相同
            if self.images and os.path.dirname(self.images[0]) == dir_path:
                reply = QMessageBox.warning(
                    self, "警告", 
                    "输出目录与原图片目录相同，可能会覆盖原文件。是否继续？",
                    QMessageBox.Yes | QMessageBox.No, 
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            self.output_path_label.setText(dir_path)
            
            # 如果勾选了"设为默认保存路径"，则保存设置
            if hasattr(self, 'set_default_path_check') and self.set_default_path_check.isChecked():
                # 保存默认输出路径到配置
                config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
                os.makedirs(config_dir, exist_ok=True)
                with open(os.path.join(config_dir, "settings.json"), 'w', encoding='utf-8') as f:
                    json.dump({"default_output_path": dir_path}, f, ensure_ascii=False, indent=4)
    
    # 模板管理方法
    def save_template(self):
        name = self.template_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入模板名称")
            return
        
        # 保存当前设置
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        template_path = os.path.join(templates_dir, f"{name}.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(self.watermark_settings, f, ensure_ascii=False, indent=4)
        
        # 更新模板列表
        self.load_saved_templates()
        QMessageBox.information(self, "成功", f"模板 '{name}' 已保存")
    
    def load_saved_templates(self):
        self.templates_list.clear()
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        if os.path.exists(templates_dir):
            for file in os.listdir(templates_dir):
                if file.endswith('.json'):
                    template_name = os.path.splitext(file)[0]
                    self.templates_list.addItem(template_name)
    
    def on_template_selected(self, item):
        # 仅选中，不加载
        pass
    
    def load_template(self):
        selected_items = self.templates_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择一个模板")
            return
        
        template_name = selected_items[0].text()
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        template_path = os.path.join(templates_dir, f"{template_name}.json")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.watermark_settings.update(settings)
                self.update_ui_from_settings()
                self.update_preview()
                QMessageBox.information(self, "成功", f"模板 '{template_name}' 已加载")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载模板失败: {str(e)}")
    
    def delete_template(self):
        selected_items = self.templates_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择一个模板")
            return
        
        template_name = selected_items[0].text()
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模板 '{template_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
            template_path = os.path.join(templates_dir, f"{template_name}.json")
            try:
                os.remove(template_path)
                self.load_saved_templates()
                QMessageBox.information(self, "成功", f"模板 '{template_name}' 已删除")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除模板失败: {str(e)}")
    
    def update_ui_from_settings(self):
        # 更新UI控件以匹配当前设置
        # 文本水印
        self.text_input.setText(self.watermark_settings['text'])
        
        index = self.font_combo.findText(self.watermark_settings['font'])
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
        
        self.font_size_spin.setValue(self.watermark_settings['font_size'])
        self.color_btn.setStyleSheet(f"background-color: {self.watermark_settings['color']};")
        self.opacity_slider.setValue(self.watermark_settings['opacity'])
        self.image_opacity_slider.setValue(self.watermark_settings['opacity'])
        
        self.shadow_check.setChecked(self.watermark_settings['effects']['shadow'])
        self.outline_check.setChecked(self.watermark_settings['effects']['outline'])
        
        # 图片水印
        if self.watermark_settings['image_path']:
            self.image_path_label.setText(os.path.basename(self.watermark_settings['image_path']))
        else:
            self.image_path_label.setText("未选择图片")
        
        self.scale_slider.setValue(self.watermark_settings['image_scale'])
        
        # 布局
        for pos, btn in self.position_buttons.items():
            btn.setChecked(pos == self.watermark_settings['position'])
        
        self.rotation_slider.setValue(self.watermark_settings['rotation'])
        self.rotation_spin.setValue(self.watermark_settings['rotation'])
    
    # 水印应用和预览
    def apply_watermark(self):
        if self.current_image_index == -1 or not self.images:
            QMessageBox.warning(self, "警告", "请先导入图片")
            return
        
        # 保存带水印的图片
        try:
            # 导入简化版水印功能
            import simple_watermark
            
            # 获取当前图片路径
            image_path = self.images[self.current_image_index]
            
            # 确定保存路径
            save_dir = self.export_settings.get('save_path', '')
            if not save_dir or not os.path.exists(save_dir):
                # 如果没有设置保存路径或路径不存在，则使用原图所在目录
                save_dir = os.path.dirname(image_path)
            
            # 确保目录存在
            os.makedirs(save_dir, exist_ok=True)
            
            # 生成保存文件名
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            
            # 根据命名规则生成文件名
            naming_rule = self.export_settings.get('naming_rule', 'prefix')
            if naming_rule == 'prefix':
                prefix = self.export_settings.get('prefix', 'wm_')
                save_filename = f"{prefix}{name}{ext}"
            elif naming_rule == 'suffix':
                suffix = self.export_settings.get('suffix', '_watermarked')
                save_filename = f"{name}{suffix}{ext}"
            else:
                # 原文件名，添加数字避免覆盖
                save_filename = f"{name}_1{ext}"
                
            save_path = os.path.join(save_dir, save_filename)
            
            # 应用水印
            if self.tabs.currentIndex() == 0:  # 如果当前是文本水印选项卡
                self.watermark_settings['type'] = 'text'
                
                # 获取文本水印参数
                text = self.watermark_settings['text']
                font_size = int(self.watermark_settings['font_size'])
                color = self.watermark_settings['color']
                position = self.watermark_settings['position']
                opacity = int(self.watermark_settings['opacity'] * 255 / 100)  # 转换为0-255范围
                rotation = self.watermark_settings['rotation']
                effects = self.watermark_settings['effects']
                
                # 应用文本水印
                success = simple_watermark.apply_text_watermark(
                    image_path, save_path, text, font_size, color, 
                    position, opacity, rotation, effects
                )
            else:  # 如果当前是图片水印选项卡
                self.watermark_settings['type'] = 'image'
                
                # 检查水印图片路径
                if not self.watermark_settings['image_path'] or not os.path.exists(self.watermark_settings['image_path']):
                    raise Exception("水印图片路径无效")
                
                # 获取图片水印参数
                watermark_path = self.watermark_settings['image_path']
                position = self.watermark_settings['position']
                opacity = int(self.watermark_settings['opacity'] * 255 / 100)  # 转换为0-255范围
                rotation = self.watermark_settings['rotation']
                scale = self.watermark_settings['image_scale'] / 100.0
                
                # 应用图片水印
                success = simple_watermark.apply_image_watermark(
                    image_path, save_path, watermark_path, position, 
                    opacity, rotation, scale
                )
            
            # 检查水印应用结果
            if not success:
                raise Exception("水印应用失败")
            
            # 更新预览
            self.update_preview()
            
            # 显示成功消息
            QMessageBox.information(self, "成功", f"已成功应用水印并保存至:\n{save_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用水印失败: {str(e)}")
            print(f"Watermark application error: {e}")
            # 添加详细错误跟踪以便调试
            import traceback
            traceback.print_exc()
    
    def update_preview(self):
        if self.current_image_index == -1 or not self.images:
            return
        
        try:
            # 打开原图
            image_path = self.images[self.current_image_index]
            img = Image.open(image_path).convert("RGBA")  # 确保图像是RGBA模式
            
            # 获取预览区域的实际大小，减去边距和标题高度
            preview_area_width = max(self.preview_label.width() - 40, 600)  # 增加边距
            preview_area_height = max(self.preview_label.height() - 40, 500)  # 增加边距
            
            # 如果预览区域还没有初始化，使用更大的默认值
            if preview_area_width <= 600 or preview_area_height <= 500:
                preview_area_width = 800
                preview_area_height = 600
            
            # 计算保持长宽比的最佳缩放比例
            width_ratio = preview_area_width / img.width
            height_ratio = preview_area_height / img.height
            scale_ratio = min(width_ratio, height_ratio)  # 选择较小的比例以确保图片完全显示
            
            # 如果图片很小，允许适度放大但不超过2倍
            if scale_ratio > 2.0:
                scale_ratio = 2.0
            
            # 计算预览图尺寸
            preview_width = int(img.width * scale_ratio)
            preview_height = int(img.height * scale_ratio)
            
            # 创建预览图 - 使用高质量重采样
            if scale_ratio < 1.0:
                # 缩小时使用LANCZOS
                preview_img = img.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            else:
                # 放大时使用BICUBIC
                preview_img = img.resize((preview_width, preview_height), Image.Resampling.BICUBIC)
            
            # 创建预览图的副本用于应用水印
            watermarked_preview = preview_img.copy()
            
            # 应用水印
            if self.watermark_settings['type'] == 'text':
                self.apply_text_watermark_to_image(watermarked_preview)
            else:
                self.apply_image_watermark_to_image(watermarked_preview)
            
            # 转换为QPixmap并显示
            data = watermarked_preview.tobytes("raw", "RGBA")
            qimg = QImage(data, watermarked_preview.width, watermarked_preview.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg)
            
            # 设置pixmap并保持长宽比
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setScaledContents(False)  # 关闭自动缩放以保持长宽比
            self.preview_label.setAlignment(Qt.AlignCenter)  # 居中显示
            
            # 更新状态栏显示图片信息
            scale_percent = int(scale_ratio * 100)
            self.statusBar().showMessage(f'预览: {os.path.basename(image_path)} - 原始: {img.width}×{img.height} - 预览: {preview_width}×{preview_height} ({scale_percent}%)')
            
        except Exception as e:
            self.preview_label.setText(f"预览失败: {str(e)}")
            print(f"Preview error: {e}")
            self.statusBar().showMessage('预览失败')
    
    def apply_text_watermark_to_image(self, img):
        """将文本水印应用到图像上"""
        # 确保图像是RGBA模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建一个透明图层用于绘制水印
        watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 确保字体大小是整数
        font_size = int(self.watermark_settings['font_size'])
        
        # 直接使用默认字体，避免找不到字体的问题
        font = ImageFont.load_default()
        
        # 尝试根据操作系统获取系统字体
        try:
            import platform
            system = platform.system()
            if system == 'Windows':
                # Windows系统常见字体
                font_paths = [
                    "C:\\Windows\\Fonts\\simhei.ttf",  # 黑体
                    "C:\\Windows\\Fonts\\simsun.ttc",  # 宋体
                    "C:\\Windows\\Fonts\\msyh.ttc",    # 微软雅黑
                    "C:\\Windows\\Fonts\\arial.ttf"    # Arial
                ]
                
                for path in font_paths:
                    if os.path.exists(path):
                        try:
                            font = ImageFont.truetype(path, font_size)
                            break
                        except:
                            continue
            elif system == 'Darwin':  # macOS
                # macOS系统常见字体
                font_paths = [
                    "/System/Library/Fonts/PingFang.ttc",
                    "/System/Library/Fonts/STHeiti Light.ttc",
                    "/System/Library/Fonts/Helvetica.ttc"
                ]
                
                for path in font_paths:
                    if os.path.exists(path):
                        try:
                            font = ImageFont.truetype(path, font_size)
                            break
                        except:
                            continue
            elif system == 'Linux':
                # Linux系统常见字体
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
                ]
                
                for path in font_paths:
                    if os.path.exists(path):
                        try:
                            font = ImageFont.truetype(path, font_size)
                            break
                        except:
                            continue
        except Exception as e:
            print(f"Font loading error: {e}")
        
        # 计算文本大小
        text = self.watermark_settings['text']
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # 旧版Pillow兼容
            text_width, text_height = draw.textsize(text, font=font)
        
        # 计算位置
        position = self.watermark_settings['position']
        margin = 10
        
        if position == 'top_left':
            x, y = margin, margin
        elif position == 'top_center':
            x, y = (img.width - text_width) / 2, margin
        elif position == 'top_right':
            x, y = img.width - text_width - margin, margin
        elif position == 'middle_left':
            x, y = margin, (img.height - text_height) / 2
        elif position == 'center':
            x, y = (img.width - text_width) / 2, (img.height - text_height) / 2
        elif position == 'middle_right':
            x, y = img.width - text_width - margin, (img.height - text_height) / 2
        elif position == 'bottom_left':
            x, y = margin, img.height - text_height - margin
        elif position == 'bottom_center':
            x, y = (img.width - text_width) / 2, img.height - text_height - margin
        else:  # bottom_right
            x, y = img.width - text_width - margin, img.height - text_height - margin
        
        # 处理颜色 - 与simple_watermark.py保持一致
        color = self.watermark_settings['color']
        if isinstance(color, str):
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
            if color.lower() in color_map:
                rgb_color = color_map[color.lower()]
            elif color.startswith('#'):
                # 处理十六进制颜色
                rgb_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            else:
                try:
                    rgb_color = ImageColor.getrgb(color)
                except:
                    rgb_color = (255, 255, 255)  # 默认白色
        else:
            rgb_color = (255, 255, 255)  # 默认白色
        
        # 应用透明度
        opacity = self.watermark_settings['opacity'] / 100.0
        color_with_opacity = rgb_color + (int(255 * opacity),)
        
        # 应用旋转
        if self.watermark_settings['rotation'] != 0:
            # 创建一个新的透明图层，大小足够容纳旋转后的文本
            rotation_layer = Image.new('RGBA', (img.width * 2, img.height * 2), (0, 0, 0, 0))
            rotation_draw = ImageDraw.Draw(rotation_layer)
            
            # 在中心位置绘制文本
            center_x = rotation_layer.width // 2
            center_y = rotation_layer.height // 2
            
            # 绘制阴影和描边效果
            effects = self.watermark_settings['effects']
            print(f"预览中的特效设置: {effects}")
            if effects.get('shadow', False):
                # 绘制阴影（偏移2像素，颜色为半透明黑色）
                shadow_opacity = int(255 * opacity * 0.5)
                shadow_color = (0, 0, 0, shadow_opacity)
                print(f"绘制阴影效果，颜色: {shadow_color}")
                rotation_draw.text((center_x + 2, center_y + 2), text, fill=shadow_color, font=font)
            
            if effects.get('outline', False):
                # 绘制描边效果（在周围8个方向绘制黑色文本）
                outline_opacity = int(255 * opacity)
                outline_color = (0, 0, 0, outline_opacity)
                print(f"绘制描边效果，颜色: {outline_color}")
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            rotation_draw.text((center_x + dx, center_y + dy), text, fill=outline_color, font=font)
            
            # 绘制主文本
            rotation_draw.text((center_x, center_y), text, fill=color_with_opacity, font=font)
            
            # 旋转图层
            rotated_layer = rotation_layer.rotate(-self.watermark_settings['rotation'], resample=Image.BICUBIC, expand=False)
            
            # 裁剪到原始大小并粘贴到水印图层
            crop_left = (rotated_layer.width - img.width) // 2
            crop_top = (rotated_layer.height - img.height) // 2
            crop_right = crop_left + img.width
            crop_bottom = crop_top + img.height
            cropped_layer = rotated_layer.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 将裁剪后的图层与水印图层合并
            watermark_layer = Image.alpha_composite(watermark_layer, cropped_layer)
        else:
            # 绘制阴影和描边效果
            effects = self.watermark_settings['effects']
            print(f"预览中的特效设置(无旋转): {effects}")
            if effects.get('shadow', False):
                # 绘制阴影（偏移2像素，颜色为半透明黑色）
                shadow_opacity = int(255 * opacity * 0.5)
                shadow_color = (0, 0, 0, shadow_opacity)
                print(f"绘制阴影效果(无旋转)，颜色: {shadow_color}")
                draw.text((x + 2, y + 2), text, fill=shadow_color, font=font)
            
            if effects.get('outline', False):
                # 绘制描边效果（在周围8个方向绘制黑色文本）
                outline_opacity = int(255 * opacity)
                outline_color = (0, 0, 0, outline_opacity)
                print(f"绘制描边效果(无旋转)，颜色: {outline_color}")
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, fill=outline_color, font=font)
            
            # 绘制主文本
            draw.text((x, y), text, fill=color_with_opacity, font=font)
        
        # 将水印图层与原图合成
        result = Image.alpha_composite(img, watermark_layer)
        
        # 将结果复制回原图
        img.paste(result)
    
    def apply_image_watermark_to_image(self, img):
        """将图片水印应用到图像上"""
        if not self.watermark_settings['image_path'] or not os.path.exists(self.watermark_settings['image_path']):
            return
        
        try:
            # 确保图像是RGBA模式
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 创建一个透明图层用于绘制水印
            watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            
            # 打开水印图片
            watermark = Image.open(self.watermark_settings['image_path']).convert("RGBA")
            
            # 调整水印大小
            scale = self.watermark_settings['image_scale'] / 100.0
            w = int(watermark.width * scale)
            h = int(watermark.height * scale)
            watermark = watermark.resize((w, h), Image.LANCZOS)
            
            # 应用透明度
            opacity = self.watermark_settings['opacity'] / 100.0
            if opacity < 1.0:
                # 创建一个新的RGBA图像，调整alpha通道
                watermark_data = watermark.getdata()
                new_data = []
                for item in watermark_data:
                    # 调整alpha通道
                    new_data.append((item[0], item[1], item[2], int(item[3] * opacity)))
                watermark.putdata(new_data)
            
            # 应用旋转
            if self.watermark_settings['rotation'] != 0:
                # 使用透明背景进行旋转，确保旋转后的图像保持透明度
                watermark = watermark.rotate(-self.watermark_settings['rotation'], expand=True, resample=Image.BICUBIC, fillcolor=(0,0,0,0))
            
            # 重新计算旋转后的尺寸
            w, h = watermark.size
            
            # 计算位置
            position = self.watermark_settings['position']
            margin = 10
            
            if position == 'top_left':
                x, y = margin, margin
            elif position == 'top_center':
                x, y = (img.width - w) // 2, margin
            elif position == 'top_right':
                x, y = img.width - w - margin, margin
            elif position == 'middle_left':
                x, y = margin, (img.height - h) // 2
            elif position == 'center':
                x, y = (img.width - w) // 2, (img.height - h) // 2
            elif position == 'middle_right':
                x, y = img.width - w - margin, (img.height - h) // 2
            elif position == 'bottom_left':
                x, y = margin, img.height - h - margin
            elif position == 'bottom_center':
                x, y = (img.width - w) // 2, img.height - h - margin
            else:  # bottom_right
                x, y = img.width - w - margin, img.height - h - margin
            
            # 将水印粘贴到透明图层上，使用水印自身作为mask确保透明度正确
            watermark_layer.paste(watermark, (int(x), int(y)), watermark)
            
            # 将水印图层与原图合成
            result = Image.alpha_composite(img, watermark_layer)
            
            # 将结果复制回原图
            img.paste(result)
            
        except Exception as e:
            print(f"Image watermark application error: {e}")
            # 显示更详细的错误信息以便调试
            import traceback
            traceback.print_exc()
    
    def export_images(self):
        if not self.images:
            QMessageBox.warning(self, "警告", "请先导入图片")
            return
        
        output_dir = self.output_path_label.text()
        if output_dir == "未选择输出目录":
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取命名规则
        if self.naming_original.isChecked():
            naming_rule = "original"
        elif self.naming_prefix.isChecked():
            naming_rule = "prefix"
            prefix = self.prefix_input.text()
        else:
            naming_rule = "suffix"
            suffix = self.suffix_input.text()
        
        # 获取输出格式
        output_format = "JPEG" if self.format_jpeg.isChecked() else "PNG"
        quality = self.quality_slider.value() if output_format == "JPEG" else None
        
        # 处理每张图片
        processed_count = 0
        for image_path in self.images:
            try:
                # 打开原图
                img = Image.open(image_path)
                
                # 应用水印
                if self.watermark_settings['type'] == 'text':
                    self.apply_text_watermark_to_image(img)
                else:
                    self.apply_image_watermark_to_image(img)
                
                # 确定输出文件名
                filename = os.path.basename(image_path)
                name, ext = os.path.splitext(filename)
                
                if naming_rule == "original":
                    output_filename = name
                elif naming_rule == "prefix":
                    output_filename = prefix + name
                else:
                    output_filename = name + suffix
                
                # 添加正确的扩展名
                if output_format == "JPEG":
                    output_filename += ".jpg"
                else:
                    output_filename += ".png"
                
                # 保存图片
                output_path = os.path.join(output_dir, output_filename)
                if output_format == "JPEG":
                    img = img.convert("RGB")  # JPEG不支持透明通道
                    img.save(output_path, format=output_format, quality=quality)
                else:
                    img.save(output_path, format=output_format)
                
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        
        if processed_count > 0:
            QMessageBox.information(self, "成功", f"已成功导出 {processed_count} 张图片到 {output_dir}")
        else:
            QMessageBox.warning(self, "警告", "导出过程中出现错误，未能成功导出图片")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec())