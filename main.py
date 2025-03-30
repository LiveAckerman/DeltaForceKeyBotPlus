import json
import pyautogui
import time
from PIL import Image
import pytesseract
import os
import keyboard
import datetime
import re
import cv2
import numpy as np

# 配置部分
CONFIG_FILE = 'config.json'

# Tesseract 环境配置
os.environ["LANGDATA_PATH"] = r"D:\my_project\DeltaForceKeyBotPlus-main\tessdata-4.1.0"
os.environ["TESSDATA_PREFIX"] = r"D:\my_project\DeltaForceKeyBotPlus-main\tessdata-4.1.0"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 全局变量
keys_config = None
purchase_btn_location = None  # 新增变量
is_loop = False
is_debug = True
is_running = False
is_paused = False
screen_width, screen_height = pyautogui.size()


def ensure_images_folder_exists():
    """确保 images 文件夹存在"""
    if not os.path.exists("./images"):
        os.makedirs("./images")


def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"[错误] 配置文件 {CONFIG_FILE} 不存在")
        return {}
    except json.JSONDecodeError as e:
        print(f"[错误] 配置文件 {CONFIG_FILE} 格式错误: {e}")
        return {}
    except Exception as e:
        print(f"[错误] 读取配置时发生未知错误: {str(e)}")
        return {}


def get_region_from_config(config, key):
    """从配置文件中获取区域"""
    region = config.get(key)
    if not region or len(region) != 4:
        print(f"[错误] 配置文件中缺少有效的 {key} 字段，请检查配置文件")
        return None
    return tuple(region)


def take_screenshot(region, threshold):
    """截取指定区域的截图并二值化"""
    try:
        screenshot = pyautogui.screenshot(region=region)
        gray_image = screenshot.convert('L')
        binary_image = gray_image.point(lambda p: 255 if p > threshold else 0)
        binary_image = Image.eval(binary_image, lambda x: 255 - x)
        screenshot.close()
        return binary_image
    except Exception as e:
        print(f"[错误] 截图失败: {str(e)}")
        return None


def get_card_price(config):
    """获取当前卡片价格，仅识别阿拉伯数字"""
    region = get_region_from_config(config, "card_price_range")
    if not region:
        return None

    image = take_screenshot(region=region, threshold=55)
    if not image:
        return None

    image.save("./images/card_price.png")
    text = pytesseract.image_to_string(image, lang='eng', config="--psm 13 -c tessedit_char_whitelist=0123456789")
    text = text.replace(",", "").replace(" ", "")

    if text.startswith('0'):
        text = text[1:]
    try:
        price = int(text)
        print(f"提取的价格文本: {price}")
        return price
    except ValueError:
        print("无法解析价格")
        return None


def get_card_name(config):
    """获取当前卡片名称"""
    region = get_region_from_config(config, "card_name_range")
    if not region:
        return None

    screenshot = take_screenshot(region=region, threshold=100)
    if not screenshot:
        return None

    screenshot.save("./images/card_name.png")

    text = pytesseract.image_to_string(
        screenshot,
        lang='chi_sim',
        config="--psm 7"
    )
    return text.replace(" ", "").strip()


def log_purchase(card_name, ideal_price, price, premium):
    """记录购买信息到 logs.txt"""
    log_entry = f"购买时间：{datetime.datetime.now():%Y-%m-%d %H:%M:%S} | 卡片名称: {card_name} | 理想价格: {ideal_price} | 购买价格: {price} | 溢价: {premium:.2f}%\n"
    with open("logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)


def price_check_flow(card_info, config):
    """价格检查主流程"""
    global is_debug, purchase_btn_location
    position = card_info.get('position')
    if not position or len(position) != 2:
        print(f"[错误] 卡片 {card_info.get('name')} 的 position 配置无效")
        return False

    pyautogui.moveTo(position[0] * screen_width, position[1] * screen_height)
    pyautogui.click()
    time.sleep(0.1)

    card_name = get_card_name(config)
    if not card_name:
        print("无法获取卡片名称，跳过本次检查")
        pyautogui.press('esc')
        return False

    current_price = get_card_price(config)
    if current_price is None:
        print("无法获取有效价格，跳过本次检查")
        pyautogui.press('esc')
        return False

    floating_percentage_range = card_info.get('floating_percentage_range', 0.1)
    ideal_price = card_info.get('ideal_price', 0)
    max_price = ideal_price + (ideal_price * floating_percentage_range)
    premium = ((current_price / ideal_price) - 1) * 100

    if card_name not in card_info.get("name", ""):
        print("需要购买的卡与点击的卡不符，已返回上一层")
        pyautogui.press('esc')
        return False

    print(f"理想价格: {ideal_price} | 最高价格: {max_price} | 当前价格: {current_price} | 溢价: {premium:.2f}%")

    if premium < 0 or current_price < max_price:
        pyautogui.moveTo(screen_width * purchase_btn_location[0], screen_height * purchase_btn_location[1])
        if not is_debug:
            print("点击购买")
        #     pyautogui.click()
        log_purchase(card_name, ideal_price, current_price, premium)
        pyautogui.press('esc')
        return True
    else:
        print("价格过高，重新刷新价格")
        pyautogui.press('esc')
        return False


def main():
    global is_running, is_paused, is_loop, is_debug, purchase_btn_location

    # 加载配置文件
    config = load_config()

    # 从配置文件中获取 purchase_btn_location 的值
    purchase_btn_location = config.get("purchase_btn_location", [0.825, 0.86])

    # 从配置文件中获取 is_debug 和 is_loop 的值
    is_debug = config.get("is_debug", True)  # 默认值为 False
    is_loop = config.get("is_loop", False)    # 默认值为 False

    # 获取 keys 配置
    keys_config = config.get("keys", [])
    if not keys_config:
        print("配置文件中没有找到有效的 keys 配置，程序退出")
        return

    # 筛选需要购买的卡片
    cards_to_buy = [card for card in keys_config if card.get('want_buy', 0) == 1]
    if not cards_to_buy:
        print("没有需要购买的门卡，程序退出")
        return

    for card in cards_to_buy:
        print(f"当前需要购买: {card['name']}")

    # 使用 lambda 函数直接修改全局变量
    keyboard.add_hotkey('f8', lambda: set_running_state(True))
    keyboard.add_hotkey('f9', lambda: set_running_state(False))

    print("按 F8 开始循环，按 F9 停止循环")

    while True:
        if is_running:
            # 确保 images 文件夹存在
            ensure_images_folder_exists()

            for card_info in cards_to_buy:
                if not is_running:
                    break
                print(f"正在检查门卡: {card_info['name']}")
                if price_check_flow(card_info, config):
                    if not is_loop:
                        cards_to_buy.remove(card_info)
                    print(f"剩余购买队列：{[card['name'] for card in cards_to_buy]}")
                time.sleep(0.1)
        else:
            time.sleep(0.1)


def set_running_state(state):
    """设置全局变量 is_running 的状态"""
    global is_running
    is_running = state


if __name__ == "__main__":
    main()