import os
import sys
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QEvent, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QDesktopServices
import platform
from TR_Utils.wordtopdf import createPdf
from TR_Utils.controller import con
from TR_Utils.text_filter import TextFilter
from TR_Utils.history_file import History_file
from TR_Utils.configure import config, config_path
from pathlib import Path
import PyPDF2


fp = Path(__file__)
sys.path.append(str(fp.parent.parent))
from service import retrieval_request
from service.translation_request import test_server_api as trans_server_api

RETRIEVAL_URL = "http://10.70.114.117:8080"
TRANSLATE_URL = "http://10.70.114.117:8081/"

sysstr = platform.system()
is_win = is_linux = is_mac = False

if sysstr == "Windows":
    is_win = True
elif sysstr == "Linux":
    is_linux = True
elif sysstr == "Mac":
    is_mac = True
## print('System: %s' % sysstr)

MAX_CHARACTERS = 5000  # 最大翻译数


class WebView(QWebEngineView):
    def __init__(self):
        ###print('init webView')
        super(WebView, self).__init__()
        self._glwidget = None
        self.pdf_js_path = "file:///" + os.path.join(os.getcwd(), "pdfjs",
                                                     "web", "viewer.html")
        pdf_path = "file:///" + os.path.join(os.getcwd(), "sample",
                                             "induction.pdf")
        if sys.platform == "win32":
            self.pdf_js_path = self.pdf_js_path.replace("\\", "/")
            pdf_path = pdf_path.replace('\\', '/')
        self.pdf_path = pdf_path[8:]
        self.changePDF(pdf_path)
        self.setAcceptDrops(True)
        self.installEventFilter(self)

    def dragEnterEvent(self, e):

        if is_linux or is_mac:
            if e.mimeData().hasFormat(
                    'text/plain') and e.mimeData().text()[-6:-2] == ".pdf":
                e.accept()
            else:
                e.ignore()
        elif is_win:
            if e.mimeData().text()[-4:] == ".pdf":
                e.accept()
            else:
                e.ignore()

    def event(self, e):
        """
        Detect child add event, as QWebEngineView do not capture mouse event directly,
        the child layer _glwidget is implicitly added to QWebEngineView and we track mouse event through the glwidget
        :param e: QEvent
        :return: super().event(e)
        """
        if self._glwidget is None:
            if e.type() == QEvent.ChildAdded and e.child().isWidgetType():
                ###print('child add')
                self._glwidget = e.child()
                self._glwidget.installEventFilter(self)
        return super().event(e)

    def eventFilter(self, source, event):
        if event.type(
        ) == QEvent.MouseButtonRelease and source is self._glwidget:
            con.pdfViewMouseRelease.emit()
        return super().eventFilter(source, event)

    def changePDF(self, pdf_path):

        self.load(
            QUrl.fromUserInput('%s?file=%s' % (self.pdf_js_path, pdf_path)))
        if sys.platform == 'win32' and 'sample' not in pdf_path:
            if "/" in pdf_path:

                with open(config_path, "w", encoding='GB2312') as f:
                    config.set("history_pdf",
                               pdf_path.split('/')[-1], pdf_path)
                    config.write(f)
                    self.pdf_path = pdf_path
            else:

                config.set("history_pdf",
                           pdf_path.split('\\')[-1].split('.')[0], pdf_path)
                with open("config.txt", "w", encoding='GB2312') as f:
                    config.write(f)
                    self.pdf_path = pdf_path
        print(self.pdf_path)


