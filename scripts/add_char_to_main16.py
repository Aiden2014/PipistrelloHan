from PIL import Image, ImageDraw, ImageFont
import math
from const import (
    MAIN16_IMAGE,
    MAIN16_MODIFIED_IMAGE,
    FONT_FILE,
    UNIQUE_CHINESE_CHARS_FILE
)

# ==============================================================================
# 1. 配置参数
# ==============================================================================

# --- 布局与网格 ---
# 第一行竖线位置（包括深红色）
first_vertical_line_start = 557  # 深红色开始位置
first_vertical_line_red_start = 559  # 红色开始位置
# 第一列竖线的X坐标
vertical_line_x = 0
# 第一个字符的红色竖线范围：0,559 到 0,572（14像素）
# 第一条横线位置：5,576 到 17,576
# 第一个字符范围：5,559 到 17,572
first_char_x_start = 5
first_char_y_start = 559  # 与红色竖线开始位置相同
first_horizontal_line_y = 576
# 横线之间的间距模式：根据实际精确测量
# 实际坐标: 5-17, 21-33, 37-49, 54-66, 70-82, 86-98, 102-114, 119-131...
# 间距规律: 4, 4, 5, 4, 4, 4, 5, 4, 4, 4, 5... (每3个4后跟一个5)
horizontal_line_spacing_pattern = [4, 4, 5, 4, 4, 4, 5, 4, 4, 4, 5, 4, 4, 4, 5, 4, 4, 4, 5, 4, 4, 4, 5, 4, 4]
# 字符内容宽度：13像素 (例如：5到17是13个像素点)
cell_content_width = 11
# 第二行第一个字符：红色竖线0,580到0,593
second_row_vertical_line_y = 580
# 竖线间距：580-559=21像素
vertical_line_spacing = 21  # 每行竖线之间的垂直间距（红色部分）
# 横线垂直间距：597-576=21像素
horizontal_line_vertical_spacing = 21  # 每行横线之间的垂直间距
# 字符可用高度：从559到572是14个像素点
cell_content_height = 11  # 字符内容区域高度
# 每行可以容纳多少个字符
chars_per_row = 26

# 简化变量（兼容旧代码）
start_x = first_char_x_start  # 5
start_y = first_char_y_start  # 559
cell_height = cell_content_height  # 11
row_spacing = horizontal_line_vertical_spacing  # 21

# --- 字体与样式 ---
# 字体大小 (需要反复尝试以匹配原始风格)
font_size = 12
# 字符在单元格内的偏移量 (用于微调居中)
text_offset_x = 0
text_offset_y = 0
# 字符颜色 (R, G, B, A) - (255, 255, 255, 255) 是白色
text_color = (255, 255, 255, 255)

# --- 红色框线样式 ---
# 框线颜色 (R, G, B)
underline_color = (255, 0, 0)
# 框线粗细 (像素)
underline_thickness = 1

# --- 网格线样式 ---
# 竖线颜色（深红色）
dark_red_color = (130, 0, 0)  # #820000
# 红色
red_color = (255, 0, 0)  # #FF0000
# 第一列竖线
left_line_red_height = 14  # 红色主体高度（559到572是14像素：0,1,2...13）
left_line_extension = 2  # 上下深红色延伸各2像素
# 横线与字符区域的关系
# 第一个字符：Y范围559-572(13像素)，横线在576
# 字符底部到横线的距离：576-572=4像素
char_to_line_spacing = 4

# 后引号”横线位置
back_quotation_mark_line_x_start = 108
back_quotation_mark_line_x_length = 6
back_quotation_mark_line_y = 193
# 复制的后引号原来的位置
back_quotation_mark_copy_x_start = 52
back_quotation_mark_copy_x_length = 7
back_quotation_mark_copy_y_start = 185
back_quotation_mark_copy_y_length = 6
# 复制的后引号的位置
back_quotation_mark_copy_target_x_start = 108
back_quotation_mark_copy_target_y_start = 176

# ·号配置
dot_line_x_start = back_quotation_mark_line_x_start + back_quotation_mark_line_x_length + 3  # ·号横线起始X
dot_line_x_length = 7   # ·号横线长度
dot_line_y = 193        # ·号横线Y坐标
dot_x_start = dot_line_x_start + 3  # ·号起始X坐标
dot_y_start = 183  # ·号起始Y坐标
dot_x_end = dot_x_start + 1   # ·号结束X坐标
dot_y_end = dot_y_start + 1   # ·号结束Y坐标


