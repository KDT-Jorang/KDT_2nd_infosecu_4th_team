import os
import subprocess
import shutil
import win32evtlog



    # 이벤트 로그 수집
class EventLogCollector:
    def __init__(self, result_path, system_root, version, UTC):
        self.result_path = result_path
        self.system_root = system_root
        self.version = version
        self.UTC = UTC

    def collect_logs(self):
        artifact_path = self.get_artifact_path()
        event_logs = []

        if artifact_path:
            self.collect(artifact_path)
            print("Collecting Eventlogs complete.")
        
        else:
            print("Unable to determine artifact path for the given Windows version.")
        
        return event_logs

    #WINDOWS 버전별 파일경로 반환
    def get_artifact_path(self):
        if "Windows 10" in self.version or "Windows 8" in self.version or "Windows 7" in self.version:
            return os.path.join(self.system_root, "System32", "winevt", "Logs")
        
        elif "Windows XP" in self.version:
            return os.path.join(self.system_root, "system32", "config")
        
        else:
            return None

    def collect(self, artifact_path):
        if "Windows 7" in self.version or "Windows 8" in self.version or "Windows 10" in self.version:
            event_logs = self.extract_logs(["Application", "System", "Security", "Setup"]) # 주요 로그 파일 추출
            for log in event_logs:
                print(log)
        
        elif "Windows XP" in self.version:
            output_file = os.path.join(self.result_path, "WindowsXP_EventLogs.csv")
            command = f"eventquery.vbs /l /v > {output_file}"
            subprocess.run(command, shell=True)
        
        else:
            print("Unsupported Windows version for collecting Eventlogs.")


    # 이벤트 로그 추출 - 주요 로그 파일을 log_names로 차례대로 돌려가며 반환받음
    def extract_logs(self, log_names):
        event_logs = []
        for log_name in log_names:
            hand = win32evtlog.OpenEventLog(None, log_name)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            total = win32evtlog.GetNumberOfEventLogRecords(hand)
            events = win32evtlog.ReadEventLog(hand, flags, 0)
        
            for event in events:
                event_num = event.RecordNumber  # 이벤트별 Record 번호
                event_id = event.EventID & 0x1FFFFFFF # 이벤트 ID 
                event_time = event.TimeGenerated.Format()  # 이벤트 생성 시간
                event_level = self.get_event_level(event.EventType)  # 이벤트 레벨
                event_user = event.Sid  # 보안 사용자 ID
                event_channel = event.ComputerName # 이벤트 채널
                event_Source = event.SourceName  # 공급자 이름

            
                # 이벤트 정보를 배열에 저장
                event_info = {
                    'Record No.' : event_num,
                    'Level': event_level,
                    'Generated Time': event_time,
                    'Event ID': event_id,
                    'Source': event_Source,
                    'User ID': event_user,
                    'Channel': event_channel,

                }
                event_logs.append(event_info)
            
            win32evtlog.CloseEventLog(hand)
            
            if event_logs:
                self.event_log_save(event_logs)
        return event_logs
    
    def event_log_save(self, event_logs):
        file_name = 'eventlog_info.txt'
        artifact_path = './ARTIFACT/EVENT_LOG'
    
        if not os.path.exists(artifact_path):
            os.makedirs(artifact_path)
        
        file_path = os.path.join(artifact_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            for event in event_logs:
                for key, value in event.items():
                    file.write(f"{key}: {value}")
                    file.write("\n")  # 각 이벤트 사이에 공백 줄 추가
            print('이벤트 로그 정보가 현재 폴더에 저장되었습니다.')

    #Level 속성 출력 형식 변환
    def get_event_level(self, event_level):
        if event_level == win32evtlog.EVENTLOG_INFORMATION_TYPE:
            return 'Information'    
        elif event_level == win32evtlog.EVENTLOG_WARNING_TYPE:
            return 'Warning'
        elif event_level == win32evtlog.EVENTLOG_ERROR_TYPE:
            return 'Error'
        elif event_level == win32evtlog.EVENTLOG_AUDIT_SUCCESS:
            return 'Audit Success'
        elif event_level == win32evtlog.EVENTLOG_AUDIT_FAILURE:
            return 'Audit Failure'
        elif event_level == win32evtlog.EVENTLOG_SUCCESS:
            return 'Success'
        else:
            return 'Unknown'
    



    # Windows7~ 이벤트 로그 출력
#if __name__ == "__main__":
 #   collector = EventLogCollector(result_path="C:\\Windows\\Users", system_root="C:\\Windows", version="Windows 7,8,10", UTC=9)
  #  collector.collect_logs()