class MainWindow(
        QMainWindow, ):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SUAI")
        self.setWindowIcon(QIcon("./sample/logo.ico"))

        self.pdfWrapper = WebView()
        self.pdfWrapper.setContentsMargins(0, 0, 0, 0)
        # gbox.setContentsMargins(0, 0, 0, 0)
        self.filter = TextFilter()

        '''    *****************************  create history area  ******************************     '''
        # 创建一个 QDockWidget 用于包装历史文件窗口
        self.dock_widget = QDockWidget("历史文件", self)
        self.dock_widget.setStyleSheet("font-size:12pt")
        self.window = History_file(self.pdfWrapper)
        self.dock_widget.setWidget(self.window)

        # 创建一个 QToolBar 用于放置三个 QAction
        self.toolbar = QToolBar()
        
        # 添加间隔0
        self.t_s0 = QAction('                            ', self)
        self.t_s0.setEnabled(False)
        self.toolbar.addAction(self.t_s0)

        # 打开PDF
        self.t_folder_open = QAction(QIcon("./sample/folder_open.ico"),
                                     '打开文件', self)
        self.toolbar.insertSeparator(self.t_folder_open)
        self.toolbar.addAction(self.t_folder_open)

        # 添加间隔1
        self.t_s1 = QAction('                            ', self)
        self.t_s1.setEnabled(False)
        self.toolbar.addAction(self.t_s1)
        self.toolbar.insertSeparator(self.t_s1)

        # 翻译文本
        self.trans = QAction(QIcon("./sample/translation.ico"),
                                     '翻译文本', self)
        self.toolbar.insertSeparator(self.trans)
        self.toolbar.addAction(self.trans)
        
        # 添加间隔2
        self.t_s2 = QAction('                            ', self)
        self.t_s2.setEnabled(False)
        self.toolbar.addAction(self.t_s2)
        self.toolbar.insertSeparator(self.t_s2)

        # 文献检索
        self.retri = QAction(QIcon("./sample/retrieval.ico"),
                                     '检索文献', self)
        self.toolbar.insertSeparator(self.retri)
        self.toolbar.addAction(self.retri)
 
        # 添加间隔3
        self.t_s3 = QAction('                            ', self)
        self.t_s3.setEnabled(False)
        self.toolbar.addAction(self.t_s3)
        self.toolbar.insertSeparator(self.t_s3)


        self.toolbar.actionTriggered[QAction].connect(self.operation)

        # 将 QToolBar 添加到 QDockWidget 顶部
        self.dock_widget.setTitleBarWidget(self.toolbar)

        # 将 QDockWidget 放置在主窗口的左侧
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

        hBoxLayout = QHBoxLayout()
        # 左右窗口可动态变化
        splitter1 = QSplitter(Qt.Horizontal)
        # splitter1.addWidget(gbox)
        splitter1.addWidget(self.pdfWrapper)
        hBoxLayout.addWidget(splitter1)

        widget = QWidget()
        widget.setLayout(hBoxLayout)

        self.setCentralWidget(widget)
        self.recent_text = ""
        self.showMaximized()
        
        self.filter = TextFilter()

    def operation(self, qaction):
        
        # 从本地打开文件
        if qaction.text() == '打开文件':
            try:
                fd = QFileDialog.getOpenFileName(self, '打开文件', './',
                                                 'All(*.*);;PDF(*.pdf)',
                                                 'All(*.*)')
                if fd[0].split('/')[-1].split(".")[-1] == "pdf":
                    self.pdfWrapper.changePDF(fd[0])

                elif fd[0].split('/')[-1].split(".")[-1] == "docx" or fd[
                        0].split('/')[-1].split(".")[-1] == "doc":
                    ss = fd[0].split(".")[:-1]
                    self.sss = str(ss[0]) + ".pdf"
                    createPdf(fd[0], self.sss)
                    self.pdfWrapper.changePDF(self.sss)
                self.window = History_file(self.pdfWrapper)
                self.dock_widget.setWidget(self.window)
            except:
                pass

        # 翻译选中文本为中文
        elif qaction.text() == '翻译文本':
            try:
                if self.recent_text == "":
                    return
                data = {"name": self.recent_text}
                trans_res = trans_server_api(TRANSLATE_URL, data)
                translate_dialog = TranslationDialog(self.recent_text, trans_res)
                translate_dialog.exec_()
            except:
                # 弹出提示框提醒错误
                QMessageBox.information(None, "WARNING", "当前网络繁忙，请稍后重试")
        
        # 检索选中内容相关文献
        elif qaction.text() == '检索文献':
            try:
                instruct = self.getPdfContent()
                # print(instruct)
                if self.recent_text == "":
                    return
                data = {'instruct': instruct, 'query': self.recent_text, 'max_capacity': 10}
                out = retrieval_request.test_server_api(RETRIEVAL_URL, data)
                # out是一个列表，每个元素是一个列表，包含[论文标题, 引用数, 发表时间及机构缩写, 论文链接]
                paper_dialog = RetrievalDialog(out)
                paper_dialog.exec_()
            except Exception as e:
                QMessageBox.information(None, "WARNING", "当前网络繁忙，请稍后重试")
                # 弹出提示框提醒错误
    
    def getPdfContent(self):
        pdfReader = PyPDF2.PdfReader(self.pdfWrapper.pdf_path)
        pageObj = pdfReader.pages[0].extract_text()
        pageObj = self.filter.removeDashLine(pageObj)
        pageObj = pageObj.split(' ')
        if len(pageObj) > 150:
            return " ".join(pageObj[:150])
        else:
            return " ".join(pageObj)

    def getHistoryPDF(self):
        tp = config.items('history_pdf')
        name_list = []
        path_list = []
        for item in tp:
            name_list.append(item[0])
            path_list.append(item[1])
        return path_list, name_list


    def updateByMouseRelease(self):
        # print('no seletion to translate')
        if self.pdfWrapper.hasSelection():

            to_translate_text = self.pdfWrapper.selectedText()
            if len(to_translate_text) > MAX_CHARACTERS:
                hint_str = '请选择少于%d个英文字符' % MAX_CHARACTERS

                return
            else:
                if self.recent_text == to_translate_text:
                    # print('same as before, not new translate')
                    return
                else:
                    filtered = self.filter.removeDashLine(to_translate_text)
                    self.recent_text = filtered

    def closeEvent(self, event):
        result = QMessageBox.question(self, "警告", "Do you want to exit?",
                                      QMessageBox.Yes | QMessageBox.No)
        if (result == QMessageBox.Yes):
            event.accept()
            try:
                os.remove(self.sss)
            except:
                pass
        else:
            event.ignore()
    
