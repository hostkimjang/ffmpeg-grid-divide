import time
import ffmpeg
from tqdm import tqdm
import re
import json
import subprocess

def get_video_resolution(path):
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        path
    ]
    output_path = subprocess.check_output(command).decode("utf-8").strip()
    return list(map(int, output_path.split("x")))

def divide_video (original_path, output_path):
    print(f"파일 경로: {original_path}")
    print(f"출력 경로: {output_path}")
    print(f"영상을 타일별로 분리합니다")

    # command = [
    #     "ffmpeg",
    #     "-i", original_path,
    #     "-filter_complex", "[0:v]crop=iw/2:ih/2:0:0[tl];[0:v]crop=iw/2:ih/2:iw/2:0[tr];[0:v]crop=iw/2:ih/2:0:ih/2[bl];[0:v]crop=iw/2:ih/2:iw/2:ih/2[br]",
    #     "-progress", "-",  # 진행 상황을 표시하기 위한 옵션
    #     "-c:a", "copy",
    #     "-map", "[tl]",
    #     "-map", "0:a",
    #     "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션\
    #     "-preset", "fast",  # 인코딩 속도 옵션
    #     "-c:a", "copy",
    #     "-y", f"{output_path}/1.mp4",
    #     "-map", "[tr]",
    #     "-map", "0:a",
    #     "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
    #     "-preset", "fast",  # 인코딩 속도 옵션
    #     "-c:a", "copy",
    #     "-y", f"{output_path}/2.mp4",
    #     "-map", "[bl]",
    #     "-map", "0:a",
    #     "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
    #     "-preset", "fast",  # 인코딩 속도 옵션
    #     "-c:a", "copy",
    #     "-y", f"{output_path}/3.mp4",
    #     "-map", "[br]",
    #     "-map", "0:a",
    #     "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
    #     "-preset", "fast",  # 인코딩 속도 옵션
    #     "-c:a", "copy",
    #     "-y", f"{output_path}/4.mp4"
    # ]

    #[0,1,2,3]
    #[4,5,6,7]
    #[8,9,10,11]
    #[12,13,14,15]
    #로 나눠짐 타일

    iw, ih = get_video_resolution(original_path)
    w, h = iw // 4, ih // 4

    print(f"영상 해상도: {iw}x{ih}")
    print(f"타일 해상도: {w}x{h}")
    count = 0

    command = [
        "ffmpeg",
        "-i", original_path,
    ]

    filter_complex_str = ""
    for i in range(16):  # 모든 타일을 한 번에 처리
        print(f"출력 경로: {output_path}/{i}.mp4")
        filter_complex_str += f"[0:v]crop={w}:{h}:{w * (i % 4)}:{h * (i // 4)}[tile{i}];"

    command.append("-filter_complex")
    command.append(filter_complex_str[:-1])  # 마지막 세미콜론을 제거합니다.

    for i in range(16):  # 모든 타일을 한 번에 처리
        command.extend([
            "-map", f"[tile{i}]",
            "-progress", "-",  # 진행 상황을 표시하기 위한 옵션
            "-map", "0:a:0",  # 첫 번째 오디오 스트림을 지정'
            "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
            "-preset", "p5",  # 인코딩 속도 옵션
            "-b:v", "8M",
            "-tune", "hq",
            "-c:a", "copy",
            "-y", f"{output_path}/{i}.mp4"
        ])

    #subprocess.run(command)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    #tqdm 진행 표시줄을 초기화합니다.
    pbar = tqdm(total=None)
    for line in process.stdout:
       # 출력에서 "Duration: 00:00:30.04"와 같은 라인을 찾아서 전체 동영상 길이를 가져옵니다.
       if "Duration" in line:
           time_str = re.search("Duration: (.*?),", line).group(1)
           hours, minutes, seconds = map(float, re.split(':', time_str))
           total_seconds = hours*3600 + minutes*60 + seconds
           pbar.total = total_seconds
           pbar.refresh()
       # 출력에서 "time=00:00:10.00"과 같은 라인을 찾아서 현재 진행 시간을 가져옵니다.
       if "time=" in line:
           match = re.search("time=(.*?) ", line)
           if match is not None:
               time_str = match.group(1)
               hours, minutes, seconds = map(float, re.split(':', time_str))
               elapsed_seconds = hours * 3600 + minutes * 60 + seconds
               pbar.n = elapsed_seconds
               pbar.refresh()
    pbar.close()


    # 4개의 작업을 한 번에 처리하기 위한 반복문
   # for batch in range(0, 16, 4):
   #     command = [
   #         "ffmpeg",
   #         "-i", original_path,
   #     ]
