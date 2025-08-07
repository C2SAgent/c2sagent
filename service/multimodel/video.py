import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os


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
):
    """
    创建文字滚动视频

    参数:
        text: 要滚动的文字
        output_path: 输出视频路径
        duration: 视频时长(秒)
        fps: 帧率
        width: 视频宽度
        height: 视频高度
        bg_color: 背景颜色 (B, G, R)
        text_color: 文字颜色 (B, G, R)
        font_size: 字体大小
    """
    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 加载字体 (使用系统字体或指定字体文件路径)
    try:
        font = ImageFont.truetype("simhei.ttf", font_size)  # 使用黑体
    except:
        font = ImageFont.load_default()

    # 计算文字宽度和滚动距离
    img = Image.new("RGB", (width, height), (bg_color[2], bg_color[1], bg_color[0]))
    draw = ImageDraw.Draw(img)
    text_width = draw.textlength(text, font=font)
    total_frames = int(duration * fps)
    scroll_distance = text_width + width  # 滚动总距离

    # 生成每一帧
    for frame_num in range(total_frames):
        # 计算当前滚动位置
        progress = frame_num / total_frames
        x_pos = int(width - scroll_distance * progress)

        # 创建空白图像
        img = Image.new("RGB", (width, height), (bg_color[2], bg_color[1], bg_color[0]))
        draw = ImageDraw.Draw(img)

        # 绘制文字
        draw.text(
            (x_pos, (height - font_size) // 2),
            text,
            fill=(text_color[2], text_color[1], text_color[0]),
            font=font,
        )

        # 转换为OpenCV格式并写入视频
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        video.write(frame)

    # 释放视频写入对象
    video.release()
    print(f"视频已保存到: {output_path}")


# 示例使用
if __name__ == "__main__":
    text = "这是一个文字滚动视频的示例，使用Python和OpenCV生成。"
    output_path = "scrolling_text.mp4"

    create_scrolling_text_video(
        text=text,
        output_path=output_path,
        duration=10,
        fps=30,
        width=800,
        height=200,
        bg_color=(0, 0, 0),  # 黑色背景
        text_color=(255, 255, 255),  # 白色文字
        font_size=40,
    )
