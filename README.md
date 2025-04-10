# 本项目基于 [sheldon1998/DeltaForceKeyBot](https://github.com/sheldon1998/DeltaForceKeyBot) 上面进行修改优化的
## Q群可以一起讨论抢卡脚本技术，大家一起学习，点击链接加入群聊【牛角洲鼠鼠抢卡】：[https://qm.qq.com/q/D8kq8ZUn8](https://qm.qq.com/q/D8kq8ZUn8)
<img src="https://github.com/user-attachments/assets/c84ed4ce-c5f6-443d-9b71-fac868203168" alt="Image" height="400">

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
目前是这样的3个部分
config.json
调整你想要的卡的匹配名字
调整是否循环购买
调整购买数量
调整是否真的购买
调整购入预期金额
debug.py
调整你要买的卡在游戏交易行的多卡界面中的位置（区域卡界面）
调整你要买的卡的名字读取位置（目的是和config中的卡名字一样才会购买）（具体卡界面）
调整你要买的卡的价格读取位置（目的是低于config中的购入预期才会买）（具体卡界面）
调整你点击购买卡的位置（具体卡界面）
main.py
运行主程序
显示你在config中设置want to buy为1的所有卡
按f8执行抢卡流程  f9暂停


### debug.py
运行debug.py 实时获取鼠标坐标 如得到 58.21%,21.25% 则坐标应该为[0.5821,0.2125]，运行时 按下 'c' 键打印并复制坐标数据结构，复制坐标结构之后就可以替换到 keys.json 里面的 position 的值。

### config.json
```json
{
  // 是否循环购买,循环购买的逻辑购买成功之后不移除钥匙信息   可选值 true 就是一直循环抢，false 就是只抢一次
  "is_loop":false,

  // 是否开启调 试模式，调试模式下不会自动购买钥匙，方便调试，默认为true，防止购买错，false 就是会购买
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

        "floating_percentage_range": 0.1, // 价格浮动范围，单位为百分比，默认0.1，计算逻辑 floating_percentage_range + (ideal_price * floating_percentage_range) 比如是 价格是 3000000，那就是 3000000 + (3000000 * 0.1) = 3300000 ,那么购买的价格范围就是 3000000 - 3300000 之间都会购买

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
