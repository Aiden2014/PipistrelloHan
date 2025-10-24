#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享配置文件
所有脚本共用的路径和常量配置
"""

import os

# ==============================================================================
# 路径配置
# ==============================================================================

# 获取脚本所在目录和项目根目录
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
RESOURCE_DIR = os.path.join(PROJECT_ROOT, 'resources')

# ==============================================================================
# 数据文件路径
# ==============================================================================

# CSV文件
PARATRANZ_FILE = os.path.join(RESOURCE_DIR, 'strings-paratranz.csv')
STRINGS_FILE = os.path.join(RESOURCE_DIR, 'strings.csv')
STRINGS_UPDATED_FILE = os.path.join(RESOURCE_DIR, 'strings_updated.csv')

# 字符相关文件
UNIQUE_CHINESE_CHARS_FILE = os.path.join(RESOURCE_DIR, 'unique_chinese_chars.txt')

# 字体和图片文件
MAIN16_IMAGE = os.path.join(RESOURCE_DIR, 'main16.png')
MAIN16_MODIFIED_IMAGE = os.path.join(RESOURCE_DIR, 'main16_modified.png')
FONT_FILE = os.path.join(RESOURCE_DIR, 'fusion-pixel-12px-proportional-zh_hans.ttf')

# ==============================================================================
# 共享常量
# ==============================================================================

# 需要添加的额外翻译
EXTRA_TRANSLATIONS = {
    'ui_settings_graphics_showFps': '显示帧率',
    'ui_settings_accessibility_lifeRecoveryRetry': '重试时回复生命',
    # 可以在这里添加更多的额外翻译
}

# 额外的中文字符（用于字符提取）
TRANSLATION_EXTRAS = ["語"] + list(EXTRA_TRANSLATIONS.values())

# 额外的符号字符（用于字符提取）
SYMBOL_EXTRAS = ["《", "》"]
