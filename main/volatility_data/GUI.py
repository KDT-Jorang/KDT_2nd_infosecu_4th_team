import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QDialog,
    QLabel,
)
from PyQt5.QtGui import QTextCursor, QTextDocument, QColor, QIcon
import importlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys_collector

class FileCheckBox(QCheckBox):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.setText(os.path.basename(file_path))


current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

file_names = [
    "clipboard_data.py",
    "device_connected_record.py",
    #"process_dump.py",
    "first_act_process.py",
    "net_connections.py",
    "net_information.py",
    "process_name_id_handle.py",
    "process_pid_user_memory.py",
    #"process-handle.py",
    "system_information.py",
    "time_information.py",
]

file_paths = [os.path.join(current_dir, file_name) for file_name in file_names]


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("파일 선택 프로그램")

        self.file_checkboxes = []
        for file_path in file_paths:
            checkbox = FileCheckBox(file_path)
            self.file_checkboxes.append(checkbox)

        self.run_button = QPushButton("실행")
        self.run_button.clicked.connect(self.run_selected_files)

        self.clear_button = QPushButton("결과 지우기")
        self.clear_button.clicked.connect(self.clear_result)

        self.save_button = QPushButton("결과 저장")
        self.save_button.clicked.connect(self.save_result)

        self.select_all_button = QPushButton("일괄 선택")
        self.select_all_button.clicked.connect(self.select_all)

        self.search_field = QLineEdit()
        self.search_button = QPushButton("검색")
        self.search_button.clicked.connect(self.search_result)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout = QVBoxLayout()
        for checkbox in self.file_checkboxes:
            layout.addWidget(checkbox)
        layout.addWidget(self.run_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.select_all_button)
        layout.addWidget(self.search_field)
        layout.addWidget(self.search_button)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

        self.search_result_window = None

    def run_selected_files(self):
        self.result_text.clear()
        results = []
        for checkbox in self.file_checkboxes:
            if checkbox.isChecked():
                module_name = "volatility_data." + checkbox.text().replace(".py", "")
                module = importlib.import_module(module_name)
                result = module.run()  # run function in each module
                results.append(result)

        for result in results:
            self.result_text.append(str(result))

    def clear_result(self):
        self.result_text.clear()

    def save_result(self):
        filename = os.path.join(os.getcwd(), "result.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.result_text.toPlainText())

    def select_all(self):
        for checkbox in self.file_checkboxes:
            checkbox.setChecked(True)

        result = sys_collector.run()

        
        self.result_text.append(f"=== total.py ===")
        self.result_text.append(str(result))
        self.result_text.append("수집이 완료되었습니다.")

    def search_result(self):
        try:
            search_text = self.search_field.text()
            occurrences = self.result_text.toPlainText().count(search_text)

            self.search_result_window = QDialog()
            self.search_result_window.setWindowTitle("검색 결과")
            self.search_result_window.setLayout(QVBoxLayout())

            label = QLabel()
            label.setText(f"'{search_text}'이(가) {occurrences}번 나왔습니다.")
            self.search_result_window.layout().addWidget(label)

            back_button = QPushButton("이전 결과")
            back_button.clicked.connect(
                lambda: self.result_text.find(search_text, QTextDocument.FindBackward)
            )
            self.search_result_window.layout().addWidget(back_button)

            next_button = QPushButton("다음 결과")
            next_button.clicked.connect(lambda: self.result_text.find(search_text))
            self.search_result_window.layout().addWidget(next_button)

            self.search_result_window.show()

            self.result_text.moveCursor(QTextCursor.Start)

            extra_selections = []
            cursor = QTextCursor(self.result_text.document())
            while cursor.find(search_text):
                extra_selection = QTextEdit.ExtraSelection()
                extra_selection.format.setBackground(QColor("yellow"))
                extra_selection.cursor = cursor
                extra_selections.append(extra_selection)
            self.result_text.setExtraSelections(extra_selections)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
