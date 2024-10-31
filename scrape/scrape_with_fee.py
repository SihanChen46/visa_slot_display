from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
import logging
from datetime import datetime

# 创建日志记录器
logger = logging.getLogger('appointment_logger')
logger.setLevel(logging.INFO)

# 创建文件处理器并设置追加模式
file_handler = logging.FileHandler('data/appointment_log.txt', mode='a')
file_handler.setLevel(logging.INFO)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
if not logger.hasHandlers():
    logger.addHandler(file_handler)

# 设置 ChromeDriver 的路径
# chrome_driver_path = './chromedriver-mac-arm64/chromedriver'  # 替换为你的 ChromeDriver 路径
chrome_driver_path = './chromedriver-mac-x64/chromedriver'  # 替换为你的 ChromeDriver 路径
url = 'https://ais.usvisa-info.com/en-bb/niv/schedule/63315832/appointment'  # 替换为你页面的实际 URL

# 登录信息
email = "sihanchen46@gmail.com"
password = "Chen+961226"

# 新增：标记是否已经预约成功
appointment_scheduled = False

# 定义目标日期范围
target_start = datetime(2024, 11, 25)
target_end = datetime(2024, 11, 25)

# 新增：定义最大日期（一直查到明年4月）
max_date = datetime(2025, 4, 30)

while True:
    try:
        # 启动 Chrome 浏览器
        options = Options()
        options.add_argument("--start-maximized")  # 浏览器最大化
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        # 打开网页
        driver.get(url)

        # 等待页面加载完成
        time.sleep(10)

        # 点击 OK 按钮
        try:
            ok_button = driver.find_element(By.CSS_SELECTOR, 'button.ui-button.ui-corner-all.ui-widget')
            ok_button.click()
            print("点击了 OK 按钮")
            time.sleep(2)  # 等待页面反应
        except Exception as e:
            print(f"点击 OK 按钮时发生错误: {e}")

        # 自动登录逻辑
        try:
            # 输入账号（email）
            email_input = driver.find_element(By.ID, 'user_email')
            email_input.send_keys(email)
            
            # 输入密码
            password_input = driver.find_element(By.ID, 'user_password')
            password_input.send_keys(password)
            
            # 勾选复选框（同意条款）
            checkbox_div = driver.find_element(By.CSS_SELECTOR, 'div.icheckbox.icheck-item')
            checkbox_div.click()
            
            # 点击登录按钮
            login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Sign In"]')
            login_button.click()

            print("已提交登录信息，等待页面加载...")
            time.sleep(10)  # 等待登录后的页面加载完成
        except Exception as e:
            print(f"登录时发生错误: {e}")

        # 登录完成后继续执行自动化操作
        print("登录完成，继续执行脚本...")

        # 无限循环，每 5 分钟刷新页面
        while True:
            # 打开日期选择器
            date_input = driver.find_element(By.ID, 'appointments_consulate_appointment_date')
            date_input.click()
            time.sleep(10)

            # 初始化当前日期
            current_year = None
            current_month = None

            # 循环遍历月份，直到达到最大日期
            while True:
                # 获取当前月份和年份
                month_element = driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div[1]//span[@class="ui-datepicker-month"]')
                year_element = driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div[1]//span[@class="ui-datepicker-year"]')
                current_month_text = month_element.text
                current_year = int(year_element.text)

                # 将月份的文本转换为数字
                month_map = {
                    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
                }
                current_month = month_map[current_month_text]
                current_date = datetime(current_year, current_month, 1)

                print(f"当前月份：{current_month_text} {current_year}")

                # 检查是否超过最大日期
                if current_date > max_date:
                    print("已达到最大日期，结束本次循环。")
                    break

                # 查找当前显示月份中的所有可用日期
                available_dates = driver.find_elements(By.XPATH, '//*[@id="ui-datepicker-div"]/div[1]//a[@class="ui-state-default"]')

                if available_dates:
                    logger.info(f"{current_year} - {current_month}找到可用日期：{[datetime(current_year, current_month, int(d.text)).strftime('%Y-%m-%d') for d in available_dates]}")
                    for date_element in available_dates:
                        date_text = date_element.text
                        date_day = int(date_text)
                        # 构造完整日期对象
                        found_date = datetime(current_year, current_month, date_day)

                        # 如果找到的日期是目标范围内的日期，且还未预约，立即预约
                        if not appointment_scheduled and target_start <= found_date <= target_end:
                            logger.info(f"找到符合条件的日期：{found_date.strftime('%Y-%m-%d')}")
                            
                            # 点击目标日期
                            date_element.click()
                            time.sleep(10)

                            # 选择第一个可用时间
                            time_dropdown = Select(driver.find_element(By.ID, 'appointments_consulate_appointment_time'))
                            time_dropdown.select_by_index(1)
                            logger.info("已选择第一个时间选项")
                            time.sleep(10)
                            
                            # 点击 "Schedule Appointment" 按钮
                            schedule_button = driver.find_element(By.ID, 'appointments_submit')
                            schedule_button.click()
                            logger.info(f"预约成功: {found_date.strftime('%Y-%m-%d')}")
                            
                            # 标记为已预约
                            appointment_scheduled = True
                            time.sleep(60)
                            # 返回到预约页面以继续监控
                            driver.get(url)
                            time.sleep(10)
                            break  # 跳出日期循环

                # 尝试点击下一页
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, "a.ui-datepicker-next")
                    if next_button.is_displayed():
                        next_button.click()
                        print("点击了下一页按钮...")
                        time.sleep(5)
                    else:
                        print("没有下一页按钮，结束查找。")
                        break
                except:
                    print("没有下一页按钮，结束查找。")
                    break

            # 等待5分钟，然后刷新页面
            print("等待5分钟后刷新页面...")
            time.sleep(285)
            driver.refresh()
            time.sleep(15)


    except Exception as e:
        logger.error(f"脚本发生错误: {e}")
        print("发生错误，等待 5 分钟后重试...")
        time.sleep(285)  # 等待 5 分钟后重新尝试
        driver.quit()