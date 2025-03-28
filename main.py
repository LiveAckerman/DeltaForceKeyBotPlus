import json
import pyautogui
import time
from PIL import Image
import pytesseract
import winsound
import os
import keyboard  # 用于监听键盘事件
import datetime  # 添加 datetime 模块
import re  # 添加正则表达式模块

# 配置部分
CONFIG_FILE = 'config.json'

# Tesseract 环境配置
os.environ["LANGDATA_PATH"] = r"D:\my_project\DeltaForceKeyBotPlus\tessdata-4.1.0"
os.environ["TESSDATA_PREFIX"] = r"D:\my_project\DeltaForceKeyBotPlus\tessdata-4.1.0"
pytesseract.pytesseract.tesseract_cmd = r'E:\Program Files\Tesseract-OCR\tesseract.exe'

# 全局变量
keys_config = None
isLoop = False # 是否循环购买
isDebug = False # 是否开启调试模式
is_running = False  # 控制循环是否运行
is_paused = False   # 控制循环是否暂停
screen_width, screen_height = pyautogui.size()

import re  # 添加正则表达式模块

def load_keys_config():
    """加载钥匙价格配置文件（只读取一次）"""
    global keys_config
    if keys_config is not None:
        return keys_config  # 如果已经加载过，直接返回

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            # 移除注释
            content = f.read()
            # 使用正则表达式移除以 // 或 # 开头的注释
            content = re.sub(r'//.*|#.*', '', content)
            config = json.loads(content)  # 解析为 JSON
            keys_config = config.get('keys', [])
            isLoop = config.get('isLoop')
            isDebug = config.get('isDebug')
            print(f"isDebug: {isDebug}")
            print(f"isLoop: {isLoop}")
            return keys_config
    except FileNotFoundError:
        print(f"[错误] 配置文件 {CONFIG_FILE} 不存在")
        return []
    except json.JSONDecodeError as e:
        print(f"[错误] 配置文件 {CONFIG_FILE} 格式错误: {e}")
        return []
    except Exception as e:
        print(f"[错误] 读取配置时发生未知错误: {str(e)}")
        return []

def take_screenshot(region, threshold):
    """截取指定区域的截图并二值化"""
    screenshot = pyautogui.screenshot(region=region)
    gray_image = screenshot.convert('L')
    binary_image = gray_image.point(lambda p: 255 if p > threshold else 0)
    binary_image = Image.eval(binary_image, lambda x: 255 - x)
    screenshot.close()
    return binary_image

def getCardPrice():
    """获取当前卡片价格，仅识别阿拉伯数字"""
    region_width = int(screen_width * 0.08)  # 区域宽度为屏幕宽度的 8%
    region_height = int(screen_height * 0.037)  # 区域高度为屏幕高度的 4%
    region_left = int(screen_width * 0.851)
    region_top = int(screen_height * 0.805)

    region = (region_left, region_top, region_width, region_height)

    image = take_screenshot(region=region, threshold=55)
    image.save("./image.png")
    text = pytesseract.image_to_string(image, lang='eng', config="--psm 13 -c tessedit_char_whitelist=0123456789")
    print(f"原始文本: {text}")

    # 如果第一个字符是 '0'，则移除它
    text = text.replace(",", "") # 去除逗号
    text = text.replace(" ", "") # 去除空格

    # 因为会截取到价格左边的哈夫币logo，会被识别成 0，所以需要去掉
    if text.startswith('0'):
        text = text[1:]
    try:
        price = int(text)
        print(f"提取的价格文本: {price}")
        return price
    except ValueError:
        print("无法解析价格")
        return None

def getCardName():
  """获取当前卡片名称"""
  screen_width, screen_height = pyautogui.size()
  region_width = int(screen_width * 0.1)  # 区域宽度为屏幕宽度的 10%
  region_height = int(screen_height * 0.05)  # 区域高度为屏幕高度的 10%
  region_left = int(screen_width * 0.768)
  region_top = int(screen_height * 0.143)
  region = (region_left, region_top, region_width, region_height)

  screenshot = take_screenshot(region=region, threshold=100)
  screenshot.save("./s.png")
  # 使用更适合中文识别的配置
  text = pytesseract.image_to_string(
    screenshot,
    lang='chi_sim',  # 指定简体中文语言
    config="--psm 7"  # 配置页面分割模式为 7（单行文本）
  )
  text = text.replace(" ", "").strip()  # 清理空格和换行符
  return text

