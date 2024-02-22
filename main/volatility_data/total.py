import pandas as pd
import importlib
import os

def run():
    # 실행하고자 하는 py 파일들의 목록
    py_files = [
        "clipboard_data",
        "device_connected_record",
        "first_act_process",
        "net_connections",
        "net_information",
        "process_name_id_handle",
        "process_pid_user_memory",
        "process-handle",
        "system_information",
        "time_information",
        "process_dump",  # 추가됨
    ]

    # 현재 스크립트 파일의 위치를 가져옴
    current_path = os.getcwd()
    artifact_path = os.path.join(current_path, "ARTIFACT")
    system_log_path = os.path.join(artifact_path, "SYSTEM")
    if not os.path.exists(system_log_path):
        os.makedirs(system_log_path)

    # 통합 데이터를 저장할 DataFrame 생성
    df_total = pd.DataFrame()

    # 각 py 파일을 하나씩 실행
    # 각 py 파일을 하나씩 실행
    for py_file in py_files:
        try:
            module = importlib.import_module(py_file)

            # 각 모듈에는 `run`이라는 함수가 있어야 하며, 그 결과를 가져와서 저장
            result = module.run()

            # 결과 데이터 형식에 따라 처리
            if isinstance(result, str):
                list_result = result.split(", ")
                df = pd.DataFrame(list_result)

            elif isinstance(result, list):
                df = pd.DataFrame(result)

            elif isinstance(result, dict):
                df = pd.DataFrame.from_dict(result, orient="index").reset_index()

            # DataFrame을 CSV 파일로 저장
            df.to_csv(os.path.join(system_log_path, f"{py_file}_results.csv"), index=False)

            # 통합본에 추가
            df_total = pd.concat([df_total, df])

        except Exception as e:
            print(f"An error occurred while running {py_file}: {e}")

    # 통합본을 CSV 파일로 저장
    try:
        df_total.to_csv(os.path.join(system_log_path, "total_results.csv"), index=False)
    except Exception as e:
        print(f"An error occurred while saving total_results.csv: {e}")
