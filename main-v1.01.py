import os,re,tqdm,requests,sys,time,colorama,webbrowser
# import socket
# import numpy as np
from urllib import request
from lxml import etree
from pypinyin import lazy_pinyin,load_phrases_dict

def httpget(url):
    i=1
    while i<=3:
        try:
            r=requests.get(url=url,timeout=20)
            r.encoding='utf-8'
            if r.status_code==404:return None
            else:
                r.raise_for_status()
                return r.text
        except requests.RequestException as e:
            print(colorama.Back.RED+'发生错误：'+str(e))
            print('[{}/3]正在尝试重连！'.format(str(i)))
            i+=1
    print(colorama.Back.RED+'重连失败，请复制错误信息报告作者！')
    input('请按Enter键退出！')
    sys.exit()

def get_input(maxint,text):
    while True:
        userin=input(text)
        if userin.lower()=='q':sys.exit()
        if userin.isdecimal()==True:
            if int(userin)<=maxint and int(userin)>0:
                return int(userin)
                break
        print(colorama.Back.RED+'您的输入非法，请重新输入！')
        
class mtl():
    def __init__(self):
        self.host='https://www.lunu8.com'
        self.results,self.urls=[],[]
        self.title=''
        self.tujilj=''
        self.num=0
    def get_urls(self,tujiurl):
        urls=[]
        html=httpget(tujiurl)
        ehtml=etree.HTML(html)
        page=ehtml.xpath("//div[2]/ul/li[last()-1]/a/text()")
        img=ehtml.xpath("//img/@src")
        urls.append(img[1])
        print(colorama.Fore.GREEN+'已开始获取第'+str(self.num)+'个图片地址！')
        for i in range(2,int(page[0])):
            print('-------------------->>正在获取第{}张<<--------------------'.format(str(i)))
            url=tujiurl+'?page='+str(i)
            #print(url) #https://www.lunu8.com/web/95.html?page=8 
            html=httpget(url)
            ehtml=etree.HTML(html)
            img=ehtml.xpath("//img/@src")
            urls.append(img[1])
        return urls
    
    def get_results(self,url):
        html=httpget(url)
        ehtml=etree.HTML(html)
        results=ehtml.xpath("/html/body/div[1]/main/article")
        return results

    def search(self):
        while True:
            while True:
                keyword='a' #//input('请输入搜索关键词： ')
                if keyword=='':print(colorama.Back.RED+'关键词不能为空！')
                elif keyword=='q':sys.exit()
                elif str.isalnum(keyword)==False:print(colorama.Back.RED+'您的输入非法，请重新输入！')
                #不能是纯数字
                else:break
                
            t0=time.time()
            url=self.host+'/search.php?q='+keyword
            html=httpget(url)
            ehtml=etree.HTML(html)
            result=ehtml.xpath("/html/body/div[1]/main/article")
            self.results=result
            pagelj=ehtml.xpath("//div[@class='pagenavi']/a[last()]/@href")[0]
            print('pagelj='+pagelj)
            if 'page' in pagelj:
                #多页
                page=pagelj.lstrip('https://www.lunu8.com/search.php?q='+keyword+'&page=')
                #页数
                pbar=tqdm.tqdm(range(2,int(page)+1),desc='解析进度',ncols=80)
                for i1 in pbar:
                    self.results+=self.get_results(url+'&page='+str(i1))
            print('共找到图集{}个'.format(len(self.results)))
            if len(self.results)==0:
                print(colorama.Back.RED+'没有匹配的结果，换个关键词试试吧！')
            else:
                t1=time.time()
                print(colorama.Fore.GREEN+'共找到匹配结果{}条，耗时{}秒'.format(str(len(self.results)),str(round(t1-t0,3))))
                break
                
    def makeurls(self):
        self.num=0
        i=1400 #get_input(len(self.results),'请输入爬取图集数量： ')
        file_name = os.listdir('E:/python/1')
        for result in self.results[:i]: #result：一个图集，self.results：所有图集
            self.num=self.num+1
            title=result.xpath("./h2/a/text()")[0] #获取图集标题
            tujiurl=result.xpath("./h2/a/@href ")[0]
            if title.strip() not in file_name: 
                #tujiurl https://www.lunu8.com/web/95.html
                self.urls=self.get_urls(tujiurl)
                print(self.urls)
                print(title)
                self.title=title
                self.tujilj=tujiurl
                self.download(i)
            

    def download(self,i):
        i1=0 #下载图集数
        c=0 #下载图片计数
        t0=time.time()
        print('-------------------->>正在下载第{}组，还剩{}组<<--------------------'.format(str(self.num),str(i-self.num)))
        print('    ·图册标题：'+self.title)
        fdir='E:\python\\1\\'+self.title.strip()+'\\'
        if os.path.isdir(fdir) == False:
            os.makedirs(fdir)
        pbar=tqdm.tqdm(range(len(self.urls)),ncols=80)
        for i2 in pbar:
            path=fdir+'{}.jpg'.format(str(i2))
            if os.path.isfile(path)==False:
                pbar.set_description_str(colorama.Fore.GREEN+'    ·下载进度')
                print('\n\n\n')
                print(path)
                print(self.urls[i2])
                print('\n\n\n')
                i=1
                while i<=3:
                    print(self.tujilj+'?page='+str(i2))
                    try:
                        headers = {'Host':'www.lunu8.com','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0','Accept':'image/webp,*/*','Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2','Accept-Encoding':'gzip, deflate, br','Connection':'keep-alive','Referer':self.tujilj+'?page='+str(i2),'Cookie':'__cfduid=d3d95fb054fba684645e6a438ee5172441584299302; HstCfa4220066=1584299341571; HstCla4220066=1584902756244; HstCmu4220066=1584299341571; HstPn4220066=7; HstPt4220066=217; HstCnv4220066=6; HstCns4220066=14; c_ref_4220066=https%3A%2F%2Fwww.google.com%2F; __dtsu=10401584299309B754FDC6BD06E669C4; ftwwwlunu8com=1; __lfcc=1; timezone=8','Pragma':'no-cache','Cache-Control':'no-cache','TE':'Trailers'}
                        mp = requests.get(self.urls[i2],headers=headers,timeout=20)
                        with open(path,'wb') as f:
                            f.write(mp.content)
                    except requests.RequestException as e:
                        print(colorama.Back.RED+'发生错误：'+str(e))
                        print('[{}/3]正在尝试重连！'.format(str(i)))
                        time.sleep(10)
                        i=i+1
                    else:
                        print('内容写入文件成功')
                        f.close()
                        break
            else:
                pbar.set_description_str(colorama.Fore.YELLOW+'    ·图片已存在')
                time.sleep(0.05)
        t1=time.time()
        print(colorama.Fore.GREEN+'\n已下载完'+self.title+'任务，耗时{}秒'.format(str(round(t1-t0,3))))

    def run(self):
        while self.num<=1400 :
            self.search()
            self.makeurls()
            time.sleep(60)
            # self.download()
            # print(colorama.Back.RED+'下载完成')
            # while True:
                # choose=input('是否继续y/n')
                # if choose.lower=='y':
                    # self.run()
                # elif choose.lower=='n':
                    # sys.exit()
                # else:
                    # print(colorama.Back.RED+'没有这个选项！')
        
        
if __name__ == "__main__":
    os.system('title LuNv8Spider[V1.0]  panxiaonan')
    print('欢迎使用美图Spider[V1.0]！\n博客：http://www.panxiaonan.cc/emlog  \n获取源站：https://www.lunu8.com')
    colorama.init(True)
    pydict={'长筒袜':[['chang'],['tong'],['wa']]}
    mtl=mtl()
    mtl.run()
    input('请按Enter键退出！')