# 论文检索结果呈现类，继承自 QDialog 的 RetrievalDialog 类
class RetrievalDialog(QDialog):
    def __init__(self, papers):
        super().__init__()

        self.setWindowTitle("论文检索结果")
        self.setGeometry(100, 100, 600, 400)
            
        self.papers = papers

        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()

        table = QTableWidget(self)
        table.setRowCount(len(self.papers))
        table.setColumnCount(3)

        table.setHorizontalHeaderLabels(["论文标题", "引用量", "发表时间及机构缩写"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)

        for row, paper in enumerate(self.papers):
            title_item = QTableWidgetItem(paper[0])
            # 论文链接保存到 UserRole 中
            title_item.setData(Qt.UserRole, paper[3])
            table.setItem(row, 0, title_item)
            table.setItem(row, 1, QTableWidgetItem(str(paper[1])))
            table.setItem(row, 2, QTableWidgetItem(paper[2]))

        table.cellClicked.connect(self.openPaperLink)

        layout.addWidget(table)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout.addWidget(button_box)

        self.setLayout(layout)
        
    def openPaperLink(self, row, column):
        if column == 0:
            link = self.papers[row][3]
            QDesktopServices.openUrl(QUrl(link))
    

class TranslationDialog(QDialog):
    def __init__(self, original_text, translated_text, parent = None):
        super().__init__(parent)
        self.setWindowTitle("文本翻译结果")
        self.setGeometry(100, 100, 600, 400)

        # 弹窗上半部分：可编辑文本框
        self.original_text_edit = QTextEdit(self)
        self.original_text_edit.setPlainText(original_text)
        self.original_text_edit.setReadOnly(False)  # 设置为可编辑
        self.original_text_edit.setMinimumHeight(100)
        self.original_text_edit.setStyleSheet("font-size:12pt")

        # 下半部分：显示翻译结果
        self.translated_text_edit = QTextEdit(self)
        self.translated_text_edit.setPlainText(translated_text)
        self.translated_text_edit.setReadOnly(True)  # 设置为只读
        self.translated_text_edit.setMinimumHeight(100)
        self.translated_text_edit.setStyleSheet("font-size:12pt")

        # 翻译按钮
        self.translation_button = QPushButton("翻译")
        self.translation_button.clicked.connect(self.translate_text)

        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.original_text_edit)
        layout.addWidget(self.translated_text_edit)
        layout.addWidget(self.translation_button)

    def translate_text(self):
        # 获取当前文本框内容
        origin = self.original_text_edit.toPlainText()

        data = {"name": origin}
        translation_result = trans_server_api(TRANSLATE_URL, data)

        # 显示翻译结果
        self.translated_text_edit.setPlainText(translation_result)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    con.pdfViewMouseRelease.connect(mainWindow.updateByMouseRelease)

    sys.exit(app.exec_())
