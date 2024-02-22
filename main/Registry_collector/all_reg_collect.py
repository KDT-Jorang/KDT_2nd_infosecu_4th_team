# 각 루트값에 어떤 것들이 있는지 모두 뽑아주는 코드
import winreg
import datetime
import os
import asyncio
import concurrent.futures
import json
import base64


root_key_names = {
    winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
    winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
    winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
    winreg.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG",
    winreg.HKEY_USERS: "HKEY_USERS"
}

def filetime_to_dt(ft):
    microseconds = (ft //10) % 1000000
    seconds = (ft // 10000000) - 11644473600
    dt = datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc)
    dt=  dt.replace(microsecond = microseconds)
    korea_timezone = datetime.timezone(datetime.timedelta(hours=9))
    dt_korea = dt.astimezone(korea_timezone)

    return dt_korea

all_results= []

def enumerate_values(hkey, subkey_path, full_path):
    try:
        with winreg.OpenKey(hkey, subkey_path) as subkey:
            _, _, last_modified = winreg.QueryInfoKey(subkey) 
            # winreg.QueryInfoKey 는 인자를 1번 : 서브키 갯수 /2번 : 값의 갯수 / 3번 : 마지막으로 수정된 시간으로 함.
            # 여기서 언더바(_) 는 인자를 무시하겠다는 말임. 
            index = 0
            while True:
                try:
                    value = winreg.EnumValue(subkey, index)
                    print(f"{full_path}\\{value[0]}: {value[1]}")
                    if isinstance(value[1],bytes):
                        try:
                            value_str = value[1].decode('utf-8')
                        except UnicodeDecodeError:
                            value_str = base64.b64encode(value[1]).decode('utf-8')
                    else:
                        value_str = value[1]
                    all_results.append({
                            "p": full_path,
                            "k": value[0],
                            "v": value_str,
                            "last_modified": str(filetime_to_dt(last_modified))
                        })
                    """ print(f"마지막 수정 시간: {filetime_to_dt(last_modified)}") """
                    index += 1
                except OSError:
                    break
            
    except PermissionError:
        print(f"권한이 거부되었습니다: {full_path}")



def enumerate_keys(hkey, subkey_path="", root_key_name=''):
    full_path = f"{root_key_name}\\{subkey_path}".strip("\\")
    
    try:
        with winreg.OpenKey(hkey, subkey_path) as subkey:
            _, _, last_modified = winreg.QueryInfoKey(subkey)
            try:
                value, _ = winreg.QueryValueEx(subkey, "")
                #all_results.append(f"{full_path}:{value}\n")
            except FileNotFoundError:
                pass
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(subkey, index)
                    next_subkey_path = f"{subkey_path}\\{subkey_name}" if subkey_path else subkey_name
                    next_full_path = f"{full_path}\\{subkey_name}"
                    enumerate_values(hkey, next_subkey_path, next_full_path)
                    enumerate_keys(hkey, next_subkey_path, root_key_name)
                    print(f"마지막 수정 시간: {filetime_to_dt(last_modified)}")
                    index += 1
                except OSError:
                    break
            
    except PermissionError:
        print(f"권한이 거부되었습니다: {full_path}")

def save_results_to_file():
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'registry_artifact.jsonl')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for result in all_results:
            json.dump(result, file)  # 딕셔너리를 JSON 문자열로 변환하여 파일에 씁니다.
            file.write('\n')

async def run_registry_collection(root_key, root_key_name):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(
            pool,
            lambda: enumerate_keys(root_key, '', root_key_name)
        )
        print(f'{root_key_name} 작업 완료')


# 루트 키의 이름을 얻어옵니다.
async def main():
    # 각 루트 키별로 비동기 작업 실행
    await asyncio.gather(
        run_registry_collection(winreg.HKEY_CLASSES_ROOT, "HKEY_CLASSES_ROOT"),
        run_registry_collection(winreg.HKEY_CURRENT_USER, "HKEY_CURRENT_USER"),
        run_registry_collection(winreg.HKEY_LOCAL_MACHINE, "HKEY_LOCAL_MACHINE"),
        run_registry_collection(winreg.HKEY_USERS, "HKEY_USERS"),
        run_registry_collection(winreg.HKEY_CURRENT_CONFIG, "HKEY_CURRENT_CONFIG")
    )
    save_results_to_file()
if __name__ == "__main__":
    asyncio.run(main())
