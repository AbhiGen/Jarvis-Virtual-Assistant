import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QPushButton, QFrame,
    QLabel, QSizePolicy, QHBoxLayout, QStackedWidget
)
from PyQt5.QtGui import QIcon, QPainter, QColor, QTextCharFormat, QFont, QPixmap, QMovie, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer, QObject
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantName = env_vars.get("AssistantName", "Grok")

# Directory paths
current_dir = os.getcwd()
tempDirPath = os.path.join(current_dir, "Frontend", "Files")  # Adjusted to Frontend/Files
GraphicsDirPath = os.path.join(current_dir, "FrontendGraphics")  # Images are here

# Ensure temp directory exists
os.makedirs(tempDirPath, exist_ok=True)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(os.path.join(tempDirPath, 'Mic.data'), 'w', encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    file_path = os.path.join(tempDirPath, 'Mic.data')
    if not os.path.exists(file_path):
        SetMicrophoneStatus("False")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(Status):
    with open(os.path.join(tempDirPath, 'Status.data'), 'w', encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    file_path = os.path.join(tempDirPath, 'Status.data')
    if not os.path.exists(file_path):
        SetAssistantStatus("")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def MicButtonInitialized():
    SetMicrophoneStatus("False")

def MicButtonClicked():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(tempDirPath, Filename)

def ShowTextToScreen(Text):
    with open(os.path.join(tempDirPath, 'Responses.data'), 'w', encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.old_chat_message = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, -40, 40, 100)
        layout.setSpacing(-10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(400, 270))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("GIF not found")
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)

        # Set background for ChatSection
        self.setStyleSheet("background-color: black;")

        # Apply stylesheet to QTextEdit only
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0 0 0 0;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical {
                background: black;
                height: 10px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::up-arrow:vertical {
                border: none;
                background: none;
            }
            QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical {
                background: none;
            }
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def eventFilter(self, obj, event):
        return super().eventFilter(obj, event)

    def loadMessages(self):
        file_path = TempDirectoryPath('Responses.data')
        if not os.path.exists(file_path):
            ShowTextToScreen("")
        with open(file_path, "r", encoding='utf-8') as file:
            messages = file.read()
            if not messages or len(messages) <= 1 or messages == self.old_chat_message:
                return
            self.addMessage(messages, 'White')
            self.old_chat_message = messages

    def SpeechRecogText(self):
        self.label.setText(GetAssistantStatus())

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(color))
        cursor.setCharFormat(char_format)

        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        block_format.setLeftMargin(10)
        cursor.setBlockFormat(block_format)

        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.ensureCursorVisible()

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 150)

        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            max_gif_size_H = int(screen_width / 16 * 9)
            movie.setScaledSize(QSize(screen_width, max_gif_size_H))
            gif_label.setAlignment(Qt.AlignCenter)
            gif_label.setMovie(movie)
            movie.start()
        else:
            gif_label.setText("GIF not found")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.icon_label = QLabel()
        mic_on_path = GraphicsDirectoryPath('Mic.on.png')
        if os.path.exists(mic_on_path):
            pixmap = QPixmap(mic_on_path)
            self.icon_label.setPixmap(pixmap.scaled(60, 60))
        else:
            self.icon_label.setText("Mic icon not found")
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.icon_label.mousePressEvent = self.toggle_icon
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        self.setLayout(content_layout)
        self.setFixedSize(screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        self.label.setText(GetAssistantStatus())

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            self.icon_label.setPixmap(pixmap.scaled(width, height))
        else:
            self.icon_label.setText("Icon not found")

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic.on.png'))
            MicButtonInitialized()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic.off.png'))
            MicButtonClicked()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection(self)
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(screen_width, screen_height)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton(" Home ", icon=QIcon(GraphicsDirectoryPath("Home.png")))
        home_button.setStyleSheet("height: 40px; background-color:white; color: black;")
        message_button = QPushButton(" Chat ", icon=QIcon(GraphicsDirectoryPath("Chats.png")))
        message_button.setStyleSheet("height: 40px; background-color:white; color: black;")
        minimize_button = QPushButton(icon=QIcon(GraphicsDirectoryPath('Minimize2.png')))
        minimize_button.setStyleSheet("background-color:white;")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton(icon=QIcon(GraphicsDirectoryPath('Maximize.png')))
        self.maximize_button.setStyleSheet("background-color:white;")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton(icon=QIcon(GraphicsDirectoryPath('Close.png')))
        close_button.setStyleSheet("background-color:white;")
        close_button.clicked.connect(self.closeWindow)

        title_label = QLabel(f" {str(AssistantName).capitalize()} AI ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white;")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath('Maximize.png')))
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath('Minimize.png')))

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen(self))
        stacked_widget.addWidget(MessageScreen(self))

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Initialize required files
    if not os.path.exists(os.path.join(tempDirPath, 'Mic.data')):
        SetMicrophoneStatus("False")
    if not os.path.exists(os.path.join(tempDirPath, 'Status.data')):
        SetAssistantStatus("")
    if not os.path.exists(os.path.join(tempDirPath, 'Responses.data')):
        ShowTextToScreen("")
    GraphicalUserInterface()