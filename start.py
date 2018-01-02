import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from multiprocessing import Pool


class kanman(object):
    def __init__(self, url, path):
        self.url = url
        self.path = path

    def gethome(self):
        r = requests.get(self.url).content
        soup = BeautifulSoup(r, 'html.parser')
        find_list = soup.find('ul', {'class': 'chapter-list'}).find_all('a')
        chapter_list = {}
        for i in find_list:
            chapter_name = i.text
            chapter_url = self.url + i.attrs['href']
            chapter_list[chapter_name] = chapter_url
            chapter_path = self.path + chapter_name
            self.mkdir(chapter_path)
        return chapter_list

    def mkdir(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            print('目录已存在,无需创建!')

    def getsoup(self, url):
        driver = webdriver.PhantomJS()
        driver.implicitly_wait(30)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        findlist = soup.find('div', {'class': 'mh_comicpic'})
        imgnum = int((len(soup.find_all('option')) - 3) / 2)
        imgstart = findlist.find('img').attrs['src'].rstrip('1.jpg-kmw.middle')
        return imgnum, imgstart

    def get_pool(self, chapter_name, soup):
        name = self.path + chapter_name + '/'
        p = Pool(4)
        for i in range(1, soup[0] + 1):
            jpgname = name + str(i) + '.jpg'
            jpgurl = soup[1] + str(i) + '.jpg-kmw.middle'
            p.apply_async(self.savejpg, args=(jpgname, jpgurl))
        p.close()
        p.join()

    def savejpg(self, jpgname, jpgurl):
        print('PID:{}'.format(os.getpid()))
        with open(jpgname, 'wb') as file:
            r = requests.get(jpgurl).content
            file.write(r)
        print(jpgname + '已保存成功!')

    def go(self):
        chapter_list = self.gethome()
        for i in chapter_list.keys():
            soup = self.getsoup(chapter_list[i])
            if self.saved(soup[0], i):
                print(i + '已保存,无需下载!')
            else:
                self.get_pool(i, soup)
        print('漫画已全部下载完毕!')

    def saved(self, num, chapter_name):
        path = self.path + chapter_name
        a = len(os.listdir(path))
        print('{0}共{1}页,已下载{2}页'.format(chapter_name, num, a))
        return a == num


if __name__ == '__main__':
    comicname = '盘龙'
    url = 'http://www.kanman.com/7099/'
    path = '漫画/' + comicname + '/'
    ok = kanman(url=url, path=path)
    ok.go()
