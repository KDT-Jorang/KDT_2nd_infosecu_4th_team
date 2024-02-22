import os
import csv
import datetime
import shutil
import sqlite3
import json
import hashlib
import math    

# 원본 정보 담을 csv 파일 생성
file_infos = []

class file_info:
    def __init__(self):
        self.name = ""
        self.mtime = ""
        self.atime = ""
        self.ctime = ""
        self.hash = ""
        self.filesize = ""
        self.filepath = ""

# 파일 크기 사이즈에 맞춰서 변환
def convert_size(size_bytes):
    if size_bytes == 0:        
        return "0B"    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")  
    i = int(math.floor(math.log(size_bytes, 1024)))    
    p = math.pow(1024, i)    
    s = round(size_bytes / p, 2)    
    return "%s %s" % (s, size_name[i])

# 파일 해시 획득
def get_file_hash(path):
    f = open(path,'rb')
    data = f.read()
    hash = hashlib.md5(data).hexdigest()
    return hash

# 크롬 히스토리 파일 복사
def get_history(browser="Chrome"):
    try:
        if browser == "Chrome":
            path = f"{os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data"
        elif browser == "Edge":
            path = f"{os.path.expanduser('~')}\\AppData\\Local\\Microsoft\\Edge\\User Data"
        elif browser == "Firefox":
            path = f"{os.path.expanduser('~')}\\AppData\\Roaming\\Mozilla\\FireFox\\Profiles"
        else:
            print("Chrome or Edge or Firefox")
            return False
        
        # 파일 복사할 폴더 생성
        artifact_path = './ARTIFACT/Browser/HISTORY'
    
        if not os.path.exists(artifact_path):
            os.makedirs(artifact_path, exist_ok=True)
      
        
        # 해당 디렉토리 내 파일 탐색
        dirs = os.listdir(path)
        
        # 브라우저 별 검색 설정
        if (browser in ["Chrome", "Edge"]):
            dirs = list(filter(lambda x: "Profile " in x, dirs))
            dirs.append("Default")
            history_filename = "History"
        elif(browser in ["Firefox"]):
            history_filename = "places.sqlite"

        for dir in dirs:
            tmp_path = f"{path}\\{dir}\\{history_filename}"
            tmp_cp_path = f"{artifact_path}\\{browser}_{dir}_History"
            if not os.path.exists(tmp_path):
                print(f"{browser} : {tmp_path} 파일 탐색 실패")
                continue
            get_artifact(tmp_path, tmp_cp_path)
            
    except Exception :
        return False
     
def get_cache(browser="Chrome"):
    try:
        if browser in ["Chrome"]:
            path = f"{os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data"
        elif browser in ["Firefox"]:
            path = f"{os.path.expanduser('~')}\\AppData\\Local\\Mozilla\\FireFox\\Profiles"
        elif browser in ["Edge"]:
            path = f"{os.path.expanduser('~')}\\AppData\\Local\\Microsoft\\Edge\\User Data"
        else:
            print("Chrome or Edge or Firefox")
            return False
        
        # 브라우저 별 폴더 생성
        artifact_path = os.path.join('./ARTIFACT/Browser/CACHE/', browser)
        if not os.path.exists(artifact_path):
            os.makedirs(artifact_path, exist_ok=True)
        
        dirs = os.listdir(path)
        if (browser in ["Chrome", "Edge"]):
            dirs = list(filter(lambda x: "Profile " in x, dirs))
            dirs.append("Default")

        if (browser in ["Firefox"]):
            get_artifact_dirs(path, artifact_path)
        else:
            for dir in dirs:
                # 프로필 별 폴더 생성
                if not os.path.exists(f"{artifact_path}\\{dir}"):
                    os.mkdir(f"{artifact_path}\\{dir}")
                get_artifact_dirs(f"{path}\\{dir}\\Cache", f"{artifact_path}\\{dir}")
            
    except Exception as e:
        print(f"get_cache() : {e}")
        return False

# 경로에 있는 파일 복사후 원본 정보 저장
def get_artifact(org_path, cp_path):
    try:
        global file_infos
        # 원본 파일 정보 담을 클래스 생성
        origin_info = file_info()
        
        # 원본 파일 이름 확보
        origin_info.name = os.path.basename(org_path)
        
        # 원본 MAC 타임 확보
        origin_info.atime = datetime.datetime.fromtimestamp(os.path.getatime(org_path))
        origin_info.ctime = datetime.datetime.fromtimestamp(os.path.getctime(org_path))
        origin_info.mtime = datetime.datetime.fromtimestamp(os.path.getmtime(org_path))

        # 원본 파일 크기 확보
        origin_info.filesize = convert_size(os.path.getsize(org_path))
        
        # 원본 파일 해시 확보
        origin_info.hash = get_file_hash(org_path)
        
        # 원본 파일 경로 확보
        origin_info.filepath = org_path
        
        # 원본 파일 복사
        shutil.copyfile(org_path,cp_path)
        file_infos.append(origin_info)
        # csv_writer.writerow([origin_info.name, origin_info.mtime, origin_info.atime, origin_info.ctime, origin_info.hash, origin_info.filesize, origin_info.filepath])
        return True
    except Exception as e:
        print(f"get_artifact : {e}")
        return False

