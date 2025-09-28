import numpy as np
from scipy.optimize import curve_fit


class Plotter:
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.fit_params = None
        self.fit_type = None
        self.last_data = None

    def plot_scatter(self, x, y):
        """绘制散点图"""
        # 保存当前数据用于后续比较
        self.last_data = (x, y)

        self.ax.clear()
        self.ax.scatter(x, y, color='blue', s=30, edgecolor='black', alpha=0.7, label='数据点')
        self.ax.set_title("散点图", fontsize=12)
        self.ax.set_xlabel("X", fontsize=10)
        self.ax.set_ylabel("Y", fontsize=10)
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        self.ax.legend(fontsize=8)
        self.canvas.draw()

    def linear_fit(self, x, y):
        """线性拟合"""
        # 拟合 y = mx + c
        coeffs = np.polyfit(x, y, 1)
        m, c = coeffs
        self.fit_params = (m, c)

        # 计算拟合线
        fit_line = np.poly1d(coeffs)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = fit_line(x_fit)

        return x_fit, y_fit, f"y = {m:.4f}x + {c:.4f}", m

    def poly_fit(self, x, y, degree):
        """多项式拟合"""
        coeffs = np.polyfit(x, y, degree)
        self.fit_params = coeffs

        # 创建多项式函数
        poly_func = np.poly1d(coeffs)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = poly_func(x_fit)

        # 创建方程字符串
        eq_str = "y = "
        for i, coef in enumerate(coeffs):
            power = len(coeffs) - i - 1
            if power == 0:
                eq_str += f"{coef:.4f}"
            elif power == 1:
                eq_str += f"{coef:.4f}x + "
            else:
                eq_str += f"{coef:.4f}x^{power} + "

        return x_fit, y_fit, eq_str, None

    def boltzmann_fit(self, x, y):
        """玻尔兹曼拟合"""

        # 玻尔兹曼函数: y = A2 + (A1 - A2)/(1 + exp((x-x0)/dx))
        def boltzmann(x, A1, A2, x0, dx):
            return A2 + (A1 - A2) / (1 + np.exp((x - x0) / dx))

        # 初始参数估计
        A1_guess = max(y)
        A2_guess = min(y)
        x0_guess = np.median(x)
        dx_guess = (max(x) - min(x)) / 10

        # 执行拟合
        try:
            params, _ = curve_fit(boltzmann, x, y, p0=[A1_guess, A2_guess, x0_guess, dx_guess])
            A1, A2, x0, dx = params
            self.fit_params = params

            # 计算拟合曲线
            x_fit = np.linspace(min(x), max(x), 100)
            y_fit = boltzmann(x_fit, A1, A2, x0, dx)

            eq_str = f"y = {A2:.4f} + ({A1:.4f}-{A2:.4f})/(1 + exp((x-{x0:.4f})/{dx:.4f}))"
            return x_fit, y_fit, eq_str, None
        except RuntimeError:
            raise ValueError("玻尔兹曼拟合失败，请检查数据是否适合此拟合类型")

    def exponential_fit(self, x, y):
        """指数拟合"""

        # 指数函数: y = a * exp(b * x)
        def exponential(x, a, b):
            return a * np.exp(b * x)

        # 初始参数估计
        a_guess = y[0]
        b_guess = (np.log(y[-1]) - np.log(y[0])) / (x[-1] - x[0]) if len(y) > 1 else 0.1

        # 执行拟合
        try:
            params, _ = curve_fit(exponential, x, y, p0=[a_guess, b_guess])
            a, b = params
            self.fit_params = params

            # 计算拟合曲线
            x_fit = np.linspace(min(x), max(x), 100)
            y_fit = exponential(x_fit, a, b)

            eq_str = f"y = {a:.4f} * exp({b:.4f} * x)"
            return x_fit, y_fit, eq_str, None
        except RuntimeError:
            raise ValueError("指数拟合失败，请检查数据是否适合此拟合类型")

    def perform_fit(self, x, y, fit_type):
        """执行选定的拟合类型"""
        self.fit_type = fit_type

        if fit_type == "线性":
            return self.linear_fit(x, y)
        elif "阶多项式" in fit_type:
            # 修复：正确处理中文数字
            chinese_to_number = {
                "二": 2, "三": 3, "四": 4, "五": 5
            }
            first_char = fit_type[0]
            if first_char in chinese_to_number:
                degree = chinese_to_number[first_char]
            else:
                # 如果无法识别中文数字，尝试直接转换为整数
                try:
                    degree = int(first_char)
                except ValueError:
                    raise ValueError(f"无法识别的多项式阶数: {fit_type}")

            return self.poly_fit(x, y, degree)
        elif fit_type == "玻尔兹曼":
            return self.boltzmann_fit(x, y)
        elif fit_type == "指数":
            return self.exponential_fit(x, y)
        else:
            raise ValueError(f"未知的拟合类型: {fit_type}")

    def plot_fit(self, x_data, y_data, x_fit, y_fit, equation, slope=None):
        """绘制拟合结果"""
        self.ax.clear()

        # 绘制原始数据
        self.ax.scatter(x_data, y_data, color='blue', s=30, edgecolor='black', alpha=0.7, label='数据点')

        # 绘制拟合曲线
        self.ax.plot(x_fit, y_fit, 'r-', linewidth=1.5, label=f'拟合: {equation}')

        # 设置图表属性
        self.ax.set_title(f"{self.fit_type}拟合", fontsize=12)
        self.ax.set_xlabel("X", fontsize=10)
        self.ax.set_ylabel("Y", fontsize=10)
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        self.ax.legend(fontsize=8)

        # 重绘画布
        self.canvas.draw()

        return slope