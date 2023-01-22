from machine import Pin, SPI, RTC
import newframebuf
import framebuf
import time
import epaper4in2
import ntptime
import network


# 记录上次矩形的左上角
last_rect_x = 0
last_rect_y = 0
# 记录上次显示的所有数字左上角
last_number_x_y = []


def get_week_with_data(y,m,d):
    '''根据年月日计算星期几'''
    y = y - 1 if m == 1 or m == 2 else y
    m = 13 if m == 1 else (14 if m == 2 else m)
    w = (d + 2 * m + 3 * (m + 1) // 5 + y + y // 4 - y // 100 + y // 400) % 7 + 1
    return w


def is_leap_year(y):
    if y%400==0 or (y%4==0 and y%100!=0):
        return True
    return  False


def get_days_in_month(y,m):
    if m in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif m in [4, 6, 9, 11]:
        return 30
    else:
        return 29 if is_leap_year(y) else 28
    

def connect_wifi(wifi, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(wifi, password)


def ntp():
    # 链接互联网
    connect_wifi("zchwifi", "zch18808195996")
    time.sleep(2)
    ntptime.host="ntp1.aliyun.com"
    ntptime.NTP_DELTA = 3155644800  # 东八区 UTC+8偏移时间（秒）
    try:
        ntptime.settime()
        print("联网成功...")
    except Exception as e:
        pass

def show_time(hour, minute):
    a=hour
    b=minute
    fb.hline(0, 180, 330, black)
    fb.text(a, 20, 200, black, size=2)
    fb.text(b, 60, 200, black, size=2)
    #fb.pixel(100, 200) 显示像素点
    
    e.display_frame(buf)  # 刷新显示

def show_text(year, month, day):
    global last_rect_x, last_rect_y, last_number_x_y
    
    # 清空上次显示的数字
    for content, x, y in last_number_x_y:
        fb.text(content, x, y, white,size=2)
        
    # 清空列表
    last_number_x_y = []
    
    # 1.提示用户输入年月
    year = year
    mouth = month
    # 2.计算这个月有多少天
    days = get_days_in_month(year, mouth)
    # 3.按照指定格式显示日期
    print('一 二 三 四 五 六 日')
    fb.text(' Mon Tus Wed Thu Fri Sat Sun', 0, 15, black, size=2)
    content = '-' * 30
    print(content)
    # fb.text(content, 0, 30, black)
    fb.hline(0, 30, 330, black)
    content = ""
    row = 3
    today_row = 0
    today_col = 0
    for i in range(1, days + 1):
        w = get_week_with_data(year, mouth, i)

        if i == 1:
            content = content + '    ' * (w-1)
            # print(content, end="*")
            
        else:
            if w == 1:
                print(content)
                fb.text(content, 0, row * 15 - 5, black, size=2)
                last_number_x_y.append([content, 0, row * 15 - 5])
                row += 2
                content = ""
        content = content + f"  {i:2d}"
        
        if i == day:
            today_row = row
            today_col = w

    if content:
        print(content)
        fb.text(content, 0, row * 15 - 5, black, size=2)
        last_number_x_y.append([content, 0, row * 15 - 5])
    
    rect_x = 2*((today_col - 1) * 25 + 5)
    rect_y = today_row * 15 - 8
    

    if last_rect_x != 0 and last_rect_y != 0:
        print("last_rect_x=%d, last_rect_y=%d" % (last_rect_x, last_rect_y))
        fb.rect(last_rect_x, last_rect_y, 22, 14, white)
    
    last_rect_x, last_rect_y = rect_x, rect_y

    fb.rect(rect_x, rect_y,  50, 24, black)
    
    # fb.text('hello World', 0, 0, black, size=2)
    e.display_frame(buf)  # 刷新显示


if __name__ == "__main__":
    # 1. 创建对应的引脚
    sck = Pin(13)
    miso = Pin(19)
    mosi = Pin(14)
    dc = Pin(27)
    cs = Pin(15)
    rst = Pin(26)
    busy = Pin(25)
    spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)

    e = epaper4in2.EPD(spi, cs, dc, rst, busy)
    e.init()

    # 3. 导入需要的背景图
    #from image_miao import imagemiao

    # 4. 定义要显示的内容宽度高度
    w = 400
    h = 300
    # 注意：实际的图片多大这里就写多大
    #buf = imagemiao
    buf = bytearray(w * h // 8)  # 296 * 128 // 8 = 4736 空白
    black = 0
    white = 1
    
    # 5. 以背景图为基础创建缓存区
    fb = newframebuf.FrameBuffer(buf, w, h, newframebuf.MHMSB)
    fb.fill(white)  # 清空内容
    fb.rotation = 0  # 调整显示的方向，可以在0/1/2/3之间选择
    
    # 6. 联网 便于获取互联网时间
    rtc = RTC()
    ntp()

    # 7. 显示文字
    date = rtc.datetime()
    show_text(date[0], date[1], date[2])  # 年月日
    
		# 8.显示时间文字
    h=str(date[4])
    m=str(date[5])
    show_time(h,m)
    print(h)
    print(m)