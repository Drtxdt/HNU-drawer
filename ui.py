import sys
import matplotlib

matplotlib.use('Qt5Agg')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLabel,
    QFileDialog, QMessageBox, QSplitter, QHeaderView, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from plotter import Plotter

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Origin绘图工具替代版")
        self.setGeometry(100, 100, 1200, 800)

        # 创建主部件和布局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板：数据输入和控制
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 数据表格
        self.table = QTableWidget()
        self.table.setRowCount(20)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["X", "Y1", "Y2"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 连接表格变化信号
        self.table.itemChanged.connect(self.handle_table_change)

        # 控制区域
        control_group = QGroupBox("控制面板")
        control_layout = QVBoxLayout(control_group)

        # 拟合选项
        fit_layout = QHBoxLayout()
        fit_layout.addWidget(QLabel("拟合类型:"))
        self.fit_combo = QComboBox()
        self.fit_combo.addItems(["线性", "二阶多项式", "三阶多项式",
                                 "四阶多项式", "五阶多项式", "玻尔兹曼", "指数"])
        fit_layout.addWidget(self.fit_combo)

        # 数据列选择
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("数据列:"))
        self.col_combo = QComboBox()
        self.col_combo.addItems(["Y1", "Y2"])
        col_layout.addWidget(self.col_combo)

        # 按钮
        btn_layout = QHBoxLayout()
        self.plot_btn = QPushButton("绘制散点图")
        self.fit_btn = QPushButton("执行拟合")
        self.export_btn = QPushButton("导出图像")
        btn_layout.addWidget(self.plot_btn)
        btn_layout.addWidget(self.fit_btn)
        btn_layout.addWidget(self.export_btn)

        # 斜率显示
        self.slope_label = QLabel("斜率: ")
        self.slope_label.setVisible(False)

        # 添加到控制布局
        control_layout.addLayout(fit_layout)
        control_layout.addLayout(col_layout)
        control_layout.addLayout(btn_layout)
        control_layout.addWidget(self.slope_label)
        control_layout.addStretch()

        # 添加到左侧面板
        left_layout.addWidget(self.table)
        left_layout.addWidget(control_group)

        # 右侧面板：绘图区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 创建matplotlib画布
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # 创建Plotter实例
        self.plotter = Plotter(self.ax, self.canvas)

        right_layout.addWidget(self.canvas)

        # 添加面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])

        # 添加到主布局
        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

        # 连接信号
        self.plot_btn.clicked.connect(self.plot_data)
        self.fit_btn.clicked.connect(self.perform_fit)
        self.export_btn.clicked.connect(self.export_image)

        # 填充示例数据
        self.fill_example_data()

        # 初始化图表
        self.plot_data()

    def fill_example_data(self):
        # 填充一些示例数据
        for i in range(10):
            x = i
            y1 = 2 * x + 3
            y2 = 0.5 * x ** 2 - 2 * x + 1

            self.table.setItem(i, 0, QTableWidgetItem(str(x)))
            self.table.setItem(i, 1, QTableWidgetItem(str(y1)))
            self.table.setItem(i, 2, QTableWidgetItem(str(y2)))

    def handle_table_change(self):
        """处理表格数据变化"""
        # 使用定时器延迟更新，避免频繁重绘
        QTimer.singleShot(300, self.plot_data)

    def get_table_data(self):
        """从表格中获取数据"""
        data = {'x': [], 'y': []}
        col_idx = self.col_combo.currentIndex() + 1

        for row in range(self.table.rowCount()):
            x_item = self.table.item(row, 0)
            y_item = self.table.item(row, col_idx)

            if x_item and y_item and x_item.text().strip() and y_item.text().strip():
                try:
                    x_val = float(x_item.text())
                    y_val = float(y_item.text())
                    data['x'].append(x_val)
                    data['y'].append(y_val)
                except ValueError:
                    continue

        return data

    def plot_data(self):
        """绘制散点图"""
        data = self.get_table_data()
        if not data['x']:
            # 清除图表
            self.ax.clear()
            self.ax.set_title("散点图", fontsize=12)
            self.ax.set_xlabel("X", fontsize=10)
            self.ax.set_ylabel("Y", fontsize=10)
            self.canvas.draw()
            return

        self.plotter.plot_scatter(data['x'], data['y'])

    def perform_fit(self):
        """执行拟合操作"""
        data = self.get_table_data()
        if not data['x']:
            QMessageBox.warning(self, "错误", "没有有效数据可拟合！")
            return

        fit_type = self.fit_combo.currentText()

        try:
            x = data['x']
            y = data['y']
            x_fit, y_fit, equation, slope = self.plotter.perform_fit(x, y, fit_type)
            self.plotter.plot_fit(x, y, x_fit, y_fit, equation, slope)

            # 如果是线性拟合，显示斜率
            if fit_type == "线性":
                self.slope_label.setText(f"斜率: {slope:.6f}")
                self.slope_label.setVisible(True)
            else:
                self.slope_label.setVisible(False)

        except Exception as e:
            QMessageBox.critical(self, "拟合错误", f"拟合过程中发生错误:\n{str(e)}")

    def export_image(self):
        """导出图像"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图像", "", "PNG图像 (*.png);;JPEG图像 (*.jpg);;PDF文件 (*.pdf)"
        )

        if file_path:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "导出成功", f"图像已保存到:\n{file_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())