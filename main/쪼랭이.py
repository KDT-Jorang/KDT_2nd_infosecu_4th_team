import sys   
import importlib
import io
from Registry_collector import *
from contextlib import redirect_stdout
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QAction, qApp, QToolBar,QFileDialog, QScrollArea, QGridLayout,QProgressDialog, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import winreg
import datetime


class all_registry_Worker(QtCore.QObject): # gui와 수집작업을 별도로 운영시키기 위해 생성한 클래스
    finished = QtCore.pyqtSignal() # 시그널로 종료를 확인함
    resultReady = QtCore.pyqtSignal(str) 

    def __init__(self, feature_name): # 클래스 초기화 -> feature_name에 따라 시작
        super().__init__()
        self.feature_name = feature_name
    
    def run(self):
        try:
            module = importlib.import_module("Registry_collector." + self.feature_name) # 모듈 동적 임포트 (importlib)
            f = io.StringIO() # 결과 캡쳐
            with redirect_stdout(f):
                module.run()
            output_text = f.getvalue() # 결과를 문자열로 캡처
            self.resultReady.emit(output_text)  # 결과 데이터 전송
        except Exception as e:
            print(f"Error in feature {self.feature_name}: {e}")
        finally:
            self.finished.emit()

class MyApp(QMainWindow):
    def __init__(self): # self 는 내가 띄우려는 창의 객체를 나타냄 = 내 자신
        # 클래스 초기화 및 초기 ui 설정 
        super().__init__()
        self.output_text = ""
        self.threads = []
        self.initUI()            
        self.original_data = []
    
    
    
    def initUI(self):
        # 제목, 아이콘 이미지, 창 크기 설정
        self.setWindowTitle('Welcome to Registry collecte world')
        self.setWindowIcon(QIcon("main/Registry_collector/오려낸 여우.png"))
        self.setGeometry(300, 300, 1500, 700)
        ########################################
        #메인 위젯과 레이아웃 설정
        mainWidget = QWidget(self)
        mainLayout = QVBoxLayout(mainWidget)

        # 버튼 그리드 레이아웃
        functionGridLayout = QGridLayout()
        for i in range(1, 16):
            button = QPushButton(f'Button {i}', self)
            button.clicked.connect(lambda _, b=i: self.load_feature(f'Button {b}'))
            functionGridLayout.addWidget(button, i // 4, i % 4)  # 그리드 위치 계산 및 추가

        #스크르롤 영역 내의 레이아웃 설정하기
        resultScrollArea = QScrollArea(self)
        resultScrollAreaWidgetContents = QWidget()
        resultScrollArea.setWidget(resultScrollAreaWidgetContents)
        resultScrollArea.setWidgetResizable(True)
        resultScrollLayout = QVBoxLayout(resultScrollAreaWidgetContents)

        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        resultScrollLayout.addWidget(self.result_label)
        resultScrollAreaWidgetContents.setLayout(resultScrollLayout)
        
        # 툴바 설정
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        saveAction = QAction(QIcon("main/Registry_collector/저장.png"), 'SAVE', self)
        saveAction.triggered.connect(self.save)
        self.toolbar.addAction(saveAction)

        # 기존 버튼과 레이블 코드                   
        self.btn1 = QPushButton('도움말', self)
        self.btn1.clicked.connect(lambda: self.load_feature("help")) 
        functionGridLayout.addWidget(self.btn1, 0, 0)
         

        self.btn2 = QPushButton('시스템 정보', self)
        self.btn2.clicked.connect(lambda: self.load_feature("system_info")) 
        functionGridLayout.addWidget(self.btn2, 0, 1)

        self.btn3 = QPushButton('유저 정보', self)
        self.btn3.clicked.connect(lambda: self.load_feature("user_info")) 
        functionGridLayout.addWidget(self.btn3, 0, 2)

        self.btn4 = QPushButton('자동 제거 여부', self)
        self.btn4.clicked.connect(lambda: self.load_feature("자동제거")) 
        functionGridLayout.addWidget(self.btn4, 0, 3)

        self.btn5 = QPushButton('자동실행프로그램', self)
        self.btn5.clicked.connect(lambda: self.load_feature("autorun_location")) 
        functionGridLayout.addWidget(self.btn5, 1, 0)

        self.btn6 = QPushButton('LNK 정보', self)
        self.btn6.clicked.connect(lambda: self.load_feature("LNK_info")) 
        functionGridLayout.addWidget(self.btn6 , 1, 1)

        self.btn7 = QPushButton('TimeZone', self)
        self.btn7.clicked.connect(lambda: self.load_feature("TimeZone")) 
        functionGridLayout.addWidget(self.btn7, 1, 2)

        """ self.btn7 = QPushButton('MRU 리스트', self)
        self.btn7.clicked.connect(lambda: self.load_feature("MRU_List")) 
        functionGridLayout.addWidget(self.btn7, 1, 2) """

        self.btn8 = QPushButton('네트워크 정보', self)
        self.btn8.clicked.connect(lambda: self.load_feature("network_interface")) 
        functionGridLayout.addWidget(self.btn8, 1, 3)

        self.btn9 = QPushButton('프리패치 정보', self)
        self.btn9.clicked.connect(lambda: self.load_feature("prefetch_info")) 
        functionGridLayout.addWidget(self.btn9, 2, 0)

        self.btn10 = QPushButton('RDP 연결 정보', self)
        self.btn10.clicked.connect(lambda: self.load_feature("RDP_CONNEC")) 
        functionGridLayout.addWidget(self.btn10, 2, 1)

        self.btn11 = QPushButton('유저별 RDP 정보', self)
        self.btn11.clicked.connect(lambda: self.load_feature("RDP_connect_user_info")) 
        functionGridLayout.addWidget(self.btn11, 2, 2)

        self.btn12 = QPushButton('최근 종료 시간', self)
        self.btn12.clicked.connect(lambda: self.load_feature("shutdowntime")) 
        functionGridLayout.addWidget(self.btn12, 2, 3)

        self.btn13 = QPushButton('소프트웨어 정보', self)
        self.btn13.clicked.connect(lambda: self.load_feature("software_info")) 
        functionGridLayout.addWidget(self.btn13,3, 0)

        self.btn14 = QPushButton('외부장치 정보', self)
        self.btn14.clicked.connect(lambda: self.load_feature("USB_info")) 
        functionGridLayout.addWidget(self.btn14, 3, 1)

        self.btn15 = QPushButton('유저별 외부장치 연결 정보', self)
        self.btn15.clicked.connect(lambda: self.load_feature("USER_USB")) 
        functionGridLayout.addWidget(self.btn15, 3, 2)

        self.btn16 = QPushButton('모든 레지스트리 정보', self)
        self.btn16.clicked.connect(lambda: self.load_feature("모든레지스트리")) 
        functionGridLayout.addWidget(self.btn16, 3, 3)

        # QLabel 추가
        self.result_label = QLabel(self)
        resultScrollLayout.addWidget(self.result_label)
        
        # 중앙 위젯 설정 -> winmain 에 레이아웃 위치 설정은 필수이다.
        self.setCentralWidget(mainWidget)
        
        # 메인 레이아웃에 버튼 그리드 레이아웃 추가
        mainLayout.addLayout(functionGridLayout)
        mainLayout.addWidget(resultScrollArea)

        #메인위젯 설정
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        #검색기능창 구현
        self.search_edit = QLineEdit(self)
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.perform_search)

        search_layout = QVBoxLayout()
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_button)
        mainLayout.addLayout(search_layout)
       
        
    def perform_search(self):
        search_term = self.search_edit.text().lower() #search_edit 에 들어간 단어를 serch_term으로 함.
        filtered_data = [data for data in self.original_data if search_term in data.lower()] #대소문자 구분없이 search_term 단어를 self.original_data에서 찾는다. 그리고 이 값을 filtered_data에 넣음
        self.updateResult("\n".join(filtered_data)) # 검색된 데이터(=filtered_data)를 결과 ui 에 띄우기 위해 updateResult 에 연결

    def updateResult(self, text): # 결과를 ui 에 올려준다.
        self.output_text = text
        self.result_label.setText(self.output_text)
        self.original_data = text.split('\n') # 수집한 데이터를 검색할 데이터로 변환



    def load_feature(self, feature_name):
        self.output_text = "" # 결과 초기화 = 새로운 정보 출력할 준비
        self.result_label.setText(self.output_text) #텍스트 선정
        self.showProgressDialog() #프로그래스바 나타내기
        self.setupThread(feature_name) #쓰레드 사용해 gui와 별도로 수집 실행
        """ self.disableButtons() """
    

    def showProgressDialog(self): # 프로그래스바 설정
        self.progressDialog = QProgressDialog("정보 수집 중...\n " " \n 잠시만 기다려 주세요.", None, 0, 0, self)
        self.progressDialog.setCancelButton(None)
        self.progressDialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progressDialog.setWindowFlags(self.progressDialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.progressDialog.show()
        
    def setupThread(self, feature_name): #별도 작업 실행 설정
        thread = QtCore.QThread()  # 새 스레드 생성
        self.threads.append(thread)  # 생성된 스레드를 리스트에 추가
        self.worker = all_registry_Worker(feature_name)  # 수집 실행
        self.worker.moveToThread(thread) 
        thread.started.connect(self.worker.run)
        self.worker.resultReady.connect(self.updateResult)  # all_registry_Worker에서 resultReady가 호출되면 updateResult를 호출해 값을 ui 에 올린다
        self.worker.finished.connect(thread.quit)  # 연결 종료
        self.worker.finished.connect(self.worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self.progressDialog.close)
        thread.start()
        """ self.thread.finished.connect(self.enableButtons) """ # 스레드가 종료될 때 버튼을 활성화
    
    
        

    def save(self):
        if self.output_text:
            options = QFileDialog.Option()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            with open(fileName, "w") as file:
                file.write(self.output_text)
            print(f"File saved : {fileName}")


def durumi():
    app = QApplication.instance() # 현재 사용중인 QApplication 인스턴스가 있는지 확인한다.
                                    # 있으면 그 인스턴스 변수를 사용한다.
                                    #QApplication은 프로그램에서 하나만 사용 가능하다. 
                                    #그래서 한개만 사용하도록 만든다. 
    if app is None:
        app = QApplication(sys.argv)
    
    ex = MyApp() # MyApp 클래스의 새 인스턴스를 생성 = 이건 gui 윈도우를 정의한다.
    
    
    ex.show() # MyApp gui 인스턴스를 화면에 표시한다.
    app.exec_() # PyQt5 QApplication 이벤트 루프를 시작함




if __name__ == '__main__':
    durumi()