# 폴더 내부 폴더까지 확보
def get_artifact_dirs(org_path, cp_path):
    try:
        dirs = os.listdir(org_path)
        if dirs == []:
            return
        for dir in dirs:
            tmp_org = f"{org_path}\\{dir}"
            tmp_cp = f"{cp_path}\\{dir}"
            if os.path.isdir(tmp_org):
                if not os.path.exists(tmp_cp):
                    os.mkdir(tmp_cp)
                get_artifact_dirs(tmp_org, tmp_cp)
            else:
                get_artifact(tmp_org, tmp_cp)
        return
        
    except Exception as e:
        print(f"get_artifact_dirs() : {e}")

# 접속기록 읽는 함수
def read_history(path):
    try:
        # 파일명을 토대로 저장한 정보 획득
        file_info = os.path.basename(path)
        file_info = file_info.split("_") # 0 : 브라우저, 2 : 프로필, 3 : 파일이름
        browser = file_info[0]
        profile = file_info[1]
        
        # History DB 파일 연결
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        # chrome urls 테이블 컬럼 목록 : id, url, title, visit_count, typed_count, last_visit_time, hidden
        # chrome visits 테이블 컬럼 목록 : id, url, visit_time, from_visit, transition, segment_id, visit_duration
        # 크로미움 쿼리문
        chrome_query = "SELECT urls.url, urls.title, visits.visit_time, urls.visit_count FROM urls JOIN visits ON urls.id = visits.url"
        # 파이어폭스 쿼리문
        firefox_query = "SELECT moz_places.url, moz_places.title, moz_historyvisits.visit_date, moz_places.visit_count FROM moz_places JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id"
        
        if(browser in ['Chrome', 'Edge']):
            cursor.execute(chrome_query)
        elif 'Firefox' in browser:
            cursor.execute(firefox_query)
            
        history_data = []
        
        for row in cursor.fetchall():
            row = list(row)
            # Unix Epoch 타임스탬프 변환
            seconds_since_epoch = row[2] / 1000000.0
            if(browser in ['Chrome', 'Edge']):
                epoch_start = datetime.datetime(1601, 1, 1)
            elif browser in ['Firefox'] :
                epoch_start = datetime.datetime(1970, 1, 1)
            date_time = str(epoch_start + datetime.timedelta(hours=9,seconds=seconds_since_epoch)) # UTC+9 및 Epoch 시간 계산
            row[2] = date_time
            row.append(browser)
            row.append(profile)
            history_data.append(row)
        
        return history_data
    except Exception as e:
        print(f"read_history() : {e}")
        return False

# 다운로드 기록 불러들이는 함수
def read_download(path):
    try:
        # 파일명을 토대로 저장한 정보 획득
        file_info = os.path.basename(path)
        file_info = file_info.split("_") # 0 : 브라우저, 2 : 프로필, 3 : 파일이름
        browser = file_info[0]
        profile = file_info[1]
        
        # History DB 파일 연결
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        # 크로미움 쿼리문
        chrome_query = "SELECT downloads.current_path, downloads_url_chains.url, downloads.referrer, downloads.start_time, downloads.end_time, downloads.total_bytes FROM downloads JOIN downloads_url_chains ON downloads.id = downloads_url_chains.id"
        # 파이어폭스 쿼리문
        firefox_query = "SELECT A.content, P.url, A.dateAdded, A.lastModified FROM moz_annos A JOIN moz_places P ON A.place_id = p.id"
        
        history_data = []
        fox_row = []
        if(browser in ['Chrome', 'Edge']):
            cursor.execute(chrome_query)
            for row in cursor.fetchall():
                row = list(row)
                file_path = row[0]
                row[0] = os.path.basename(row[0])
                # Unix Epoch 타임스탬프 변환
                seconds_since_epoch_start = row[3] / 1000000.0
                seconds_since_epoch_end = row[4] / 1000000.0
                epoch_start = datetime.datetime(1601, 1, 1)
                date_time_start = str(epoch_start + datetime.timedelta(hours=9,seconds=seconds_since_epoch_start)) # UTC+9 및 Epoch 시간 계산
                date_time_end = str(epoch_start + datetime.timedelta(hours=9,seconds=seconds_since_epoch_end))
                row[3] = date_time_start # 타임스탬프 변환
                row[4] = date_time_end
                row.append(browser)
                row.append(profile)
                row.append(file_path)
                history_data.append(row)
        elif browser in ['Firefox']:
            cursor.execute(firefox_query)
            for row in cursor.fetchall():
                row = list(row)
                if 'fileSize' in row[0]:
                    dic = json.loads(row[0])
                    fox_row.append(dic['fileSize'])
                    fox_row.append(browser)
                    fox_row.append(profile)
                    fox_row.append(file_path)
                    history_data.append(fox_row)
                    continue
                fox_row = row
                file_path = fox_row[0]
                fox_row[0] = os.path.basename(row[0])
                fox_row.insert(2,"")
                seconds_since_epoch_start = fox_row[3] / 1000000.0
                seconds_since_epoch_end = fox_row[4] / 1000000.0
                epoch_start = datetime.datetime(1970, 1, 1)
                date_time_start = str(epoch_start + datetime.timedelta(hours=9,seconds=seconds_since_epoch_start)) # UTC+9 및 Epoch 시간 계산
                date_time_end = str(epoch_start + datetime.timedelta(hours=9,seconds=seconds_since_epoch_end))
                fox_row[3] = date_time_start
                fox_row[4] = date_time_end
            cursor.execute(firefox_query)
            
        return history_data
    except Exception as e:
        print(f"read_download() : {e}")
        return False

browsers = ['Edge','Chrome',"Firefox"]

# if __name__ == '__main__':
#     for browser in browsers:
#         get_cache(browser)
#         get_history(browser)