#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本功能：
从 resource/strings-paratranz.csv 中提取所有不重复的中文字符
"""

from const import (
    PARATRANZ_FILE, 
    UNIQUE_CHINESE_CHARS_FILE,
    TRANSLATION_EXTRAS
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
    
    return chinese_chars


def update_plugin_cs(sorted_chars):
    """更新Plugin.cs文件中的newChars字符串"""
    # 获取Plugin.cs的路径（在scripts的上一级目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_cs_path = os.path.join(os.path.dirname(script_dir), 'Plugin.cs')
    
    if not os.path.exists(plugin_cs_path):
        print(f"\n警告: Plugin.cs文件不存在: {plugin_cs_path}")
        return
    
    print(f"\n正在更新Plugin.cs中的newChars...")
    
    # 读取Plugin.cs文件
    with open(plugin_cs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建新的字符串
    new_chars_str = ''.join(sorted_chars)
    
    # 使用正则表达式查找并替换newChars的值
    # 匹配模式: string newChars = "任意字符";
    pattern = r'(string\s+newChars\s*=\s*)"[^"]*"'
    replacement = r'\1"' + new_chars_str + '"'
    
    new_content, count = re.subn(pattern, replacement, content)
    
    if count == 0:
        print("警告: 未找到newChars变量，无法更新")
        return
    
    # 写回文件
    with open(plugin_cs_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"成功更新Plugin.cs中的newChars ({len(sorted_chars)} 个字符)")
    print(f"Plugin.cs路径: {plugin_cs_path}")


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
    
    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"CSV文件中不重复的中文字符（共 {len(unique_chars)} 个）\n")
        f.write("=" * 80 + "\n\n")
        
        # 以字符串形式保存（方便复制使用）
        f.write("所有不重复的中文字符：\n")
        f.write(''.join(sorted_chars) + "\n\n")
        
        # 详细信息（字符和Unicode编码）
        f.write("=" * 80 + "\n")
        f.write("详细信息（字符 | Unicode）：\n")
        for char in sorted_chars:
            f.write(f"{char} | U+{ord(char):04X}\n")
    
    print(f"\n结果已保存到: {output_file}")
    print(f"\n字符预览: {''.join(sorted_chars[:100])}{'...' if len(sorted_chars) > 100 else ''}")
    
    # 更新Plugin.cs中的newChars字符串
    update_plugin_cs(sorted_chars)


if __name__ == '__main__':
    main()
