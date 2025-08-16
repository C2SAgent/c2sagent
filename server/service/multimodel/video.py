import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import sys

# 确保标准输出和文件读取使用 UTF-8
sys.stdout.reconfigure(encoding="utf-8")  # Python 3.7+


def create_scrolling_text_video(
    text,
    output_path,
    duration=10,
    fps=30,
    width=800,
    height=200,
    bg_color=(0, 0, 0),
    text_color=(255, 255, 255),
    font_size=40,
    font_path=None,
):
    """创建文字向上滚动视频（强制 UTF-8 处理）"""
    # 确保文本是 Unicode 字符串（Python 2/3 兼容）
    if isinstance(text, bytes):
        text = text.decode("gbk")

    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 加载字体（优先使用支持中文的字体）
    font = None
    if font_path and os.path.exists(font_path):
        try:
            font = ImageFont.truetype(font_path, font_size)
            print(f"使用指定字体: {font_path}")
        except:
            pass

    # 如果未指定或加载失败，尝试系统默认中文字体
    if font is None:
        system_fonts = [
            "simhei.ttf",  # Windows 黑体
            "msyh.ttc",  # Windows 微软雅黑
            "/System/Library/Fonts/STHeiti Medium.ttc",  # MacOS 黑体
            "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",  # Linux 文泉驿
        ]
        for font_file in system_fonts:
            try:
                font = ImageFont.truetype(font_file, font_size)
                print(f"使用系统字体: {font_file}")
                break
            except:
                continue

    # 如果仍然失败，使用默认字体（可能不支持中文）
    if font is None:
        print("警告: 未找到中文字体，使用默认字体（可能乱码）")
        font = ImageFont.load_default()

    # 计算文字高度和滚动距离
    lines = text.split("\n")
    line_height = font_size + 5
    total_text_height = len(lines) * line_height
    scroll_distance = total_text_height + height
    total_frames = int(duration * fps)

    for frame_num in range(total_frames):
        img = Image.new("RGB", (width, height), (bg_color[2], bg_color[1], bg_color[0]))
        draw = ImageDraw.Draw(img)
        y_pos = int(height - scroll_distance * (frame_num / total_frames))

        for i, line in enumerate(lines):
            # 计算文字宽度并居中
            text_width = draw.textlength(line, font=font)
            x_pos = (width - text_width) // 2
            draw.text(
                (x_pos, y_pos + i * line_height),
                line,
                fill=(text_color[2], text_color[1], text_color[0]),
                font=font,
            )

        # 转换为 OpenCV 格式并写入视频
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        video.write(frame)

    video.release()
    print(f"视频已保存: {output_path}")


# 示例使用
if __name__ == "__main__":
    text = "这是一个测试\n中文显示正常吗？\n如果还有问题请检查字体！"
    output_path = "chinese_scroll.mp4"

    # 指定字体路径（如果知道）
    # font_path = "C:/Windows/Fonts/msyh.ttc"  # Windows 微软雅黑

    create_scrolling_text_video(
        text=text,
        output_path=output_path,
        font_path=None,  # 自动查找字体
        font_size=40,
    )
