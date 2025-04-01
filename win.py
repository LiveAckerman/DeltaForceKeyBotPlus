import sys
import json
import pygetwindow as gw  # 使用 pygetwindow 库
import pyautogui
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QPixmap, QScreen, QImage


def read_config_field(field, default=None):
    """读取 config.json 中指定字段的值"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get(field, default)
    except FileNotFoundError:
        return default

def write_config_field(field, value):
    """写入 config.json 中指定字段的值"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    config[field] = value

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


class LogRedirector:
    """将标准输出重定向到日志区域"""
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def write(self, message):
        if message.strip():  # 忽略空行
            self.log_callback(message.strip())

    def flush(self):
        pass  # 必须实现，但这里不需要具体操作


class ConfigApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("配置工具")
        self.setGeometry(100, 100, 1000, 600)  # 调整窗口大小
        self.selection_area = None  # 用于存储框选区域的值

        # 初始化界面
        self.initUI()

        # 重定向标准输出到日志区域
        sys.stdout = LogRedirector(self.log_message)

    def initUI(self):
        # 主布局
        self.main_layout = QHBoxLayout()  # 修改为水平布局

        # 左侧布局
        left_layout = QVBoxLayout()

        # 第一行：主操作选择和具体配置内容
        operation_layout = QHBoxLayout()
        operation_layout.addWidget(QLabel("主操作选择："))
        self.main_combo_box = QComboBox(self)
        self.main_combo_box.addItem("请选择要执行的操作")
        self.main_combo_box.addItem("配置钥匙卡名称和价格位置")
        self.main_combo_box.addItem("配置钥匙卡位置")
        self.main_combo_box.addItem("配置购买按钮位置")
        self.main_combo_box.currentIndexChanged.connect(self.update_secondary_options)
        operation_layout.addWidget(self.main_combo_box)

        operation_layout.addWidget(QLabel("具体配置内容："))
        self.secondary_combo_box = QComboBox(self)
        self.secondary_combo_box.addItem("请选择具体配置内容")
        operation_layout.addWidget(self.secondary_combo_box)

        # 开始配置按钮
        self.start_button = QPushButton("开始配置", self)
        self.start_button.clicked.connect(self.start_configuration)
        operation_layout.addWidget(self.start_button)

        left_layout.addLayout(operation_layout)

        # 第二行：框选区域文字、截图和保存配置按钮
        screenshot_row_layout = QVBoxLayout()
        self.screenshot_label_text = QLabel("框选区域：")
        screenshot_row_layout.addWidget(self.screenshot_label_text)

        self.screenshot_label = QLabel(self)
        self.screenshot_label.setFixedSize(400, 300)
        self.screenshot_label.setStyleSheet("border: 1px solid #ccc;")  # 添加边框
        screenshot_row_layout.addWidget(self.screenshot_label)

        # 框选区域提示信息
        self.selection_info_label = QLabel("框选区域：[x=0, y=0, 宽=0, 高=0]")
        self.selection_info_label.setStyleSheet("font-size: 16px; color: #ff0000;")
        screenshot_row_layout.addWidget(self.selection_info_label)

        # 保存配置按钮
        self.save_button = QPushButton("保存配置", self)
        self.save_button.clicked.connect(self.save_configuration)
        screenshot_row_layout.addWidget(self.save_button)

        left_layout.addLayout(screenshot_row_layout)

        # 右侧布局：日志显示
        right_layout = QVBoxLayout()
        self.log_label = QLabel("日志：")
        right_layout.addWidget(self.log_label)

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)  # 设置为只读
        right_layout.addWidget(self.log_text)

        # 将左右布局添加到主布局
        self.main_layout.addLayout(left_layout, 2)  # 左侧占 2/3 宽度
        self.main_layout.addLayout(right_layout, 1)  # 右侧占 1/3 宽度

        # 设置主窗口布局
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # 应用样式
        self.apply_styles()

    def log_message(self, message):
        """在日志区域显示消息"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def update_secondary_options(self, index):
        """根据主操作选择更新第二个下拉框的选项"""
        self.secondary_combo_box.clear()  # 清空第二个下拉框的选项

        if index == 1:  # 配置钥匙卡名称和价格位置
            self.secondary_combo_box.addItem("钥匙卡的名称区域")
            self.secondary_combo_box.addItem("钥匙卡的价格区域")
        elif index == 2:  # 配置钥匙卡位置
            # 从 config.json 中读取 keys 数组
            keys = read_config_field("keys", [])
            if keys:
                for key in keys:
                    self.secondary_combo_box.addItem(key.get("name", "未知钥匙卡"))
            else:
                self.secondary_combo_box.addItem("未找到钥匙卡数据")
        elif index == 3:  # 配置购买按钮位置
            self.secondary_combo_box.addItem("购买按钮位置")
        else:
            self.secondary_combo_box.addItem("请选择具体配置内容")

    def start_configuration(self):
        """处理开始配置按钮点击事件"""
        # 校验具体配置内容是否选择了具体选项
        if self.secondary_combo_box.currentText() == "请选择具体配置内容":
            QMessageBox.warning(self, "提示", "请先选择具体配置内容！")
            return

        # 获取并激活窗口标题包含“三角洲”的窗口
        target_window = None
        for window in gw.getAllTitles():
            if "三角洲" in window:  # 模糊匹配窗口标题
                target_window = gw.getWindowsWithTitle(window)[0]
                break

        if target_window:
            target_window.activate()  # 激活“三角洲”窗口
            self.log_message(f"已激活窗口：{target_window.title}")
        else:
            QMessageBox.warning(self, "提示", "未找到标题包含“三角洲”的窗口！")
            self.log_message("未找到标题包含“三角洲”的窗口！")
            return

        # 最小化主窗口
        self.showMinimized()

        # 打开全屏透明窗口
        self.selection_window = SelectionWindow(self)
        self.selection_window.show()

        # 再次激活全屏透明窗口
        self.selection_window.activateWindow()
        self.selection_window.setFocus()

    def display_screenshot(self, screenshot):
        """在主窗口中显示截图"""
        self.screenshot_label.setPixmap(screenshot.scaled(
            self.screenshot_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.showNormal()  # 恢复主窗口

    def set_selection_area(self, x, y, width, height):
        """设置框选区域"""
        self.selection_area = [x, y, width, height]
        # 更新框选区域提示信息
        self.selection_info_label.setText(f"框选区域：[x={x}, y={y}, 宽={width}, 高={height}]")
        self.log_message(f"框选区域：[x={x}, y={y}, 宽={width}, 高={height}]")

    def save_configuration(self):
        """保存配置按钮点击事件"""
        selected_option = self.secondary_combo_box.currentText()
        main_option = self.main_combo_box.currentText()

        if main_option == "配置钥匙卡名称和价格位置":
            # 钥匙卡的名称区域或价格区域逻辑
            if selected_option == "钥匙卡的名称区域":
                field = "card_name_range"
            elif selected_option == "钥匙卡的价格区域":
                field = "card_price_range"
            else:
                QMessageBox.warning(self, "提示", "当前配置内容无法保存！")
                return

            # 检查是否有框选区域
            if not self.selection_area:
                QMessageBox.warning(self, "提示", "请先完成框选操作！")
                return

            # 获取框选区域的值
            x, y, width, height = self.selection_area

            # 使用公共函数写入配置文件，保存为数组格式
            write_config_field(field, [x, y, width, height])

            QMessageBox.information(self, "保存配置", f"{selected_option} 已保存到 {field}！")

        elif main_option == "配置钥匙卡位置":
            # 钥匙卡位置逻辑
            keys = read_config_field("keys", [])
            if not keys:
                QMessageBox.warning(self, "提示", "配置文件中没有找到 keys 数组！")
                return

            # 查找选中的钥匙卡
            selected_card = None
            for card in keys:
                if card.get("name") == selected_option:
                    selected_card = card
                    break

            if not selected_card:
                QMessageBox.warning(self, "提示", f"未找到名称为 {selected_option} 的钥匙卡！")
                return

            # 检查是否有框选区域
            if not self.selection_area:
                QMessageBox.warning(self, "提示", "请先完成框选操作！")
                return

            # 获取框选区域的值
            x, y, _, _ = self.selection_area  # 使用框选区域的 x 和 y
            screen_width, screen_height = pyautogui.size()
            x_percent = round(x / screen_width, 4)
            y_percent = round(y / screen_height, 4)

            # 更新 position 值
            selected_card["position"] = [x_percent, y_percent]
            print(f"{selected_card['name']} 的 position 已更新为: {selected_card['position']}")

            # 保存到配置文件
            write_config_field("keys", keys)
            QMessageBox.information(self, "保存配置", f"{selected_card['name']} 的位置已保存！")

        elif main_option == "配置购买按钮位置":
            # 购买按钮位置逻辑
            if not self.selection_area:
                QMessageBox.warning(self, "提示", "请先完成框选操作！")
                return

            # 获取框选区域的值
            x, y, _, _ = self.selection_area  # 使用框选区域的 x 和 y
            screen_width, screen_height = pyautogui.size()
            x_percent = round(x / screen_width, 4)
            y_percent = round(y / screen_height, 4)

            # 更新 purchase_btn_location 值
            write_config_field("purchase_btn_location", [x_percent, y_percent])
            self.log_message(f"购买按钮的位置已更新为: {[x_percent, y_percent]}")  # 使用日志记录

            QMessageBox.information(self, "保存配置", "购买按钮的位置已保存！")

        else:
            QMessageBox.warning(self, "提示", "当前配置内容无法保存！")

    def apply_styles(self):
        """应用样式表"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QPushButton {
                font-size: 14px;
                padding: 5px 10px;
                border: 1px solid #0078d7;
                border-radius: 5px;
                background-color: #0078d7;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QTextEdit {
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
        """)


class SelectionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        # 设置窗口标志，确保全屏透明窗口覆盖其他应用程序
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setWindowState(Qt.WindowFullScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置背景透明
        self.setWindowModality(Qt.ApplicationModal)  # 设置为模态窗口
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False
        self.show_red_border = True  # 控制是否显示红色边框

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.start_point = event.globalPos()
        self.end_point = self.start_point
        self.is_selecting = True
        self.show_red_border = True  # 开始框选时显示红色边框
        self.update()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_selecting:
            self.end_point = event.globalPos()
            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.is_selecting:
            self.end_point = event.globalPos()
            self.is_selecting = False
            self.update()

            # 计算框选区域
            x1 = min(self.start_point.x(), self.end_point.x())
            y1 = min(self.start_point.y(), self.end_point.y())
            x2 = max(self.start_point.x(), self.end_point.x())
            y2 = max(self.start_point.y(), self.end_point.y())
            width = x2 - x1
            height = y2 - y1

            # 打印框选区域
            print(f"框选区域：[x={x1}, y={y1}, 宽={width}, 高={height}]")

            # 将框选区域传递给主窗口
            self.parent.set_selection_area(x1, y1, width, height)

            # 截图框选区域
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, x1, y1, width, height)

            # 显示截图到主窗口
            self.parent.display_screenshot(screenshot)

            # 关闭红色边框的显示
            self.show_red_border = False
            self.update()

            # 关闭透明窗口
            self.close()

    def keyPressEvent(self, event):
        """键盘按下事件"""
        if event.key() == Qt.Key_Escape:  # 检测是否按下 ESC 键
            print("ESC 键按下，退出框选窗口")
            self.close()  # 关闭透明窗口
            event.accept()  # 标记事件为已处理，防止传播到其他程序
        else:
            event.ignore()  # 对于其他按键，继续传播事件

    def paintEvent(self, event):
        """绘制框选区域和背景"""
        painter = QPainter(self)

        # 绘制半透明黑色背景
        painter.setOpacity(0.5)
        painter.fillRect(self.rect(), Qt.black)

        # 绘制框选区域
        if self.is_selecting:
            painter.setOpacity(0.3)
            painter.fillRect(QRect(self.start_point, self.end_point), Qt.white)
            if self.show_red_border:  # 仅在框选时显示红色边框
                painter.setOpacity(1.0)
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                rect = QRect(self.start_point, self.end_point)
                painter.drawRect(rect)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigApp()
    window.show()
    sys.exit(app.exec_())