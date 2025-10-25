#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本功能：
从 resource/strings-paratranz.csv 中提取所有不重复的中文字符
"""

from const import (
    PARATRANZ_FILE, 
    UNIQUE_CHINESE_CHARS_FILE,
    TRANSLATION_EXTRAS,
    SYMBOL_EXTRAS
)
import os
import re

translation_extras = TRANSLATION_EXTRAS

def is_chinese_char(char):
    """判断是否为中文字符（包括CJK统一汉字）"""
    code_point = ord(char)
    # CJK统一汉字基本区: U+4E00 - U+9FFF
    # CJK统一汉字扩展A区: U+3400 - U+4DBF
    # CJK统一汉字扩展B-F区: U+20000 - U+2EBEF
    # CJK兼容汉字: U+F900 - U+FAFF
    return (0x4E00 <= code_point <= 0x9FFF or
            0x3400 <= code_point <= 0x4DBF or
            0x20000 <= code_point <= 0x2EBEF or
            0xF900 <= code_point <= 0xFAFF)


def extract_unique_chinese_chars(file_path):
    """从CSV文件中提取所有不重复的中文字符"""
    chinese_chars = set()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # 读取整个文件内容
        content = f.read()
        # 提取所有中文字符（自动去重）
        for char in content:
            if is_chinese_char(char):
                chinese_chars.add(char)

    # 添加额外的翻译字符
    for extra_char in translation_extras:
        for char in extra_char:
            if is_chinese_char(char):
                chinese_chars.add(char)
    
    # 添加额外的符号字符
    for symbol in SYMBOL_EXTRAS:
        chinese_chars.add(symbol)

    return chinese_chars


def main():
    # 使用共享配置中的文件路径
    csv_file = PARATRANZ_FILE
    output_file = UNIQUE_CHINESE_CHARS_FILE
    
    # 提取不重复的中文字符
    print(f"正在读取CSV文件: {csv_file}")
    unique_chars = extract_unique_chinese_chars(csv_file)
    
    print(f"提取到 {len(unique_chars)} 个不重复的中文字符")

    # 按Unicode编码排序
    sorted_chars = sorted(unique_chars, key=lambda x: ord(x))
    
    # 保存到文件（只保存一行字符）
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(sorted_chars))
    
    print(f"\n结果已保存到: {output_file}")
    print(f"共 {len(sorted_chars)} 个字符")
    print(f"字符预览: {''.join(sorted_chars[:100])}{'...' if len(sorted_chars) > 100 else ''}")


if __name__ == '__main__':
    main()
