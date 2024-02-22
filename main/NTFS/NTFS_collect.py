import pytsk3
import sys
import os
import string
from ctypes import windll
""" import binascii """

class Extract_file:

    def __init__(self, volume_path):
        try:
            self.volume = '\\\\.\\' + volume_path # 시스템에 저수준으로 직접적 접근하기 위한 경로
            self.img = pytsk3.Img_Info(self.volume)  # 디스크 이미지 또는 물리적 드라이브의 정보를 나타내는 객체 생성
            self.fs = pytsk3.FS_Info(self.img) # Img_Info 객체로부터 파일 시스템 정보 추출

        except IOError as e:
            print(f"Error accessing volume: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def extract(self, filename, output_name):
        try:
            f = self.fs.open(filename)
            output_path = os.path.join(os.getcwd(), output_name) # getcwd = 현재 스크립트 파일의 경로를 기준으로 파일 저장 경로 설정
            with open(output_path, 'wb') as o:       #O를 참조로 하여 wb(이진쓰기) 모드로 파일을 연다.
                offset = 0
                size = f.info.meta.size
                while offset < size:
                    available_to_read = min(1024*1024, size - offset) # 최대 읽어들일 양을 지정함 -> 1024*1024 (= 1MB) 또는 size -offset 중 더 작은 값으로 설정한다
                    buf = f.read_random(offset, available_to_read)# 파일의 지정된 위치부터 데이터 읽기
                    if not buf:# 읽은 데이터가 없으면 파일 끝에 도달한 것이므로 루프 종료
                        break
                    # 읽은 데이터를 16진수 문자열로 변환하여 파일에 쓰기
                    """ hex_data = binascii.hexlify(buf).decode('utf-8') """
                    o.write(buf)
                    offset += len(buf) # 다음 읽을 위치로 오프셋 이동
            print(f"Extracted {filename} to {output_path}")
        except Exception as e:
            print(f"Error extracting {filename}: {e}")

    def extract_usnjrnl(self):
        try:
            f = self.fs.open('/$Extend/$UsnJrnl') # 경로에 해당하는 UsnJrnl 파일을 연다.
            found = False
            for attr in f:  #파일의 속성(attribute)을 확인하면서
                if attr.info.name == "$J":  # 속성 이름 J는 USN Journal의 시작 오프셋, 최대 크기, 현재 USN Journal 의 크기, 초과하면 처리된 방법 등의 정보를 갖는다.
                    found = True
                    break
            if not found:
                print("USN Journal not found.")
                return
            
            usnjrnl_path = os.path.join(os.getcwd(), '$UsnJrnl') # $UsnJrnl 저장할 파일의 경로를 설정
            with open(usnjrnl_path, 'wb') as o: #O를 참조로 하여 wb(이진쓰기) 모드로 파일을 연다.
                offset = 0
                size = attr.info.size # 파일 크기를 알기 위해 사용
                while offset < size: # 파일 끝까지 반복 
                    available_to_read = min(1024*1024, size - offset) # 최대 읽어들일 양을 지정함 -> 1024*1024 (= 1MB) 또는 size -offset 중 더 작은 값으로 설정한다
                    # 파일의 지정된 위치부터 데이터 읽기 (속성 정보 사용)
                    buf = f.read_random(offset, available_to_read, attr.info.type, attr.info.id)  # 오프셋부터 avail 까지 정보를 읽으면서 속성 type, 속성 id 정보를 읽는다.
                    if not buf:
                        break
                    """ hex_data = binascii.hexlify(buf).decode('utf-8') """
                    o.write(buf)
                    offset += len(buf)
            print("Extracted USN Journal.")
        except Exception as e:
            print(f"Error extracting USN Journal: {e}")

def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(f"{letter}: ")
        bitmask >>=1
    return drives

def extract_ntfs_info(volume):
    
    try:
        ext = Extract_file(volume)
        ext.extract('/$MFT', f'{volume[0]}_$MFT')
        ext.extract('/$LogFile', f'{volume[0]}_$LogFile')
        ext.extract_usnjrnl()
    except Exception as e:
        print(f"Error processing {volume}: {e}")


def ggachi():
    available_drives = get_drives()
    for drive in available_drives:
        extract_ntfs_info(drive)

if __name__ == '__main__':
    ggachi()

