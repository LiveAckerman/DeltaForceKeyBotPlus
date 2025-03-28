import pyautogui
import time
import keyboard  # 用于监听键盘事件
import pyperclip  # 用于复制到剪切板

# 获取屏幕分辨率
screen_width, screen_height = pyautogui.size()


print("按 Ctrl+C 结束程序，按下 'c' 键打印并复制坐标数据结构")
try:
    while True:
        x, y = pyautogui.position()

        # 计算百分比（保留4位小数，例如 0.7523 表示 75.23%）
        x_percent = round(x / screen_width, 4)
        y_percent = round(y / screen_height, 4)

        # 实时显示原始坐标和百分比坐标
        print(
            f"原始坐标: X={x:<4} Y={y:<4} | "
            f"百分比坐标: X={x_percent:.2%} Y={y_percent:.2%}",
            end="\r"
        )

        # 检测是否按下 'c' 键
        if keyboard.is_pressed('c'):
            position_data = f'"position": [\n    {x_percent},\n    {y_percent}\n  ]'
            print(f'\n{position_data}')
            pyperclip.copy(position_data)  # 复制到剪切板
            print("坐标数据已复制到剪切板")
            time.sleep(0.5)  # 防止重复触发

        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n程序已终止")