def log_purchase(card_name, ideal_price, price, premium):
    """记录购买信息到 logs.txt"""
    log_entry = f"购买时间：{datetime.datetime.now():%Y-%m-%d %H:%M:%S} | 卡片名称: {card_name} | 理想价格: {ideal_price} | 购买价格: {price} | 溢价: {premium:.2f}%\n"
    with open("logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

def price_check_flow(card_info):
    """价格检查主流程"""
    global is_paused
    esc_pressed = False  # 标志变量，确保只按一次 Esc

    # 移动到卡牌位置并点击
    position = card_info.get('position')
    pyautogui.moveTo(position[0] * screen_width, position[1] * screen_height)
    pyautogui.click()
    time.sleep(0.1)  # 减少延迟时间

    try:
        card_name = getCardName().strip()
        current_price = getCardPrice()
        if current_price is None:
            print("无法获取有效价格，跳过本次检查")
            if not esc_pressed:
                pyautogui.press('esc')  # 按 Esc 取消
                esc_pressed = True
            return False
    except Exception as e:
        print(f"获取门卡信息失败: {str(e)}")
        if not esc_pressed:
            pyautogui.press('esc')  # 按 Esc 取消
            esc_pressed = True
        return False

    # base_price = card_info.get('base_price', 0)
    floating_percentage_range = card_info.get('floating_percentage_range', 0.1)
    ideal_price = card_info.get('ideal_price', 0)

    max_price = ideal_price + (ideal_price * floating_percentage_range)

    premium = ((current_price / ideal_price) - 1) * 100

    check_card_name = card_info.get("name")
    print(f"当前门卡:{card_name}\n需要购买的卡:{check_card_name}")
    if card_name not in check_card_name:
        if not esc_pressed:
            pyautogui.press('esc')
            esc_pressed = True
        print("需要购买的卡与点击的卡不符，已返回上一层")
        return False

    print(f"理想价格: {ideal_price}  | 最高溢价：{max_price} | 差价: {current_price - ideal_price} | 当前价格/溢价%: {current_price}/{premium:.2f}%")

    if premium < 0 or current_price < max_price:
        pyautogui.moveTo(screen_width * 0.825, screen_height * 0.852)
        if not isDebug:
          print("正在购买...")
          # pyautogui.click()  # 点击购买

        print(f"[+]已自动购买{card_name},理想价格为：{ideal_price},购买价格为：{current_price},溢价：{premium:.2f}%")
        log_purchase(card_name, ideal_price, current_price, premium)  # 调用日志记录函数
        time.sleep(0.5)  # 避免重复操作
        if not esc_pressed:
            pyautogui.press('esc')  # 立即返回上一层
            esc_pressed = True
        return True
    else:
        print(">> 价格过高，重新刷新价格 <<\n\n")
        if not esc_pressed:
            pyautogui.press('esc')  # 按 Esc 取消
            esc_pressed = True
        return False

def start_loop():
    """开始循环"""
    global is_running, is_paused
    is_running = True
    is_paused = False
    print("循环已启动")

def stop_loop():
    """停止循环"""
    global is_running, is_paused
    is_running = False
    is_paused = False
    print("循环已停止")

def main():
    global is_running, is_paused

    # 初始化时加载配置
    keys_config = load_keys_config()
    if not keys_config:
        print("无法加载配置文件，程序退出")
        return

    # 过滤出需要购买的卡牌
    cards_to_buy = [card for card in keys_config if card.get('want_buy', 0) == 1]
    if not cards_to_buy:
        print("没有需要购买的门卡，程序退出")
        return
    for card in cards_to_buy:
        print(f"当前需要购买: {card['name']}")
    # 监听键盘事件
    keyboard.add_hotkey('f8', start_loop)  # 按 F8 开始循环
    keyboard.add_hotkey('f9', stop_loop)   # 按 F9 停止循环

    print("按 F8 开始循环，按 F9 停止循环")

    while True:
        if is_running and not is_paused:
            for card_info in cards_to_buy:
                if not is_running:
                    break
                print(f"正在检查门卡: {card_info['name']}")
                if price_check_flow(card_info):
                  print(f"isDebug {isDebug}")
                  print(f"isLoop {isLoop}")
                  if not isLoop:
                    cards_to_buy.remove(card_info)
                    print(f"剩余购买队列：{cards_to_buy}")
                  continue
                time.sleep(0.1)
        elif is_paused:
            print("循环已暂停，等待手动恢复...")
            time.sleep(1)
        else:
            time.sleep(0.1)  # 空闲时降低 CPU 占用

if __name__ == "__main__":
    main()
