import os
import subprocess
import psutil


def run():
    # 실행 중인 모든 프로세스에 대한 정보를 가져오는 코드
    results = []
    for proc in psutil.process_iter(
        ["pid", "name", "username", "memory_info", "cpu_percent"]
    ):
        result = {}
        # 프로세스 정보 저장
        result["이미지 이름"] = proc.info["name"]
        result["PID"] = proc.info["pid"]
        result["사용자 이름"] = proc.info["username"]
        result["메모리 사용량"] = proc.info["memory_info"].rss / 1024 / 1024
        result["CPU 점유율"] = proc.info["cpu_percent"]

        # 프로세스 ID를 입력합니다.
        pid = str(proc.info["pid"])

        # 'tasklist' 명령을 이용하여 DLL 목록을 가져옵니다.
        output = subprocess.check_output(
            'tasklist /m /fi "PID eq %s"' % pid, shell=True
        )

        # 결과를 저장합니다. 'cp949' 코덱을 사용하여 디코딩합니다.
        result["로드된 DLL 목록"] = output.decode("cp949")

        # 프로세스가 열고 있는 파일 목록을 저장합니다.
        try:
            open_files = proc.open_files()
            if open_files:
                result["열린 파일 목록"] = [f.path for f in open_files]
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue

        results.append(result)
    return results