#
   #     filter_complex_str = ""
#
   #     for i in range(16):  # 모든 타일을 한 번에 처리
   #         print(f"출력 경로: {output_path}/{i}.mp4")
   #         filter_complex_str += f"[0:v]crop={w}:{h}:{w * (i % 4)}:{h * (i // 4)}[tile{i}];"
#
   #     command.append("-filter_complex")
   #     command.append(filter_complex_str[:-1])  # 마지막 세미콜론을 제거합니다.
#
   #     for i in range(16):  # 모든 타일을 한 번에 처리
   #         command.extend([
   #             "-map", f"[tile{i}]",
   #             "-progress", "-",  # 진행 상황을 표시하기 위한 옵션
   #             "-map", "0:a:0",  # 첫 번째 오디오 스트림을 지정
   #             "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
   #             "-preset", "fast",  # 인코딩 속도 옵션
   #             "-c:a", "copy",
   #             "-y", f"{output_path}/{i}.mp4"
   #         ])
   #
   #     for i in range(4):  # 4개의 타일을 한 번에 처리
   #         tile_index = i + 4 * (batch // 4)
   #         print(f"출력 경로: {output_path}/{tile_index}.mp4")
   #         filter_complex_str += f"[0:v]crop={w}:{h}:{w * (tile_index % 4)}:{h * (tile_index // 4)}[tile{tile_index}];"
#
   #     command.append("-filter_complex")
   #     command.append(filter_complex_str[:-1])  # 마지막 세미콜론을 제거합니다.
#
   #     for i in range(4):  # 4개의 타일을 한 번에 처리
   #         tile_index = i + 4 * (batch // 4)
   #         command.extend([
   #             "-map", f"[tile{tile_index}]",
   #             "-progress", "-",  # 진행 상황을 표시하기 위한 옵션
   #             "-map", "0:a:0",  # 첫 번째 오디오 스트림을 지정
   #             "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
   #             "-preset", "fast",  # 인코딩 속도 옵션
   #             "-c:a", "copy",
   #             "-y", f"{output_path}/{tile_index}.mp4"
   #         ])

        # 프로세스를 시작하고, stdout을 파이프에 연결합니다.
        #subprocess.run(command)

        #process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        ## tqdm 진행 표시줄을 초기화합니다.
        #pbar = tqdm(total=None)
        #for line in process.stdout:
        #    # 출력에서 "Duration: 00:00:30.04"와 같은 라인을 찾아서 전체 동영상 길이를 가져옵니다.
        #    if "Duration" in line:
        #        time_str = re.search("Duration: (.*?),", line).group(1)
        #        hours, minutes, seconds = map(float, re.split(':', time_str))
        #        total_seconds = hours*3600 + minutes*60 + seconds
        #        pbar.total = total_seconds
        #        pbar.refresh()
        #    # 출력에서 "time=00:00:10.00"과 같은 라인을 찾아서 현재 진행 시간을 가져옵니다.
        #    if "time=" in line:
        #        match = re.search("time=(.*?) ", line)
        #        if match is not None:
        #            time_str = match.group(1)
        #            hours, minutes, seconds = map(float, re.split(':', time_str))
        #            elapsed_seconds = hours * 3600 + minutes * 60 + seconds
        #            pbar.n = elapsed_seconds
        #            pbar.refresh()
        #pbar.close()


    # 프로세스를 시작하고, stdout을 파이프에 연결합니다.

    # command = [
    #     "ffmpeg",
    #     "-i", original_path,
    #     "-progress", "-",  # 진행 상황을 표시하기 위한 옵션
    # ]
    #
    # print(f"타일별 영상을 추출합니다")
    # for i in range(4):
    #     for j in range(4):
    #         print(f"출력 경로: {output_path}/{i * 4 + j}.mp4")
    #         command_tile = command.copy()
    #         command_tile.extend([
    #             "-filter_complex", f"[0:v]crop={w}:{h}:{w * i % iw}:{h * j % ih}[tile{i * 4 + j}]",  # 타일별로 영상을 분리합니다.
    #             "-map", f"[tile{i * 4 + j}]",
    #             "-map", "0:a:0",  # 첫 번째 오디오 스트림을 지정
    #             "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
    #             "-preset", "fast",  # 인코딩 속도 옵션
    #             "-c:a", "copy",
    #             "-y", f"{output_path}-{i * 4 + j}.mp4"
    #         ])
    #
    #         # 프로세스를 시작하고, stdout을 파이프에 연결합니다.
    #         subprocess.run(command_tile)

            # # 프로세스를 시작하고, stdout을 파이프에 연결합니다.
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    #
    # # tqdm 진행 표시줄을 초기화합니다.
    # pbar = tqdm(total=None)
    #
    # for line in process.stdout:
    #     # 출력에서 "Duration: 00:00:30.04"와 같은 라인을 찾아서 전체 동영상 길이를 가져옵니다.
    #     if "Duration" in line:
    #         time_str = re.search("Duration: (.*?),", line).group(1)
    #         hours, minutes, seconds = map(float, re.split(':', time_str))
    #         total_seconds = hours*3600 + minutes*60 + seconds
    #         pbar.total = total_seconds
    #         pbar.refresh()
    #
    #     # 출력에서 "time=00:00:10.00"과 같은 라인을 찾아서 현재 진행 시간을 가져옵니다.
    #     if "time=" in line:
    #         match = re.search("time=(.*?) ", line)
    #         if match is not None:
    #             time_str = match.group(1)
    #             hours, minutes, seconds = map(float, re.split(':', time_str))
    #             elapsed_seconds = hours * 3600 + minutes * 60 + seconds
    #             pbar.n = elapsed_seconds
    #             pbar.refresh()
    #
    # pbar.close()



