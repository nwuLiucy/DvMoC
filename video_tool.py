import cv2
import os
from tqdm import tqdm

def get_info(video_path):
    # 获取视频信息：帧率和总帧数
    video = cv2.VideoCapture(video_path)
    video_fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) # 视频总帧数
    return video_fps, frame_count

def sample_video(src_video, dst_path, video_name = 'video.mp4',fps=25, \
                 n_frames=100, start_frames=None, start_time=None):
    if start_frames is not None and start_time is not None:
        raise ValueError("只能传入start_frames或start_time中的一个")
    # 读取视频
    video = cv2.VideoCapture(src_video)
    if start_frames is not None:
        # 设置视频的起始帧位置
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frames)
    elif start_time is not None:
        # 获取视频的帧率并设置起始帧
        video_fps = video.get(cv2.CAP_PROP_FPS)
        video.set(cv2.CAP_PROP_POS_FRAMES, int(start_time*video_fps))
    
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)) # 视频宽度
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 视频高度
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    out = cv2.VideoWriter(os.path.join(dst_path,video_name), fourcc, fps, (frame_width, frame_height))
    # 截取每个视频的n帧
    progress_bar = tqdm(total = n_frames)
    count = 0
    print('截取视频...')
    while count < n_frames:
        ret, frame = video.read()
        if not ret:  # 当读取到最后一帧时结束循环
            break
        count += 1
        out.write(frame)
        cv2.waitKey(25)
        progress_bar.update(1) # 更新进度条
    progress_bar.close()
    # 释放所有视频对象
    video.release()
    out.release()
    cv2.destroyAllWindows()
    return

def adjust_resolution(input_path,target_width=1280,target_height=720):
    # 读取原始视频
    video = cv2.VideoCapture(input_path)
    video_dir = os.path.dirname(input_path)
    output = os.path.join(video_dir,'output.mp4')
    # 获取原始视频的宽度和高度
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 判断分辨率是否需要调整
    if width != target_width or height != target_height:
        # 创建输出视频对象
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 视频编码格式
        output_video = cv2.VideoWriter(output, fourcc, 30.0, (target_width, target_height))
        # 循环读取每一帧并调整分辨率
        while True:
            ret, frame = video.read()
            if not ret:
                break  
            # 调整帧的分辨率
            resized_frame = cv2.resize(frame, (target_width, target_height))  
            # 写入输出视频
            output_video.write(resized_frame)
        # 释放资源
        video.release()
        output_video.release()
        print("视频分辨率已调整为{}x{}".format(target_width, target_height))
    else:
        print("视频分辨率已符合要求")
    # 新文件替换旧文件
    os.remove(input_path)
    os.rename(output,input_path)
    return