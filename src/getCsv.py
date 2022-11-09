#!/usr/bin/env python3

from posixpath import split
from typing import List
import json
import pandas as pd
from bs4 import BeautifulSoup as bs
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import datetime
import chromedriver_binary 

class Selenium():
    def __init__(self):
        self.driver = self.__open_chrome()
        self.item_list = {}

    # GoogleChromeを起動
    def __open_chrome(self) -> webdriver: 
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('prefs', {
            'download.prompt_for_download': False,
        })
        driver = webdriver.Chrome(chrome_options=options)
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        driver.execute("send_command", {
            'cmd': 'Page.setDownloadBehavior',
            'params': {
                'behavior': 'allow',
                'downloadPath': './csv/'
            }
        })
        return driver

    # 指定したURLを開く
    def open_url(self, url) -> None:
        self.driver.get(url)

    # driverのhtmlを取得
    def get_source(self) -> str:
        html_text = self.driver.page_source
        self.driver.implicitly_wait(10)
        return html_text

    # numページ分の商品を取得
    def get_item_list_sumpage(self, num):
        for _ in range(num):
            html_text = self.get_source()
            self.__get_item_list(html_text)
            self.__next_item_page(html_text)


    # 開いているamazonページから商品リストを取得
    def __get_item_list(self, html_text) -> list:
        soup = bs(html_text, 'html.parser')
        for item in soup.select(".s-title-instructions-style > .a-size-mini > .a-link-normal"):
            try:
                name = item.find("span").text
                if name not in self.item_list:
                    self.item_list[name] = item.get("href")
            except AttributeError:
                pass
        print(f"商品数{len(self.item_list)}")

    # 商品一覧ページを1ページ進める
    def __next_item_page(self, html_text):
        soup = bs(html_text, 'html.parser')
        url = soup.select(".s-pagination-next")[0].get("href")
        url = f"https://www.amazon.co.jp/{url}"
        self.open_url(url)
        
    # item_listの全商品のレビューを取得
    def get_review(self):
        df_review = pd.DataFrame(index=[], columns=["商品名", "値段", "レビュー"], dtype=object)

        for name, url in self.item_list.items():
            url = f"https://www.amazon.co.jp/{url}"
            self.open_url(url)
            html_text = self.get_source()
            soup = bs(html_text, 'html.parser')
            price = soup.select(".a-price > .a-offscreen")[0].text[1:]

            for review in soup.select(".review-text-content > span"):
                review = review.text
                series = pd.Series([name, price, review], index=df_review.columns)
                df_review = df_review.append(series, ignore_index=True)
        
        self.__out_csv(df_review)

    def __out_csv(self, df):
        df.to_csv("./csv/amazon_review.csv", index=False)

    def close_driver(self):
        self.driver.close()

if __name__ == "__main__":
    sl = Selenium()
    # amazonの検索結果画面
    sl.open_url("https://www.amazon.co.jp/s?k=%E3%83%AF%E3%82%A4%E3%83%A4%E3%83%AC%E3%82%B9%E3%82%A4%E3%83%A4%E3%83%9B%E3%83%B3&sprefix=%E3%83%AF%E3%82%A4%E3%83%A4%E3%83%AC%E3%82%B9%E3%82%A4%E3%83%A4%E3%83%9B%E3%83%B3%2Caps%2C215&ref=nb_sb_ss_pltr-ranker-24hours_1_9") 
    # 商品を取得するページ数
    sl.get_item_list_sumpage(2)
    sl.get_review()
    sl.close_driver()