def mix_tile(tile_paths, output_path):
    #split_tiles = ([0,1,2,3],
    #               [4,5,6,7],
    #               [8,9,10,11],
    #               [12,13,14,15])
    #
    #original_recovery

    split_tiles = ([9,8,11,10],
                   [7,6,5,4],
                   [1,0,3,2],
                   [15,14,13,12])
    #mix_tiles
    #recovery


    print(f"타일 경로: {tile_paths}")
    print(f"출력 경로: {output_path}")
    print("타일을 원본 영상으로 복원합니다")

    command = [
        "ffmpeg",
    ]
    for row in split_tiles:
        for tile in row:
            tile_path = f"{tile_paths}/{tile}.mp4"
            print(f"타일 경로: {tile_path}")
            command.extend(["-i", tile_path])

    #filter_complex_str = "xstack=inputs=16:layout=0_0|0_h0|0_h0+h1|0_h0+h1+h2|w0_0|w0_h0|w0_h0+h1|w0_h0+h1+h2|w0+w4_0|w0+w4_h0|w0+w4_h0+h1|w0+w4_h0+h1+h2|w0+w4+w8_0|w0+w4+w8_h0|w0+w4+w8_h0+h1|w0+w4+w8_h0+h1+h2[v];"
    filter_complex_str = "xstack=inputs=16:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|0_h0|w0_h0|w0+w1_h0|w0+w1+w2_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1|w0+w1+w2_h0+h1|0_h0+h1+h2|w0_h0+h1+h2|w0+w1_h0+h1+h2|w0+w1+w2_h0+h1+h2[v];"

    for i in range(16):  # 16개의 타일을 하나로 결합
        filter_complex_str += f"[{i}:a]"

    filter_complex_str += "amix=inputs=16[a]"

    command.extend([
        "-filter_complex",
        filter_complex_str,
        "-progress", "-",  # 진행 상황을 표시하기 위한 옵션
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
        "-preset", "p5",  # 인코딩 속도 옵션
        "-b:v", "8M",
        "-tune", "hq",
        "-c:a", "aac",  # 오디오 코덱 설정
        "-y", output_path
    ])

    #subprocess.run(command)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # tqdm 진행 표시줄을 초기화합니다.
    pbar = tqdm(total=None)

    for line in process.stdout:
        # 'Duration'과 'out_time'을 찾아서 전체 동영상 길이와 현재 진행 시간을 가져옵니다.
        if "Duration" in line:
            time_str = re.search("Duration: (.*?),", line).group(1)
            hours, minutes, seconds = map(float, re.split(':', time_str))
            total_seconds = hours * 3600 + minutes * 60 + seconds
            pbar.total = total_seconds
            pbar.refresh()

        elif "time=" in line:
            match = re.search("time=(.*?) ", line)
            if match is not None:
                time_str = match.group(1)
                hours, minutes, seconds = map(float, re.split(':', time_str))
                elapsed_seconds = hours * 3600 + minutes * 60 + seconds
                pbar.n = elapsed_seconds
                pbar.refresh()
    pbar.close()

