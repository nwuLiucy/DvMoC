import os
import sys
import socket

import paramiko
import shutil
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *

import video_tool as vtool


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        title = "双视角多目标计数系统"
        self.setWindowTitle(title)

        icon = QIcon('icon.png')
        icon = QIcon(icon)
        self.setWindowIcon(icon)
        # self.center()
        # 标准输出显示框
        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setFixedHeight(100)
        self.wgt_video1 = QVideoWidget()  # 视频显示的widget
        self.wgt_video2 = QVideoWidget()  # 视频显示的widget
        self.video_path1 = r'network1.mp4'
        self.video_path2 = r'network2.mp4'
        self.set_duration()
        self.current_frame1 = 1
        self.current_frame2 = 1
        self.sample_interval = ''
        self.main_file = ''
        self.aux_file = ''
        self.set_ui()
        self.showMaximized()

    def write(self, text):
        # 将标准输出重定向
        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.output_text_edit.setTextCursor(cursor)
        self.output_text_edit.ensureCursorVisible()

    def set_ui(self):
        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 界面1：登录界面
        self.login_page = QWidget()
        self.set_login_page()
        self.stacked_widget.addWidget(self.login_page)

        # 界面2：连接成功界面
        self.success_page = QWidget()
        self.set_success_page()
        self.stacked_widget.addWidget(self.success_page)

        # 界面3：连接失败界面
        self.failure_page = QWidget()
        self.set_failure_page()
        self.stacked_widget.addWidget(self.failure_page)

        self.stacked_widget.setCurrentIndex(0) # 设置登录页或成功页

    def set_login_page(self):
        vbox = QVBoxLayout()  # 垂直布局
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(20)  # 设置控件之间的垂直距离为20像素

        font = QFont("Times New Roman", 18)  # 创建一个字体对象
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(255, 255, 255))  # 设置为白色

        # 服务器地址输入框
        hbox1 = QHBoxLayout()  # 水平布局
        hbox1.setAlignment(Qt.AlignCenter)
        self.host_label = QLabel('地址')
        self.host_entry = QLineEdit('10.15.14.198')  # 默认值
        self.host_label.setFixedWidth(60)
        self.host_entry.setFixedWidth(300)
        self.host_label.setFont(font)
        self.host_entry.setFont(font)
        self.host_label.setAlignment(Qt.AlignCenter)  # 设置文本居中对齐
        self.host_label.setAutoFillBackground(True)
        self.host_label.setPalette(palette)
        hbox1.addWidget(self.host_label)
        hbox1.addWidget(self.host_entry)

        # 用户名输入框
        hbox2 = QHBoxLayout()
        hbox2.setAlignment(Qt.AlignCenter)
        self.username_label = QLabel('用户')
        self.username_entry = QLineEdit('asus')
        self.username_label.setFixedWidth(60)
        self.username_entry.setFixedWidth(300)
        self.username_label.setFont(font)
        self.username_entry.setFont(font)
        self.username_label.setAlignment(Qt.AlignCenter)
        self.username_label.setAutoFillBackground(True)
        self.username_label.setPalette(palette)
        hbox2.addWidget(self.username_label)
        hbox2.addWidget(self.username_entry)

        # 密码输入框
        hbox3 = QHBoxLayout()
        hbox3.setAlignment(Qt.AlignCenter)
        self.password_label = QLabel('密码')
        self.password_entry = QLineEdit('123456')
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_label.setFixedWidth(60)
        self.password_entry.setFixedWidth(300)
        self.password_label.setFont(font)
        self.password_entry.setFont(font)
        self.password_label.setAlignment(Qt.AlignCenter)
        self.password_label.setAutoFillBackground(True)
        self.password_label.setPalette(palette)
        hbox3.addWidget(self.password_label)
        hbox3.addWidget(self.password_entry)

        # 登录按钮
        login_button = QPushButton('登录')
        login_button.setFont(font)
        login_button.clicked.connect(self.login)
        hbox4 = QHBoxLayout()
        hbox4.setAlignment(Qt.AlignCenter)
        hbox4.addWidget(login_button)

        # vbox.addLayout(self.title_bar)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)

        # 设置登录页背景图片
        label = QLabel(self.login_page)
        label.setStyleSheet("border-image:url(background.jpg);")
        screen_width, screen_height = self.get_screen_size()
        label.setFixedSize(screen_width, screen_height)

        self.login_page.setLayout(vbox)

    def set_success_page(self):
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(20)  # 设置控件之间的垂直距离为20像素

        # 通用元素
        icon = QIcon('upload.png')
        font = QFont("Times New Roman", 14)  # 创建一个字体对象

        # 主视角
        hbox1 = QHBoxLayout()
        hbox1.setAlignment(Qt.AlignCenter)
        main_label = QLabel('主视角:')
        main_label.setFixedWidth(80)
        main_label.setFont(font)
        main_file = QLineEdit()
        main_file.setFont(font)

        def set_main_file():
            self.main_file = main_file.text()
            # print('主视角文件为：{}'.format(self.main_file))
        main_file.textChanged.connect(set_main_file)

        main_button = QPushButton(icon, '')
        main_button.setFixedWidth(60)

        def upload_main_file():
            file_dialog = QFileDialog()
            file_name = file_dialog.getOpenFileName(None, "选择文件", "", "*.mp4")
            if file_name[0]:
                main_file.setText(file_name[0])
        main_button.clicked.connect(upload_main_file)
        main_button.clicked.connect(lambda: main_file.setCursorPosition(0))

        hbox1.addWidget(main_label)
        hbox1.addWidget(main_file)
        hbox1.addWidget(main_button)

        vbox.addLayout(hbox1)

        # 辅视角
        hbox2 = QHBoxLayout()
        hbox2.setAlignment(Qt.AlignCenter)
        aux_label = QLabel('辅视角:')
        aux_label.setFixedWidth(80)
        aux_file = QLineEdit()
        aux_label.setFont(font)
        aux_file.setFont(font)

        def set_aux_file():
            self.aux_file = aux_file.text()
        aux_file.textChanged.connect(set_aux_file)

        aux_button = QPushButton(icon, '')
        aux_button.setFixedWidth(60)

        def upload_aux_file():
            file_dialog = QFileDialog()
            file_name = file_dialog.getOpenFileName(None, "选择文件", "", "*.mp4")
            if file_name[0]:
                aux_file.setText(file_name[0])
        aux_button.clicked.connect(upload_aux_file)
        aux_button.clicked.connect(lambda: aux_file.setCursorPosition(0))

        hbox2.addWidget(aux_label)
        hbox2.addWidget(aux_file)
        hbox2.addWidget(aux_button)

        vbox.addLayout(hbox2)

        # 上传至服务器
        hbox3 = QHBoxLayout()
        hbox3.setAlignment(Qt.AlignCenter)
        # 是否使用GPU
        self.device_button = QCheckBox()
        self.device_button.setText('使用GPU加速')
        self.device_button.setChecked(True)
        self.device_button.setFont(font)
        self.device_button.setFixedWidth(180)
        # 采样间隔标签
        sample_interval_label = QLabel('采样间隔:')
        sample_interval_label.setFont(font)
        sample_interval_label.setFixedWidth(100)
        # 采样间隔时间单位
        self.sample_interval_unit = QComboBox()
        self.sample_interval_unit.addItems(['秒', '分钟', '帧'])
        self.sample_interval_unit.setFixedWidth(80)
        self.sample_interval_unit.setFont(font)
        # 采样间隔时间
        self.sample_interval_entry = QLineEdit()
        self.sample_interval_entry.setFont(font)
        self.sample_interval_entry.setFixedWidth(100)
        validator = QIntValidator(1, 9999)  # 创建整数验证器
        self.sample_interval_entry.setValidator(validator)  # 设置验证器到QLineEdit控件
        self.sample_interval_entry.textChanged.connect(
            self.set_sample_interval)

        # 采样长度
        self.sample_length_label = QLabel('采样长度(帧)')
        self.sample_length_label.setFont(font)
        self.sample_length_label.setFixedWidth(140)
        self.sample_length_entry = QLineEdit('60')
        self.sample_length_entry.setFont(font)
        self.sample_length_entry.setFixedWidth(50)
        self.sample_length_entry.setAlignment(Qt.AlignCenter)
        validator = QIntValidator(1, 9999)  # 创建整数验证器
        self.sample_length_entry.setValidator(validator)

        self.setup_button = QPushButton('执行')
        self.setup_button.setFixedWidth(100)
        self.setup_button.setFont(font)
        self.setup_button.clicked.connect(self.set_video_play)

        hbox3.addWidget(self.device_button)
        hbox3.addWidget(sample_interval_label)
        hbox3.addWidget(self.sample_interval_entry)
        hbox3.addWidget(self.sample_interval_unit)
        hbox3.addWidget(self.sample_length_label)
        hbox3.addWidget(self.sample_length_entry)
        hbox3.addWidget(self.setup_button)
        vbox.addLayout(hbox3)

        # 人数显示模块
        hbox4 = QHBoxLayout()
        hbox4.setAlignment(Qt.AlignCenter)
        font2 = QFont("Times New Roman", 24)  # 创建一个字体对象
        cur_num_label = QLabel('当前人数')
        cur_num_label.setFixedWidth(100)
        cur_num_label.setAlignment(Qt.AlignCenter)  # 设置文本居中对齐
        cur_num_label.setFont(font)

        self.cur_num = QLineEdit()
        self.cur_num.setAlignment(Qt.AlignCenter)
        self.cur_num.setReadOnly(True)
        self.cur_num.setFixedWidth(80)
        self.cur_num.setFont(font2)
        palette = QPalette()
        palette.setColor(QPalette.Text, QColor(255, 0, 0))  # 设置文字颜色为红色
        self.cur_num.setPalette(palette)

        history_num_label = QLabel('历史人数')
        history_num_label.setFixedWidth(100)
        history_num_label.setFont(font)
        self.history_num = QTextEdit()
        self.history_num.setFixedWidth(200)
        self.history_num.setReadOnly(True)
        self.history_num.setFont(font)

        hbox4.addWidget(cur_num_label)
        hbox4.addWidget(self.cur_num)
        hbox4.addWidget(history_num_label)
        hbox4.addWidget(self.history_num)

        vbox.addLayout(hbox4)

        hbox5 = QHBoxLayout()
        hbox5.setAlignment(Qt.AlignCenter)

        # 消除播放过程中的黑边
        self.wgt_video1.setAspectRatioMode(
            Qt.AspectRatioMode.IgnoreAspectRatio)
        self.wgt_video1.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.wgt_video2.setAspectRatioMode(
            Qt.AspectRatioMode.IgnoreAspectRatio)
        self.wgt_video2.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_play()

        hbox5.addWidget(self.wgt_video1)
        hbox5.addWidget(self.wgt_video2)
        vbox.addLayout(hbox5)

        # 终端输出
        vbox.addWidget(self.output_text_edit)  # 输出文本框

        self.success_page.setLayout(vbox)

    def set_sample_interval(self):
        self.sample_interval = self.sample_interval_entry.text()
        print('当前的采样间隔为{}'.format(self.sample_interval))

    def set_video_play(self):
        # 以一定的时间间隔从源视频中采样，上传到服务器，进行计数
        if (self.main_file == '' or self.aux_file == ''):
            print('请先上传两个视角的源文件')
            return
        if self.sample_interval == '':
            print('请先设置采样间隔')
            return
        if int(self.sample_interval) == 0:
            print('请输入大于0的整数')
            return
        sample_interval = int(self.sample_interval)
        video_fps1, frame_count1 = vtool.get_info(self.main_file)
        video_fps2, frame_count2 = vtool.get_info(self.aux_file)
        sample_unit = self.sample_interval_unit.currentText()
        if sample_unit == '秒':
            frame_interval1 = sample_interval*video_fps1
            frame_interval2 = sample_interval*video_fps2
        elif sample_unit == '分钟':
            frame_interval1 = sample_interval*video_fps1*60
            frame_interval2 = sample_interval*video_fps1*60
        else:
            frame_interval1 = sample_interval
            frame_interval2 = sample_interval

        frame_interval1 = int(frame_interval1)
        frame_interval2 = int(frame_interval2)
        n1 = (frame_count1 - self.current_frame1 - 1)//frame_interval1
        n2 = (frame_count2 - self.current_frame2 - 1)//frame_interval2
        n = min(n1, n2)  # 还剩下n个采样周期
        start_frame1 = 0
        start_frame2 = 0
        self.video_path1 = 'sample_videos/main.mp4'
        self.video_path2 = 'sample_videos/aux.mp4'
        n_frames = self.sample_length_entry.text()
        n_frames = int(n_frames)
        for i in range(n):
            start_frame1 = self.current_frame1 + frame_interval1*i
            start_frame2 = self.current_frame2 + frame_interval2*i
            vtool.sample_video(src_video=self.main_file, dst_path='sample_videos/',
                               video_name='main_new.mp4', fps=15, n_frames=n_frames, start_frames=start_frame1)
            vtool.sample_video(src_video=self.aux_file, dst_path='sample_videos/',
                               video_name='aux_new.mp4', fps=15, n_frames=n_frames, start_frames=start_frame2)

            # 在两个视频之间切换播放
            self.upload_to_server()
            self.setup()
            if self.video_path1 == 'sample_videos/main.mp4':
                shutil.copy2('sample_videos/main_new.mp4',
                             'sample_videos/main_1.mp4')
                shutil.copy2('sample_videos/aux_new.mp4',
                             'sample_videos/aux_1.mp4')
                self.video_path1 = 'sample_videos/main_1.mp4'
                self.video_path2 = 'sample_videos/aux_1.mp4'
                self.set_duration()
                self.video_play()
            else:
                shutil.copy2('sample_videos/main_new.mp4',
                             'sample_videos/main.mp4')
                shutil.copy2('sample_videos/aux_new.mp4',
                             'sample_videos/aux.mp4')
                self.video_path1 = 'sample_videos/main.mp4'
                self.video_path2 = 'sample_videos/aux.mp4'
                self.set_duration()
                self.video_play()
        self.current_frame1 = start_frame1
        self.current_frame2 = start_frame2

    def set_duration(self):
        video_fps, frame_count = vtool.get_info(self.video_path1)
        self.duration1 = int(frame_count/video_fps * 1000)
        video_fps, frame_count = vtool.get_info(self.video_path2)
        self.duration2 = int(frame_count/video_fps * 1000)

    def video_play(self):
        # 播放视频（单次）
        video_path1 = self.video_path1
        self.player1 = QMediaPlayer()
        self.player1.setVideoOutput(self.wgt_video1)  # 视频输出的widget
        self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(video_path1)))
        self.player1.stateChanged.connect(self.handle_state_changed1)
        self.player1.play()

        video_path2 = self.video_path2
        self.player2 = QMediaPlayer()
        self.player2.setVideoOutput(self.wgt_video2)  # 视频输出的widget
        self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(video_path2)))
        self.player2.stateChanged.connect(self.handle_state_changed2)
        self.player2.play()

    def handle_state_changed1(self):
        # 判断是否到视频末尾了，但是这里的self.duration1不能每次都从main.mp4中读取，
        # 因为如果在还没有生成第二个视频时，视频就播放停止了，此时的帧数为0，会出现非法运算
        if self.player1.position() == self.duration1:
            self.player1.setPosition(0)
            self.player1.play()

    def handle_state_changed2(self):
        if self.player2.position() == self.duration1:
            self.player2.setPosition(0)
            self.player2.play()

    def set_failure_page(self):
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)

        # 返回按钮
        hbox1 = QHBoxLayout()
        hbox1.setAlignment(Qt.AlignCenter)
        back_button = QPushButton('返回')
        back_button.clicked.connect(self.switch_to_login)
        hbox1.addWidget(back_button)

        # 连接失败图片
        hbox2 = QHBoxLayout()
        hbox2.setAlignment(Qt.AlignCenter)
        failure_label = QLabel()
        pixmap = QPixmap("failure.png")
        scaled_pixmap = pixmap.scaled(200, 200, aspectRatioMode=True)
        failure_label.setPixmap(scaled_pixmap)
        hbox2.addWidget(failure_label)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.failure_page.setLayout(vbox)

    def switch_to_login(self):
        self.stacked_widget.setCurrentIndex(0)

    def switch_to_success(self):
        self.stacked_widget.setCurrentIndex(1)

    def switch_to_faliure(self):
        self.stacked_widget.setCurrentIndex(2)

    def get_screen_size(self):
        if len(QGuiApplication.screens()) > 1:
            screen2 = QGuiApplication.screens()[1]  # 第二屏幕
            screen2_size = screen2.availableGeometry()
            screen_width = screen2_size.width()
            screen_height = screen2_size.height()
        else:
            screen_width = QApplication.desktop().width()
            screen_height = QApplication.desktop().height()
        return screen_width, screen_height

    def login(self):
        # 获取输入值
        host = self.host_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        # 连接到远程服务器
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=username,
                           password=password, timeout=2)  # 超过2秒没有反应则认为连接失败
            client.close()
            print("登录成功")
            QApplication.processEvents()  # 强制刷新界面
            self.switch_to_success()
        except:
            self.switch_to_faliure()
            # self.switch_to_success()

    def upload_to_server(self):
        # main = self.video_path1
        # aux = self.video_path2
        main = 'sample_videos/main_new.mp4'
        aux = 'sample_videos/aux_new.mp4'
        # 创建SSH客户端对象
        client = paramiko.SSHClient()
        # 自动添加主机密钥
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接到远程服务器
        # try:
        client.connect(self.host_entry.text(), username=self.username_entry.text(),
                    password=self.password_entry.text())
        # 上传文件
        sftp = client.open_sftp()
        self.flag_main = False
        self.flag_aux = False

        sftp.put(
            main, '/home/asus/liucy/yxy_project/multiview/datasets/original/main.mp4')
        print('主视角视频上传成功')
        self.flag_main = True
        
        sftp.put(
            aux, '/home/asus/liucy/yxy_project/multiview/datasets/original/aux.mp4')
        print('辅视角视频上传成功')
        self.flag_aux = True
        try:
            sftp.put(
                main, '/home/asus/liucy/yxy_project/multiview/datasets/original/main.mp4')
            print('主视角视频上传成功')
            self.flag_main = True
        except:
            print('请检查主视角文件路径是否正确')
        try:
            sftp.put(
                aux, '/home/asus/liucy/yxy_project/multiview/datasets/original/aux.mp4')
            print('辅视角视频上传成功')
            self.flag_aux = True
        except:
            print('请检查辅视角文件路径是否正确')
        sftp.close()
        client.close()
        # except:
        #     self.upload_to_server()

    def setup(self):
        try:
            if self.flag_main & self.flag_aux:
                print('开始执行程序')
                # 创建SSH客户端对象
                client = paramiko.SSHClient()
                # 自动添加主机密钥
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # 连接到远程服务器
                client.connect(self.host_entry.text(), username=self.username_entry.text(),
                               password=self.password_entry.text())
                # 打开交互式shell会话
                shell = client.invoke_shell()
                # 执行命令
                shell.send('cd /home/asus/liucy/yxy_project/multiview\n')
                shell.send('source ~/.bashrc\n')
                shell.send('conda activate liucy\n')
                if self.device_button.isChecked():  # 使用GPU
                    shell.send('python detect.py\n')
                    shell.send('python test_mgn4.py\n')
                else:  # 使用CPU
                    shell.send('python detect_cpu.py\n')
                    shell.send('python test_mgn4_cpu.py\n')

                # 读取输出结果并实时刷新
                output = ''
                while 'β' not in output:  # 读取结束的标志
                    shell.settimeout(90)  # 保险起见，超时就断开
                    try:
                        output = shell.recv(1024).decode()
                        print(output)
                        QApplication.processEvents()  # 强制刷新界面
                    except:
                        print('执行超时，已退出')
                        break

                remote_file_path = '/home/asus/liucy/yxy_project/multiview/cur_people_num.txt'
                command = f'tail -n 1 {remote_file_path}'
                _, stdout, _ = client.exec_command(command)
                num = stdout.read().decode().strip()
                self.cur_num.setText(num)
                self.history_num.append(num+'人')  # 添加人数
                self.history_num.moveCursor(QTextCursor.End)  # 将光标置于最后

                client.close()
                print('程序已退出')
            else:
                print('请检查文件路径是否正确')
        except:
            print('请先上传文件')


if __name__ == '__main__':
    original_stdout = sys.stdout
    app = QApplication(sys.argv)
    application = Application()
    # 保存原始的sys.stdout对象
    original_stdout = sys.stdout
    # 重定向标准输出到QTextEdit
    sys.stdout = application
    # 在应用程序退出时恢复原始的sys.stdout对象
    app.aboutToQuit.connect(lambda: setattr(sys, 'stdout', original_stdout))
    sys.exit(app.exec_())
