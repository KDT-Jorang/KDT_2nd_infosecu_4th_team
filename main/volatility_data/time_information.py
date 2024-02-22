from datetime import datetime
import pytz
import os
import psutil


def run():
    # Create a dictionary to store all the information
    time_info = {}

    # 로그인 사용자 이름
    username = os.getlogin()
    time_info["사용자 이름"] = username

    # 현재 시간을 가져옵니다.
    now_local = datetime.now(
        pytz.timezone("Asia/Seoul")
    )  # 이 부분은 사용자의 시간대에 따라 변경
    time_info["현재 시간"] = str(now_local)

    # 현재 시간을 UTC(협정 세계시)로 변환합니다.
    now_utc = now_local.astimezone(pytz.timezone("UTC"))
    time_info["UTC 시간"] = str(now_utc)

    # 시스템 부팅 시간
    boot_time = psutil.boot_time()
    boot_time_datetime = datetime.fromtimestamp(boot_time)
    time_info["부팅 시간"] = boot_time_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # 시스템이 부팅된 시간(현재까지)
    uptime = datetime.now() - boot_time_datetime
    time_info["시스템이 부팅된 시간"] = str(uptime)

    # 현재 시스템에 로그인한 사용자의 정보를 가져옵니다.
    users = psutil.users()

    # 사용자 정보를 출력합니다.
    user_info = []
    for user in users:
        # Unix timestamp를 datetime 객체로 변환합니다.
        start_time = datetime.fromtimestamp(user.started)
        # datetime 객체를 년/월/일/시/분/초 형태의 문자열로 변환합니다.
        start_time_str = start_time.strftime("%Y/%m/%d %H:%M:%S")
        user_info.append(
            {
                "User": user.name,
                "Terminal": user.terminal,
                "Host": user.host,
                "Started": start_time_str,
            }
        )
    time_info["사용자 정보"] = user_info

    return time_info


if __name__ == "__main__":
    # Get all time information
    print(run())
