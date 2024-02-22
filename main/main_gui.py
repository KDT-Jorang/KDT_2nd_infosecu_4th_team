from PyQt5 import QtCore, QtGui, QtWidgets
from UI import tableUI, mainUI, browserUI, caseUI
from Collect import BA_Collect
import gui_tk
import 쪼랭이
import volatility_reg
#import system_all_collector
import eventlog
from NTFS import NTFS_collect
import csv
import os
import sys
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QProgressDialog
from volatility_data import GUI, sys_collector
import asyncio
from PyQt5.QtWidgets import QApplication
import qasync
import asyncio

histroy_path = './ARTIFACT/Browser/HISTORY'

last_search = [-1, -1, None]

save_path = ""

########## 저장 경로 설정  #############
current_path = os.getcwd()
artifact_path = os.path.join(current_path, "ARTIFACT")
event_log_path = os.path.join(artifact_path, "EVENT_LOG")
registry_log_path = os.path.join(artifact_path, "REGISTRY")
browser_log_path = os.path.join(artifact_path, "Browser")
system_log_path = os.path.join(artifact_path, "SYSTEM")
if not os.path.exists(artifact_path):
    os.makedirs(artifact_path)
if not os.path.exists(event_log_path):
    os.makedirs(event_log_path)
if not os.path.exists(registry_log_path):
    os.makedirs(registry_log_path)
if not os.path.exists(browser_log_path):
    os.makedirs(browser_log_path)
if not os.path.exists(system_log_path):
    os.makedirs(system_log_path)
########## 저장 경로 설정  #############


