import pyautogui
import keyboard
import json

CONFIG_FILE = "config.json"  # 配置文件路径

# 获取屏幕分辨率
screen_width, screen_height = pyautogui.size()

def load_config(file_path=CONFIG_FILE):
    """加载配置文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件 {file_path} 未找到！")
        return {}
    except json.JSONDecodeError as e:
        print(f"配置文件解析错误: {e}")
        return {}

def save_config(config, file_path=CONFIG_FILE):
    """保存配置文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    print(f"配置文件已保存到 {file_path}")

def select_region(region_name):
    """让用户手动框选区域"""
    print(f"请手动框选 {region_name} 区域：")
    print("将鼠标移动到区域左上角并按下空格键...")
    keyboard.wait('space')  # 等待用户按下空格键
    top_left = pyautogui.position()  # 用户按下空格键后记录左上角坐标

    print("将鼠标移动到区域右下角并按下空格键...")
    keyboard.wait('space')  # 等待用户按下空格键
    bottom_right = pyautogui.position()  # 用户按下空格键后记录右下角坐标

    # 计算宽度和高度
    width = bottom_right.x - top_left.x
    height = bottom_right.y - top_left.y

    # 返回 (x, y, width, height)
    region = [
        top_left.x,
        top_left.y,
        width,
        height
    ]
    print(f"{region_name} 区域已选择：{region}")
    return region

def configure_card_regions(config):
    """配置钥匙卡的名称和价格区域"""
    while True:
        print("\n请选择要框选的区域：")
        print("1. 钥匙卡的名称区域")
        print("2. 钥匙卡的价格区域")
        print("0. 返回上一层")
        choice = input("请输入选项编号（0、1 或 2）：").strip()

        if choice == "1":
            region_name = "钥匙卡的名称区域"
            key = "card_name_range"
        elif choice == "2":
            region_name = "钥匙卡的价格区域"
            key = "card_price_range"
        elif choice == "0":
            print("返回上一层...")
            break
        else:
            print("无效的选项，请重新输入。")
            continue

        # 让用户框选区域
        region = select_region(region_name)

        # 保存到配置文件
        config[key] = region
        save_config(config)

def configure_card_positions(config):
    """配置钥匙卡的位置"""
    keys = config.get("keys", [])

    if not keys:
       print("配置文件中没有找到 keys 数组！")
    else:
      while True:
          print("\n请选择要设置 position 的卡片：")
          for i, key in enumerate(keys, start=1):
              print(f"{i}. {key['name']}")  # 显示卡片名称
          print("0. 返回上一层")

          choice = input("请输入卡片编号（0-{}）：".format(len(keys))).strip()

          if choice == "0":
              print("返回上一层...")
              break

          if not choice.isdigit() or int(choice) < 1 or int(choice) > len(keys):
              print("无效的选项，请重新输入。")
              continue

          card_index = int(choice) - 1
          card = keys[card_index]

          print(f"请将鼠标移动到 {card['name']} 的位置并按下空格键...")
          keyboard.wait('space')  # 等待用户按下空格键
          x, y = pyautogui.position()

          # 计算百分比（保留4位小数）
          x_percent = round(x / screen_width, 4)
          y_percent = round(y / screen_height, 4)

          # 更新 position 值
          card["position"] = [x_percent, y_percent]
          print(f"{card['name']} 的 position 已更新为: {card['position']}")

          # 更新配置中的卡片信息
          config["keys"][card_index] = card

          # 保存到配置文件
          save_config(config)

def configure_purchase_button(config):
    """配置购买按钮的位置"""
    print("请将鼠标移动到购买按钮的位置并按下空格键...")
    keyboard.wait('space')  # 等待用户按下空格键
    x, y = pyautogui.position()

    # 计算百分比（保留4位小数）
    x_percent = round(x / screen_width, 4)
    y_percent = round(y / screen_height, 4)

    # 更新 purchase_btn_location 值
    config["purchase_btn_location"] = [x_percent, y_percent]
    print(f"购买按钮的位置已更新为: {config['purchase_btn_location']}")

    # 保存到配置文件
    save_config(config)

def main():
    config = load_config()

    while True:
        print("\n请选择要执行的操作：")
        print("1. 配置钥匙卡名称和价格位置")
        print("2. 配置钥匙卡位置")
        print("3. 配置购买按钮位置")  # 新增选项
        print("0. 退出程序")
        choice = input("请输入选项编号（0、1、2 或 3）：").strip()

        if choice == "1":
            configure_card_regions(config)
        elif choice == "2":
            configure_card_positions(config)
        elif choice == "3":  # 新增选项处理
            configure_purchase_button(config)
        elif choice == "0":
            print("程序已退出。")
            break
        else:
            print("无效的选项，请重新输入。")

if __name__ == "__main__":
    main()