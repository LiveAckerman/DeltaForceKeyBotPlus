# 本项目基于 [sheldon1998/DeltaForceKeyBot](https://github.com/sheldon1998/DeltaForceKeyBot) 上面进行修改优化的
# Q群可以一起讨论抢卡脚本技术，大家一起学习，点击链接加入群聊【牛角洲鼠鼠抢卡】：[https://qm.qq.com/q/D8kq8ZUn8](https://qm.qq.com/q/D8kq8ZUn8)
 ![Image](https://github.com/user-attachments/assets/c84ed4ce-c5f6-443d-9b71-fac868203168)

# 免责声明
免责声明
脚本仅供学习和研究目的使用，作者不对因使用该脚本而导致的任何后果负责。使用该脚本的风险完全由用户自行承担。

用户须知：

尽管脚本设计为非侵入性，但使用第三方工具可能违反目标平台的使用条款或服务协议。
使用该脚本可能导致账号被封禁或其他形式的处罚。

作者不保证脚本的稳定性、安全性或合法性。
# DeltaForceKeyBotPlus
三角洲行动拍卖行自动挂卡工具(单三跑刀巴克什匹配实在太久,所以利用匹配时间进行补卡),通过ocr+模拟鼠标点击实现自动购买钥匙卡
项目默认只配置了交易行>钥匙>巴克什 页面的的部分钥匙坐标数据,如有其他地图的钥匙可以将钥匙添加到收藏，然后通过debug.py 记录钥匙卡的位置来进行监控购买


## 开始
### 安装
注：未安装[python](https://wwjk.lanzoue.com/i22Gf2rxn75i)请先安装

## 配置
### 运行项目下的 bin/run_debug.py
![image](https://raw.githubusercontent.com/LiveAckerman/image_repository/refs/heads/main/DeltaForceKeyBotPlus/0.png)
![image](https://raw.githubusercontent.com/LiveAckerman/image_repository/refs/heads/main/DeltaForceKeyBotPlus/1.png)
![image](https://raw.githubusercontent.com/LiveAckerman/image_repository/refs/heads/main/DeltaForceKeyBotPlus/2.png)
![image](https://raw.githubusercontent.com/LiveAckerman/image_repository/refs/heads/main/DeltaForceKeyBotPlus/3.png)

## 运行
### 运行 python main.py 时 必须要用管理员黑窗口运行，否则触发不了模拟点击和按键，可以直接右键管理员运行项目下的 bin/run.bat
```
python main.py
```
F8开始抢卡,F9暂停脚本已适配不同分辨率(16:9)以及多显示器的场景
开始抢卡时需要将页面点击到买卡的区域,如下图项目默认只配置了交易行>钥匙>巴克什 页面如下图的的部分钥匙坐标数据,
![image](https://github.com/user-attachments/assets/b76727bc-d126-47a5-a3ed-964f9221d38c)

**如有其他地图的钥匙可以将钥匙添加到收藏，然后通过debug.py 记录钥匙卡的位置来进行监控购买**

## 其他说明
### debug.py
运行debug.py 实时获取鼠标坐标 如得到 58.21%,21.25% 则坐标应该为[0.5821,0.2125]，运行时 按下 'c' 键打印并复制坐标数据结构，复制坐标结构之后就可以替换到 keys.json 里面的 position 的值。

### config.json
```json
{
  // 是否循环购买,循环购买的逻辑购买成功之后不移除钥匙信息
  "is_loop":false,

  // 是否开启调 试模式，调试模式下不会自动购买钥匙，方便调试，默认为true，防止购买错
  "is_debug":true,

  // 钥匙卡名称的识别文字范围，通过debug.py可进行配置
  "card_name_range": [
    1969,
    209,
    166,
    40
  ],

  // 钥匙卡价格的识别文字范围，通过debug.py可进行配置
  "card_price_range": [
    1978,
    1367,
    395,
    69
  ],

  // 需要抢钥匙卡的信息数组
  "keys":[
    {
        "name": "总裁会议室", //  目标卡牌名称，需与游戏保持一致，如果识别中文有问题，或者识别错了比如 总裁会议室 识别成了 总载会议室   之类的，可以在这里修改成数组，["总裁会议室", "总载会议室"]

        "floating_percentage_range": 100000, // 价格浮动范围，单位为分，默认100000，表示10w的浮动范围，逻辑就是  ideal_price +  floating_percentage_range > 识别到当前卡的价格 也会购买

        "ideal_price": 3000000, // 钥匙卡的理想价格，识别到当前的价格小于理想价格时就会购买

        "position": [
          0.5926,
          0.1963
        ], // 钥匙卡的坐标通过 debug.py 脚本获取

        "want_buy": 1 // 是否购买，1为购买，0为不购买
      }
  ]
}
```

### 购买逻辑

1. 当前价格小于理想购买价格,自动购买
2. 卡牌溢价 floating_percentage_range 百分比范围以内,自动购买
3. 卡牌负溢价,自动购买
