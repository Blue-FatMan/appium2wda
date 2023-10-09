#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
import base64


def encode_file(file):
    with open(file, 'rb') as f:
        data = f.read()
        # 将图片文件内容编码为base64字符串
        base64_data = base64.b64encode(data).decode()
        return base64_data


# https://www.jianshu.com/p/77468f12a192
class ScreenRecord(object):

    def __init__(self):
        self._running = False # 记录是否正在录屏，为了给多次录屏做判断
        self.run_p = None  # 记录当前录制的的进程p
        self.current_tmp_storage = None  # 记录当前正在录制的文件存储路径

        self.ffmpeg_execute = None
        self.__check_ffmpeg()

    def __check_ffmpeg(self):
        ffmpeg_execute = shutil.which("ffmpeg")
        if not ffmpeg_execute:
            raise RuntimeError(
                "Can not found ffmpeg.exe in your System environment variables, please use pip install tidevice")
        self.ffmpeg_execute = ffmpeg_execute

    def check_timelimit(self, timeLimit):
        start_time = time.time()
        while time.time() - start_time <= timeLimit:
            if not self._running:
                return
        self.stop_recording_screen()

    def __run(self, timeLimit, cmd):
        # 得到一个临时文件对象， 调用close后，此文件从磁盘删除
        out_temp = tempfile.TemporaryFile(mode='w+')
        # 获取临时文件的文件号
        file_tmp = out_temp.fileno()
        # print(cmd)
        self.run_p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=file_tmp, stderr=file_tmp)
        self._running = True
        self.check_stop_record_thread = threading.Thread(
            target=self.check_timelimit, daemon=False, args=(timeLimit,)
        )
        self.check_stop_record_thread.start()

    def start_recording_screen(self, **options):
        """Start asynchronous screen recording process.
        Keyword Args:
            timeLimit (int): The actual time limit of the recorded video in seconds.
                The default value for both iOS and Android is 180 seconds (3 minutes).
                The maximum value for Android is 6 minutes.
                如果超过了maxmum，则程序自动停止录制，并且不返回任何值

            videoType (str): [iOS only] The format of the screen capture to be recorded.
                Available formats: Execute `ffmpeg -codecs` in the terminal to see the list of supported video codecs.
                'mjpeg' by default. (Since Appium 1.10.0),current only support mpeg4

            mjpegServerPort (int): mjpegServerPort
        Returns:
            bytes: Base-64 encoded content of the recorded media file or an empty string

        use exp:
        payload = self.driver.start_recording_screen(videoType='mpeg4', timeLimit=600)
        if payload:
            with open("test.mp4", "wb") as fd:
                fd.write(base64.b64decode(payload))

        """
        old_data = False
        timeLimit = options.get("timeLimit", 180)
        mjpegServerPort = options.get("mjpegServerPort", None)

        if not isinstance(timeLimit, int):
            raise ValueError("the timeLimit only support int type value")
        if not isinstance(mjpegServerPort, int):
            raise ValueError("the mjpegServerPort only support int type value")

        if "videoType" in options:
            if options["videoType"] != "mpeg4":
                raise ValueError("the videoType value error, only support mpeg4")
        timeLimit = min(60*6, timeLimit)

        if self._running:
            old_data = self.stop_recording_screen()

        video_stream_url = f"http://127.0.0.1:{mjpegServerPort}"
        self.current_tmp_storage = f"{str(uuid.uuid4())}.mp4"
        cmd = f"{self.ffmpeg_execute} -f mjpeg -r 10 -i {video_stream_url} -vcodec mpeg4 -y {self.current_tmp_storage}"
        self.__run(timeLimit=timeLimit, cmd=cmd)

        return old_data

    def stop_recording_screen(self, **options):
        """Gather the output from the previously started screen recording to a media file.
        Returns:
            bytes:Base-64 encoded content of the recorded media file or an empty string
                if the file has been successfully uploaded to a remote location
                (depends on the actual `remotePath` value).

        use exp:
        payload = self.driver.stop_recording_screen()
        with open("test.mp4", "wb") as fd:
            fd.write(base64.b64decode(payload))
        """
        self.run_p.communicate("q".encode("GBK"))
        self.run_p.kill()
        self._running = False
        data = encode_file(self.current_tmp_storage)
        os.remove(self.current_tmp_storage)
        return data
