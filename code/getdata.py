from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from openpyxl import workbook
import re

baseurl = 'https://s.weibo.com/weibo?q='
#搜索关键字↓
searchword = '新冠肺炎'

if __name__ == "__main__":

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.set_headless()
    driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', chrome_options=chrome_options)
    # driver = webdriver.Firefox()

    # 手动登录
    driver.get('https://weibo.com/')
    print('请再3分钟内完成登录！')
    try:
        WebDriverWait(driver, 180).until(EC.title_is('我的首页 微博-随时随地发现新鲜事'))
        print('登录成功')
    except:
        print('未登录')

    wb = workbook.Workbook()
    ws = wb.active
    #爬50页
    for page in range(1,51):
        print("正在爬取第"+  str(page) +'页')

        driver.get(baseurl + searchword + '&page=' + str(page))


        #展开全文
        js="pp = document.getElementsByClassName('txt')\n var i\n for(i=0;i<pp.length;i++)\n { pp[i].style.display=''}"
        driver.execute_script(js)

        card_feeds = driver.find_elements_by_class_name('card-feed')

        for card_feed in card_feeds:
            content = card_feed.find_element_by_class_name('content')

            text = ''
            ps = content.find_elements_by_class_name('txt')
            for p in ps:
                # print(p.text)
                text = p.text
                if 'feed_list_content_full' in p.get_attribute('node-type'):
                    # print("###"+p.text)
                    text = p.text
                    break


            # print(text)
            
            line_list = []
            line_list.append(text)

            imgs = content.find_elements_by_tag_name('img')
            for img in imgs:
                imgurl = img.get_attribute('src')
                #png图片不保存
                if 'png' not in imgurl:
                    # print(imgurl)
                    line_list.append(imgurl)
            ws.append(line_list)


    wb.save("url.xlsx")
   
    # driver.close()