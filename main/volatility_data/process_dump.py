import ctypes
import os
import psutil
from datetime import datetime

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04


class MEMORY_BASIC_INFORMATION64(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_uint64),
        ("AllocationBase", ctypes.c_uint64),
        ("AllocationProtect", ctypes.c_ulong),
        ("__alignment1", ctypes.c_ulong),
        ("RegionSize", ctypes.c_ulonglong),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
        ("__alignment2", ctypes.c_ulong),
    ]


OpenProcess = ctypes.windll.kernel32.OpenProcess
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
VirtualQueryEx = ctypes.windll.kernel32.VirtualQueryEx

# 추가 
current_path = os.getcwd()
artifact_path = os.path.join(current_path, "ARTIFACT")
system_log_path = os.path.join(artifact_path, "SYSTEM")
if not os.path.exists(system_log_path):
    os.makedirs(system_log_path)



def memory_dump(pid):
    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not process_handle:
        return f"Could not open process {pid}"

    base_address = ctypes.c_uint64(0)
    mbi = MEMORY_BASIC_INFORMATION64()

    while VirtualQueryEx(
        process_handle, base_address, ctypes.byref(mbi), ctypes.sizeof(mbi)
    ):
        if mbi.State == MEM_COMMIT and mbi.Protect == PAGE_READWRITE:
            buffer = ctypes.create_string_buffer(mbi.RegionSize)
            if ReadProcessMemory(
                process_handle,
                ctypes.c_uint64(mbi.BaseAddress),
                buffer,
                mbi.RegionSize,
                None,
            ):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                script_dir = os.path.dirname(
                    os.path.realpath(__file__)
                )  # 스크립트가 위치한 디렉토리
                print(
                    f"Current script directory: {script_dir}"
                )  # 스크립트 디렉토리 출력
                collector = system_log_path
                dump_dir = os.path.join(collector, "process_dump")
                if not os.path.exists(dump_dir):
                    os.makedirs(dump_dir, exist_ok=True)

                filename = os.path.join(dump_dir, f"process_dump_{pid}_{timestamp}.bin")
                try:
                    with open(filename, "wb") as f:
                        f.write(buffer.raw)
                except Exception as e:
                    print(
                        f"Error while writing the file: {e}, Location: {filename}"
                    )  # 예외 발생 시 정보 출력
            else:
                error_code = ctypes.GetLastError()
                return (
                    f"Could not read memory of process {pid}, error code: {error_code}"
                )
        base_address.value += mbi.RegionSize
    return f"dump_complete for process {pid}"


def run():
    results = {
        "Could not open process": [],
        "Could not read memory of process": [],
        "dump_complete": [],
    }
    for proc in psutil.process_iter(["pid", "name"]):
        result = memory_dump(proc.info["pid"])
        if "Could not open process" in result:
            results["Could not open process"].append(proc.info["name"])
        elif "Could not read memory of process" in result:
            results["Could not read memory of process"].append(proc.info["name"])
        else:
            results["dump_complete"].append(proc.info["name"])
    return results


run()