# ==============================================================================
# 2. 脚本主逻辑 (无需修改)
# ==============================================================================

def generate_modified_atlas():
    """
    主函数，执行所有操作。
    """
    print("--- 开始处理字体图集 ---")

    # 加载输入文件
    try:
        print(f"1. 加载原始图片: {MAIN16_IMAGE}")
        original_image = Image.open(MAIN16_IMAGE).convert("RGBA")

        print(f"2. 加载字体: {FONT_FILE}")
        font = ImageFont.truetype(FONT_FILE, font_size)

        print(f"3. 读取字符列表: {UNIQUE_CHINESE_CHARS_FILE}")
        with open(UNIQUE_CHINESE_CHARS_FILE, "r", encoding="utf-8") as f:
            chars_to_draw = f.read().strip()
        print(f"   找到 {len(chars_to_draw)} 个字符需要绘制。")

    except FileNotFoundError as e:
        print(f"错误: 找不到文件 {e.filename}。请检查文件路径配置。")
        return

    # 计算新图片尺寸
    original_width, original_height = original_image.size
    num_rows_needed = math.ceil(len(chars_to_draw) / chars_per_row)
    # 使用vertical_line_spacing而不是cell_height，因为行间距是21px
    new_section_height = num_rows_needed * vertical_line_spacing + cell_height + 10  # 额外+10像素作为底部缓冲
    new_total_height = start_y + new_section_height

    # 如果需要，创建一张更高的新画布
    if new_total_height > original_height:
        print(f"4. 新内容需要更多空间。创建新画布，高度: {new_total_height}px。")
        new_image = Image.new("RGBA", (original_width, new_total_height), (0, 0, 0, 0))
    else:
        print("4. 新内容可以在原图尺寸内完成。")
        new_image = original_image.copy() # 先复制一份

    # 粘贴原始图片中不需要修改的部分
    # 保留从0,0到Y=557的内容（557是深红色延伸的起点）
    preserve_height = first_vertical_line_start  # 557
    print(f"5. 复制原图保留区域 (从 0,0 到 {original_width},{preserve_height})。")
    preserved_region = original_image.crop((0, 0, original_width, preserve_height))
    new_image.paste(preserved_region, (0, 0))
    
    # 清空从Y=557开始到图片底部的区域（设置为透明）
    print(f"   清空区域: 从 Y={preserve_height} 到底部（设置为透明）")
    # 创建一个透明区域覆盖需要清空的部分
    clear_region = Image.new("RGBA", (original_width, new_total_height - preserve_height), (0, 0, 0, 0))
    new_image.paste(clear_region, (0, preserve_height))

    # 准备绘制
    draw = ImageDraw.Draw(new_image)
    print("6. 开始批量绘制新字符和网格线...")

    # 计算总行数
    total_rows = math.ceil(len(chars_to_draw) / chars_per_row)
    
    # 绘制网格线
    print("   6.1 绘制横线...")
    # 横线位置计算：第一条在576，第二条在597，垂直间距21
    # 但横线的水平位置需要按照间距模式计算
    for row in range(total_rows):  # 移除 +1，只绘制实际字符行数的横线
        y_line = first_horizontal_line_y + row * horizontal_line_vertical_spacing
        
        # 计算这一行实际有多少个字符
        chars_in_this_row = min(chars_per_row, len(chars_to_draw) - row * chars_per_row)
        
        # 绘制每一段横线，只绘制有字符的格子下方的横线
        current_x = start_x  # 从5开始
        for col in range(chars_in_this_row):  # 只绘制有字符的列
            # 每个字符格子的横线：从current_x画到current_x+12就是13个像素点(5到17)
            line_segment_end = current_x + cell_content_width
            draw.line([(current_x, y_line), (line_segment_end, y_line)], 
                      fill=red_color, width=underline_thickness)
            
            # 移动到下一个格子的起点
            # 当前起点 + 格子宽度(终点偏移) + 间距 = 下一个起点
            # 例如：5 + 12 + 4 = 21 ✓
            spacing = horizontal_line_spacing_pattern[col % len(horizontal_line_spacing_pattern)]
            current_x = current_x + cell_content_width + spacing
    
    print("   6.2 绘制第一列竖线...")
    # 竖线位置：第一行在559(红色开始)，第二行在580，间距21
    for row in range(total_rows):
        # 红色竖线起点
        y_red_start = first_vertical_line_red_start + row * vertical_line_spacing
        # 红色竖线终点（14像素高）
        y_red_end = y_red_start + left_line_red_height - 1  # 559到572是14像素(0-13)
        
        # 绘制红色主体
        draw.line([(vertical_line_x, y_red_start), (vertical_line_x, y_red_end)], 
                  fill=red_color, width=underline_thickness)
        
        # 上延伸（深红色，2个像素）
        for i in range(left_line_extension):
            draw.point((vertical_line_x, y_red_start - i - 1), fill=dark_red_color)
        
        # 下延伸（深红色，2个像素）
        for i in range(1, left_line_extension + 1):
            draw.point((vertical_line_x, y_red_end + i), fill=dark_red_color)
    
    # 绘制字符
    print("   6.3 绘制字符...")
    total_chars = len(chars_to_draw)
    for i, char in enumerate(chars_to_draw):
        # 每100个字符显示一次进度
        if i % 100 == 0:
            print(f"      进度: {i}/{total_chars} ({i*100//total_chars}%) - 当前字符: {char}")
        
        row = i // chars_per_row
        col = i % chars_per_row

        # 计算字符X坐标，按照间距模式累加
        x = start_x  # 从5开始
        for c in range(col):
            # 跳过前面的格子：格子宽度 + 间距
            x += cell_content_width + horizontal_line_spacing_pattern[c % len(horizontal_line_spacing_pattern)]
        
        # Y坐标：第一行559，第二行580，间距21
        y = first_char_y_start + row * vertical_line_spacing

        # 使用位图模式绘制字符（无抗锯齿）
        # 创建一个临时的单色图像（1位）
        char_width = cell_content_width + 4  # 稍微大一点以容纳字符
        char_height = cell_content_height + 4
        temp_image = Image.new('1', (char_width, char_height), 0)  # '1'模式是1位黑白图像
        temp_draw = ImageDraw.Draw(temp_image)
        
        # 在临时图像上绘制字符（纯黑白，无抗锯齿）
        temp_draw.text(
            (text_offset_x, text_offset_y),
            char,
            font=font,
            fill=1  # 1表示白色（在1位图像中）
        )
        
        # 将1位图像转换为RGBA，并应用纯白色
        # 创建一个RGBA图像用于粘贴
        temp_rgba = Image.new('RGBA', (char_width, char_height), (0, 0, 0, 0))
        temp_pixels = temp_image.load()
        rgba_pixels = temp_rgba.load()
        
        # 将白色像素转换为纯白色RGBA
        for py in range(char_height):
            for px in range(char_width):
                if temp_pixels[px, py] == 1:
                    rgba_pixels[px, py] = text_color
        
        # 粘贴到主图像上
        new_image.paste(temp_rgba, (x, y), temp_rgba)

    # 绘制后引号”
    print("   6.4 绘制后引号”...")
    draw.line([(back_quotation_mark_line_x_start, back_quotation_mark_line_y), 
                (back_quotation_mark_line_x_start + back_quotation_mark_line_x_length, back_quotation_mark_line_y)], 
               fill=red_color, width=underline_thickness)
    # 复制后引号”到新位置
    back_quotation_region = new_image.crop((back_quotation_mark_copy_x_start, 
                                            back_quotation_mark_copy_y_start, 
                                            back_quotation_mark_copy_x_start + back_quotation_mark_copy_x_length, 
                                            back_quotation_mark_copy_y_start + back_quotation_mark_copy_y_length))
    new_image.paste(back_quotation_region, (back_quotation_mark_copy_target_x_start, back_quotation_mark_copy_target_y_start))

    print("   6.5 绘制·号...")
    draw.line([(dot_line_x_start, dot_line_y), 
                (dot_line_x_start + dot_line_x_length, dot_line_y)], 
               fill=red_color, width=underline_thickness)
    # 直接画图绘制·号 - 填充矩形区域为白色
    for y in range(dot_y_start, dot_y_end + 1):
        for x in range(dot_x_start, dot_x_end + 1):
            draw.point((x, y), fill=text_color)
    


    print(f"      完成: {total_chars}/{total_chars} (100%)")

    # 保存最终图片
    new_image.save(MAIN16_MODIFIED_IMAGE)
    print(f"7. 处理完成！新图片已保存至: {MAIN16_MODIFIED_IMAGE}")
    print("--- 任务结束 ---")

if __name__ == "__main__":
    generate_modified_atlas()