#https://ffmpeg.org/ffmpeg-filters.html#xstack #291.1 xstack


    # print(f"파일 경로: {divide_video_path}")
    # for i in mix_data:
    #     print(f"타일별 영상을 합성합니다: {i}")
    #
    # command = [
    #     "ffmpeg",
    #     "-i", f"{divide_video_path}/0.mp4",
    #     "-i", f"{divide_video_path}/1.mp4",
    #     "-i", f"{divide_video_path}/2.mp4",
    #     "-i", f"{divide_video_path}/3.mp4",
    #     "-i", f"{divide_video_path}/4.mp4",
    #     "-i", f"{divide_video_path}/5.mp4",
    #     "-i", f"{divide_video_path}/6.mp4",
    #     "-i", f"{divide_video_path}/7.mp4",
    #     "-i", f"{divide_video_path}/8.mp4",
    #     "-i", f"{divide_video_path}/9.mp4",
    #     "-i", f"{divide_video_path}/10.mp4",
    #     "-i", f"{divide_video_path}/11.mp4",
    #     "-i", f"{divide_video_path}/12.mp4",
    #     "-i", f"{divide_video_path}/13.mp4",
    #     "-i", f"{divide_video_path}/14.mp4",
    #     "-i", f"{divide_video_path}/15.mp4",
    #
    #     "-filter_complex", "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v][9:v][10:v][11:v][12:v][13:v][14:v]xstack=inputs=15:layout=0_0|w",
    #     "-progress", "-",  # 진행 상황을 표시하기 위한 옵션
    #     "-map", "[outv]",
    #     "-map", "0:a",
    #     "-c:v", "h264_nvenc",  # 하드웨어 가속 옵션
    #     "-preset", "fast",  # 인코딩 속도 옵션
    #     "-c:a", "copy",
    #     "-y", f"{divide_video_path}/combined.mp4"
    # ]
    #
    # subprocess.run(command)

    # 프로세스를 시작하고, stdout을 파이프에 연결합니다.
    #process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    #pbar = tqdm(total=None)

    #for line in process.stdout:
    #    # 출력에서 "Duration: 00:00:30.04"와 같은 라인을 찾아서 전체 동영상 길이를 가져옵니다.
    #    if "Duration" in line:
    #        time_str = re.search("Duration: (.*?),", line).group(1)
    #        hours, minutes, seconds = map(float, re.split(':', time_str))
    #        total_seconds = hours*3600 + minutes*60 + seconds
    #        pbar.total = total_seconds
    #        pbar.refresh()
    #
    #    # 출력에서 "time=00:00:10.00"과 같은 라인을 찾아서 현재 진행 시간을 가져옵니다.
    #    if "time=" in line:
    #        match = re.search("time=(.*?) ", line)
    #        if match is not None:
    #            time_str = match.group(1)
    #            hours, minutes, seconds = map(float, re.split(':', time_str))
    #            elapsed_seconds = hours * 3600 + minutes * 60 + seconds
    #            pbar.n = elapsed_seconds
    #            pbar.refresh()
    #pbar.close()



if __name__ == "__main__":
    video_path = "qhd output [v43OthTbbVA].webm"
    output_path = "./test-output"
    divide_video(video_path, output_path)
    mix_tile(output_path, "./test-output/combined.mp4")