class caseWindow():
    def __init__(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = caseUI.Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.ui.pushButton.clicked.connect(self.new)
        self.ui.pushButton_2.clicked.connect(self.load)
        
    def new(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        if(path == ""):
            return
        case_file = open(f"{path}\\caseInfo",'w')
        case_name = self.ui.lineEdit.text()
        case_auth = self.ui.lineEdit_2.text()
        case_time = datetime.now()
        case_file.writelines(f'{case_name}\n')
        case_file.write(f'{case_auth}\n')
        case_file.write(f'{case_time}')
        global save_path
        save_path = path
        self.showMain(case_name, case_auth, case_time)
        
    def load(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        self.msg = QtWidgets.QMessageBox()
        if(path == ""):
            return
        if not os.path.exists(f"{path}\\caseInfo"):
            self.msg.setWindowTitle("ERROR")
            self.msg.setText(f"케이스가 저장된 폴더가 아닙니다.")
            self.msg.exec_()
            return
        case_file = open(f"{path}\\caseInfo",'r')
        case_line = case_file.read()
        case_line = case_line.splitlines()
        case_name = case_line[0]
        case_auth = case_line[1]
        case_time = case_line[2]
        global save_path
        save_path = path
        self.showMain(case_name, case_auth, case_time)
        
    def showMain(self, name, auth, time):
        self.window.close()
        self.main = mainWindow()
        self.main.ui.lineEdit.setText(name)
        self.main.ui.lineEdit_2.setText(auth)
        self.main.ui.lineEdit_3.setText(str(time))
        self.main.window.show()


class NTFSWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def run(self):
        try:
            NTFS_collect.ggachi()
        except Exception as e:
            print(f"Error in NTFS collection: {e}")
        finally:
            self.finished.emit()


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.window = QtWidgets.QMainWindow()
        self.ui = mainUI.Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.ui.pushButton_4.clicked.connect(self.showBrowser)
        self.ui.pushButton_2.clicked.connect(gui_tk.show)
        self.ui.pushButton.clicked.connect(self.registrycollect)
        self.ui.pushButton_5.clicked.connect(self.NTFSCOLLECT)
        self.ui.pushButton_3.clicked.connect(self.showSystem)  # 추가
        self.ui.pushButton_6.clicked.connect(self.button_6_clicked) # 추가
        
    # 비동기 작업 함수
    async def runALLtasks(self):
        tasks = [
            self.browser_collect(),
            self.reg_collect(),
            self.ntfs_collector(),
            self.evtlog_collect(),
            #self.all_system_artifact()
        ]
        await asyncio.gather(*tasks)    
    
    # 버튼 상호작용 함수
    def button_6_clicked(self):
        asyncio.create_task(self.runALLtasks())

    # 비동기 브라우저 탐색
    async def browser_collect(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, collect_history)
        await loop.run_in_executor(None, BA_Collect.get_cache, "Chrome")

    """ # 비동기 모든 레지스트리 탐색 # 이 함수는 위, 아래 다른 함수와 다르게 비동기 함수이기 때문에 get_running_loop할 필요가 없다. 
    async def reg_collect(self):    # 왜냐면 이 메서드는 지금 진행중인 이벤트 루프를 쓰겠다는 표시인데 처음부터 비동기인 함수를 비동기로 호출한다면 
        await all_reg_collect.main() # await으로 충분히 지금 사용중인 이벤트 루프를 탈 수 있기 때문이다. """   
    
    # 비동기 필수 레지스트리 탐색
    async def reg_collect(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, volatility_reg.volatility_reg_collect)                                   


    ## 여기 진봉님 코드 추가해야 됨. #####
    async def all_system_artifact(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, sys_collector.run())
    
    # 비동기 ntfs
    async def ntfs_collector(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, NTFS_collect.ggachi)
    
    # 비동기 이벤트로그
    async def evtlog_collect(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, gui_tk.show)



    def eventlog_collect():
        gui_tk.show

    def showBrowser(self):
        self.browser = browserWindow()
        self.browser.window.show()

    def registrycollect(self):
        쪼랭이.durumi()

    def NTFSCOLLECT(self):
        # 프로그레스 다이얼로그 생성 및 표시
        self.progressDialog = QProgressDialog(
            "NTFS 정보를 수집 중입니다...\n " " \n수집된 파일은 현재 실행중인 폴더에 저장됩니다.",
            "취소",
            0,
            0,
            self.window,
        )
        self.progressDialog.setCancelButton(None)
        self.progressDialog.setWindowModality(QtCore.Qt.WindowModal)
        # 윈도우나 다이얼로그가 다른 ui 요소와 상호작용하는 방식을 정의함.
        # QtCore.Qt.WindowModal은 다른 윈도우와 상호작용하는 것을 제한한다는 의미
        self.progressDialog.show()
        self.startNTFSThread()

    def startNTFSThread(self):
        self.thread = QtCore.QThread()
        self.worker = NTFSWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(
            self.progressDialog.close
        )  # 작업 완료 시 프로그레스 다이얼로그 닫기
        self.thread.start()

    def showSystem(self):  # 추가
        self.system = GUI.MainWindow()
        self.system.show()



class browserWindow:
    def __init__(self):
        self.window = QtWidgets.QMainWindow()  # 새 창을 구성한다.
        self.ui = browserUI.Ui_MainWindow()  # 클래스를 사용하여 이 윈도우의 UI를 구성한다.
        self.ui.setupUi(self.window)  # self.ui = ui 클래스에서 정의된 모든 ui 요소를 실제 생성 인자에 배치한다.
        # setupUi = 모든 ui 요소를 실제로 생성하고 주어진 윈도우에 배치한다. 또한 이벤트와 핸들로를 연결하는데 사용. 윈도우 창의 느낌과 외관을 설정해줌.
        self.ui.pushButton.clicked.connect(self.showHistory)  # history
        self.ui.pushButton_2.clicked.connect(self.showDownload)  # Download
        self.ui.pushButton_3.clicked.connect(self.collect_cache)  # cache

    def showDownload(self):
        collect_history()
        self.table_window = tableWindow()
        self.table_window.setDownload()
        self.table_window.window.show()

    def showHistory(self):
        collect_history()
        self.table_window = tableWindow()
        self.table_window.setHistory()
        self.table_window.window.show()

    def collect_cache(self):
        browsers = ["Edge", "Chrome", "Firefox"]
        for browser in browsers:
            BA_Collect.get_cache(browser)
            
        csv_file = open(f"{save_path}\\fileinfo.csv",'w', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["이름", "수정시간", "접근시간", "생성시간", "해시(MD5)", "파일 크기", "파일 경로"])
        for file in BA_Collect.file_infos:
            csv_writer.writerow([file.name, file.mtime, file.atime, file.ctime, file.hash, file.filesize, file.filepath])
            
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Done")
        self.msg.setText(f"Jobs Done")
        self.msg.exec_()
        
        
    
class tableWindow:
    def __init__(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = tableUI.Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.ui.pushButton.clicked.connect(self.search)
        self.ui.pushButton_2.clicked.connect(self.save)
        self.type = ""

    def setHistory(self):
        self.ui.tableWidget = table_create(self.ui.tableWidget, "history")
        self.type = "history"

    def setDownload(self):
        self.ui.tableWidget = table_create(self.ui.tableWidget, "download")
        self.type = "download"

    def save(self):
        try:
            row_count = self.ui.tableWidget.rowCount()
            col_count = self.ui.tableWidget.columnCount()
            if row_count == 0:
                return

            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.ui.tableWidget,
                "파일 저장",
                f"{self.type}_list.csv",
                "csv Files (*.csv)",
            )
            if fileName:
                csv_file = open(fileName, "w", newline="", encoding="utf-8")
                csv_writer = csv.writer(csv_file)
            else:
                return

            if self.type == "history":
                csv_writer.writerow(
                    [
                        "URL",
                        "Title",
                        "Visit Time",
                        "Visit Count",
                        "Web Browser",
                        "Profile",
                    ]
                )
            elif self.type == "download":
                csv_writer.writerow(
                    [
                        "File Name",
                        "Download URL",
                        "Web URL",
                        "Start Time",
                        "End Time",
                        "File Size",
                        "Browser",
                        "Profile",
                        "File Full Path",
                    ]
                )

            for row in range(0, row_count):
                tmp_row = []
                for column in range(col_count):
                    cell_item = self.ui.tableWidget.item(row, column)
                    cell_text = cell_item.text()
                    tmp_row.append(cell_text)
                csv_writer.writerow(tmp_row)

            self.msg = QtWidgets.QMessageBox()
            self.msg.setWindowTitle("SAVE")
            self.msg.setText(f"Save Success!")

            self.msg.exec_()
        except Exception as e:
            print(f"tableWindow.save() : {e}")
    
    def search(self):
        text = self.ui.textEdit.toPlainText()
        table = table_create(self.ui.tableWidget, table_type=self.type)
        row_count = table.rowCount()
        col_count = table.columnCount()
        rows = []
        matched = False
        for row in range(0, row_count):
            if matched:
                rows.append(tmp_row)
            tmp_row = []
            matched = False
            for column in range(col_count):
                cell_item = table.item(row, column)
                cell_text = cell_item.text()
                tmp_row.append(cell_text)
                if text in cell_text:
                    matched = True
                else:
                    continue

        if rows == []:
            self.ui.tableWidget.setColumnCount(0)
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.update()
            return

        row_count = len(rows[0])
        col_count = len(rows) - 1

        # 테이블 열과 행 생성
        self.ui.tableWidget.setColumnCount(row_count)
        self.ui.tableWidget.setRowCount(col_count)

        if self.type == "history":
            rows = sorted(rows, key=lambda x: x[2])  # 방문 날짜를 기준으로 정렬
        elif self.type == "download":
            rows = sorted(rows, key=lambda x: x[3])

        col_count = 0
        for row in rows:
            for i in range(row_count):
                item = QtWidgets.QTableWidgetItem(str(row[i]))
                self.ui.tableWidget.setItem(col_count, i, item)
            col_count += 1
        self.ui.tableWidget.update()


def table_create(table, table_type="history"):
    if table_type == "history":
        rows = [["URL", "Title", "Visit Time", "Visit Count", "Web Browser", "Profile"]]
    elif table_type == "download":
        rows = [
            [
                "File Name",
                "Download URL",
                "Web URL",
                "Start Time",
                "End Time",
                "File Size",
                "Browser",
                "Profile",
                "File Full Path",
            ]
        ]
    else:
        print(f"table_create() : only input type history or download")

    files = os.listdir(histroy_path)
    for file in files:
        if table_type == "history":
            chrome_rows = BA_Collect.read_history(histroy_path + "\\" + file)
        elif table_type == "download":
            chrome_rows = BA_Collect.read_download(histroy_path + "\\" + file)
        if chrome_rows:
            rows.extend(chrome_rows)

    # 모든 파일 검사 실패
    if rows == []:
        return table

    row_count = len(rows[0])
    col_count = len(rows) - 1

    # 테이블 열과 행 생성
    table.setColumnCount(row_count)
    table.setHorizontalHeaderLabels(rows[0])  # 테이블 열 헤더 변경
    header = table.horizontalHeader()
    header.setStyleSheet(
        "QHeaderView::section { background-color:gray; color: black; font-weight: bold; }"
    )
    table.setStyleSheet(
        "QTableView::item:focus { background-color: yellow; color: black }"
    )
    table.setRowCount(col_count)

    del rows[0]

    rows = sorted(rows, key=lambda x: x[2])  # 방문 날짜를 기준으로 정렬

    col_count = 0
    for row in rows:
        for i in range(row_count):
            item = QtWidgets.QTableWidgetItem(str(row[i]))
            table.setItem(col_count, i, item)
        col_count += 1

    return table

def collect_history():
    browsers = ["Edge", "Chrome", "Firefox"]
    for browser in browsers:
        BA_Collect.get_history(browser)


async def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    case = caseWindow() # 케이스 창을 먼저 생성 후 메인 윈도우 창을 나오게 할 것이다.
    case.window.show()

    await loop.run_forever()  # 인스턴스에 대해 runALLtasks 메서드를 호출

if __name__ == "__main__":
    asyncio.run(main())
