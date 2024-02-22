import pyperclip


def run():
    # 클립보드에 있는 데이터를 가져옵니다.
    data = pyperclip.paste()
    
    print (data)
    return data
run()
