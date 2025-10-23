#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 strings-paratranz.csv 第三列的翻译内容复制到 strings.csv 的第七列（ja_JP）
根据第一列（String ID）进行匹配
支持带前缀的ID匹配，例如：
  ^1$area5_hitTheRoad1 -> area5_hitTheRoad1 后的第1个 ^
  ^2$area5_hitTheRoad1 -> area5_hitTheRoad1 后的第2个 ^
"""

import csv
import os
import re
from const import (
    PARATRANZ_FILE,
    STRINGS_FILE,
    STRINGS_UPDATED_FILE,
    EXTRA_TRANSLATIONS
)

def parse_string_id(string_id):
    """
    解析字符串ID，提取基础ID和序号
    例如：^1$area5_hitTheRoad1 -> ('area5_hitTheRoad1', 1)
         area5_hitTheRoad1 -> ('area5_hitTheRoad1', 0)
    """
    match = re.match(r'^\^(\d+)\$(.+)$', string_id)
    if match:
        index = int(match.group(1))
        base_id = match.group(2)
        return (base_id, index)
    return (string_id, 0)

def main():
    print("开始处理翻译文件...")
    
    # 第一步：读取 paratranz 文件，建立 ID -> 翻译的映射
    print(f"正在读取 {os.path.basename(PARATRANZ_FILE)}...")
    translations = {}
    
    with open(PARATRANZ_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3 and row[0]:  # 确保有至少3列且第一列不为空
                string_id = row[0]
                translation = row[2] if len(row) > 2 else ""
                translation = translation.replace('\\n', '\r\n')
                translations[string_id] = translation
    
    print(f"已读取 {len(translations)} 条翻译")
    
    # 第二步：读取 strings.csv 文件
    print(f"正在读取 {os.path.basename(STRINGS_FILE)}...")
    rows = []
    
    with open(STRINGS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    
    print(f"已读取 {len(rows)} 行数据")

    # 添加更新后添加的翻译
    for extra_id, extra_translation in EXTRA_TRANSLATIONS.items():
        translations[extra_id] = extra_translation

    
    # 第三步：更新第七列（ja_JP，索引为6）
    print("正在更新翻译...")
    updated_count = 0
    skipped_count = 0
    
    # 用于跟踪当前基础ID和其后续的^行
    current_base_id = None
    continuation_index = 0
    
    for i, row in enumerate(rows):
        if len(row) > 0:
            row_id = row[0]
            
            # 检查是否是新的基础ID还是续行（^）
            if row_id and row_id != '^':
                # 新的基础ID
                current_base_id = row_id
                continuation_index = 0
                
                # 尝试直接匹配
                if row_id in translations:
                    # 确保行有足够的列
                    while len(row) < 13:
                        row.append("")
                    
                    old_value = row[6] if len(row) > 6 else ""
                    new_value = translations[row_id]
                    
                    if old_value != new_value:
                        row[6] = new_value
                        updated_count += 1
                        if updated_count <= 20:  # 只显示前20个更新示例
                            print(f"  [{row_id}] 更新")
                else:
                    skipped_count += 1
                    
            elif row_id == '^' and current_base_id:
                # 这是一个续行
                continuation_index += 1
                prefixed_id = f"^{continuation_index}${current_base_id}"
                
                if prefixed_id in translations:
                    # 确保行有足够的列
                    while len(row) < 13:
                        row.append("")
                    
                    old_value = row[6] if len(row) > 6 else ""
                    new_value = translations[prefixed_id]
                    
                    if old_value != new_value:
                        row[6] = new_value
                        updated_count += 1
                        if updated_count <= 20:  # 只显示前20个更新示例
                            print(f"  [{prefixed_id}] 更新 (续行 {continuation_index})")
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
        else:
            skipped_count += 1
    
    print(f"已更新 {updated_count} 条翻译")
    print(f"跳过 {skipped_count} 行（无匹配或空ID）")
    
    # 第四步：写回文件
    print(f"正在保存到 {os.path.basename(STRINGS_UPDATED_FILE)}...")
    
    with open(STRINGS_UPDATED_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print("完成！")

if __name__ == "__main__":
    main()
