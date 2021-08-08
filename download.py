import requests
import re
import subprocess     #后续会用到，控制终端的库
import os
from tqdm import tqdm    #为了好看，加上进度条
from time import sleep
from multiprocessing.dummy import Pool    #多线程的

s = '_uab_collina=162790230655834173919529; _sensors_dapeng_anonymous_uuid=%223b757e4d-c0ff-41f7-a5f5-a4703068ba39%22; _pk_ref.3.fd4d=%5B%22%22%2C%22%22%2C1627902309%2C%22https%3A%2F%2Fblog.csdn.net%2Fsakura_ting%2Farticle%2Fdetails%2F119236876%22%5D; _pk_ses.3.fd4d=1; enter_dapeng=enter_dapeng; dptoken=7bf24792-47bf-4e83-a1cc-11b8d7a610b5; _sensors_dapeng_login_id=%22k0epfvneff%22; userinfo=%7B%22userId%22%3A%22k0epfvneff%22%2C%22nickname%22%3A%22May0919%22%2C%22avatar%22%3A%22https%3A%2F%2Fimage.dapengjiaoyu.com%2Fimages%2Favatars%2F28avatar.jpg%22%2C%22dpAccount%22%3A%22dp65239857%22%2C%22mobile%22%3A%2213177322377%22%2C%22loginName%22%3A%22May0919%22%2C%22studentSatusId%22%3Anull%7D; looyu_id=7925bb63ebc56565de0dabde52486426_20004236%3A2; looyu_20004236=v%3A0acf59f8652811748bbe4ab8e5e0ab8e%2Cref%3A%2Cr%3A%2Cmon%3A//m6815.talk99.cn/monitor%2Cp0%3Ahttps%253A//www.dapengjiaoyu.cn/personal-center/course/formal%253FuserId%253Dk0epfvneff%2526faid%253D3b757e4d-c0ff-41f7-a5f5-a4703068ba39%2526said%253D3b757e4d-c0ff-41f7-a5f5-a4703068ba39%2526fuid%253Dk0epfvneff%2526suid%253D%2526d%253D0%2526suu%253De70c047f-fd91-44d7-9cfd-57fc76936ae0%2526suc%253D1%2526college%253Dj5m48deg; _99_mon=%5B0%2C0%2C0%5D; _pk_id.3.fd4d=14718c05a40a3094.1627902309.1.1627906420.1627902309.'

#处理cookies的方式
cookies = {}
s = s.encode('utf-8').decode('latin1')   #如果cookies有中文，这样处理编码就不会报错了
for k_v in s.split(';'):
    k,v = k_v.split('=',1)
    cookies[k.strip()] = v.replace('"','')


def spider(url,className):
    x = 0     #计数，防止出现重复的文件名，打断ffmpeg的合并
    headers = {   #防盗链建议加上
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Host': 'www.dapengjiaoyu.cn',
        #'Referer': 'https://www.dapengjiaoyu.cn/details/course?type=VIP&courseId=ijmiw8ve&faid=0853c508-9328-47e6-b65a-7b155523e509&said=0853c508-9328-47e6-b65a-7b155523e509&fuid=kewhtyxxuk&suid=&d=0&suu=51898ffd-988e-4455-8d8e-4158660db282&suc=1&state=LIVING'
    }
    #一定要json处理
    menu = requests.get(url=url,headers=headers,cookies=cookies).json()
    for i in tqdm(menu):
        x += 1             #计数
        print(i)
        videoName = i['title']  #保存的视频名
        videoName = videoName.replace(' ','') #将空格替换掉，如果有空格，ffmpeg会报错
        #获取vid，将后边的_e替换成.m3u8
        if i['videoContent']==None:
            continue
        vid = i['videoContent']['vid'].replace('_e', '_1.m3u8')
        #构造url
        m3u8_url = 'https://hls.videocc.net/ef4825bc7e/6/' + vid
        print(m3u8_url)
        m3u8_data = requests.get(m3u8_url).text
        #提取m3u8里边的ts文件的url
        ts_urls = re.findall('(https:.*?\.ts)', m3u8_data)
        #下载每一个ts文件
        jishu=0
        for ts_url in ts_urls:    
            #给下载的ts命名
            print(str(jishu)+'/'+str(len(ts_urls)))
            jishu+=1
            index = re.findall('_1_(\d+\.ts)', ts_url)[0]
            flag_0=False
            test=3
            while not flag_0 and test>0:
                try:
                    ts = requests.get(url=ts_url).contenty
                    flag_0=True
                except:
                    test-=1
            
            #这是保存的函数，下边解释
            write(className,ts,index)
            #将m3u8里边的ts url替换掉，成ts文件名，为了方便合并
            #print(ts_url)
            #print(index)
            m3u8_data = m3u8_data.replace(ts_url,index)
            #print(m3u8_data[0:500])
        if 'URI' in m3u8_data:#判断是否有密钥，有就提取url下载key
            key_url = re.findall('URI="(.*?key)', m3u8_data)[0]
            key = requests.get(url=key_url).content
            #className是文件夹的名称
            with open(className + '/' + 'key.m3u8','wb') as f3:
                f3.write(key)
            #将kye的url替换成本地的key密钥，方便合并
            m3u8_data = m3u8_data.replace(key_url,'key.m3u8')
        #保存函数
        write(className, m3u8_data)
        sleep(5)
        #获取当前程序路径
        path = os.getcwd()
        #将程序路径改为视频保存的路径
        os.chdir(className)
        sleep(1)
        #利用ffmpeg合并视频的函数，下边有解释
        merge(videoName,x)
        #沉睡20秒，让视频有足够的时间合并
        sleep(20)
        #删除除mp4文件以为的文件的函数，下边解释
        remove()
        sleep(2)
        #再将程序路径改回来
        os.chdir(path)
        print(f'合成完毕:{videoName}')

        #保存文件的函数
def write(name,data,index=''):
	#创建文件夹
    if not os.path.exists(name):
        os.mkdir(name)
     #因为保存的格式不一样，需要判断一下
    if type(data) == str:
    	#这是m3u8文件
        with open(name + '/' + 'index.m3u8','w') as f1:
            f1.write(data)
    else:
    	#这是ts文件，index是上边的序号
        with open(name + '/' + index, 'wb') as f2:
            f2.write(data)

#这是利用ffmpeg的函数
def merge(title,x):
	#还记得上边那个计数的x嘛，在这里用，因为如果名称一样的话，ffmpeg会报错
    c = 'ffmpeg -allowed_extensions ALL -i index.m3u8 -c copy {}.mp4'.format(str(x)+title)
    #在终端中输入ffmpeg的命令，合并视频
    subprocess.Popen(c,shell=True)



#删除多余文件的函数
def remove():
    con = True
    while con:
        li = os.listdir()
        for i in li:
        #我曾想检测到mp4合成以后再删除文件，就不用sleep()了，但是ffmpeg不是一次性合并完成，所以只能用sleep()了，如果大佬有好的方法，可以指点小弟一下
            if 'mp4' in i:
                for j in li:
                    if 'mp4' not in j:
                        os.remove(j)
                con = False
                break


if __name__ == '__main__':
    #all_course替换为getCourse.py中的allCourse
    all_course=[('754074e672ce4cfa82c38222908664dd', 'jft2wxm0', '油画专项修炼模块'), ('b0b8761ade7f4b499e811785e7e9b045', 'joxopqqppg', '美术基础入门模块'), ('35e74aec26a84cd9b62b1b7543af8215', 'jft2m3bh', '速写入门模块'), ('1125712ba9f64c9e9843f713b7cfb4d1', 'jzumb11oaj', '素描系统模块'), ('5faa769c1f5e4d71b17e46bcd54ca284', 'jzumirk7yb', '色彩系统模块'), ('9af8da7569d54750996a4bd2395744ec', 'jft2ntt5', '素描专项模块'), ('1f41b7b683be4f42ac8ce34d43a4af03', 'jft2olbf', '水粉专项模块'), ('54761238482e4946913ddf289c89211b', 'jft2xf2a', '水彩画专项修炼模块'), ('329420053e784dad9c20ed80e4309e92', 'jft2q5i9', '彩铅手绘专项修炼模块'), ('297e4da5cf1c42aeb4d6ecde1e574639', 'jft2p26f', '设计手绘专项修炼模块'), ('fc5df16f6a444124ba600b8588fb1783', 'jj9fgmjxew', '服装设计手绘专项修炼模块'), ('e24c077ea1bc4120988f297bbfd2a07a', 'jft2v4nb', '动漫手绘专项修炼模块'), ('1f91c660fe6f4765a57ddc2a873d77dc', 'k6c0ex1zce', '美术亲子课'), ('k9zbh9p1hr', 'k9zbg6nfxz', '设计师手绘预习课'), ('29ca5956cf3b46d18f46b0cd980f1f2f', 'jotf1dgvzy', '人物线描课'), ('k8tnt4wpqo', 'jp3pjz5iqa', '百变美甲课'), ('2415eebd7fca4c7ea4f81de8c66a9e45', 'k4i7awsyyo', '简笔画'), ('k64nw4w7nz', 'k4i7n0nnlk', '手账tips')]
    for course in all_course:
        flag=False
        value=0
        while not flag:
            i = 'https://www.dapengjiaoyu.cn/api/old/courses/stages/'+str(course[0])+'/chapters?courseId='+str(course[1])+'&page=' + str(value)
            res=requests.get(url=i,cookies=cookies)
            print(res.text)
            if res.text=='[]':
                flag=True
            spider(i,course[2])
            value+=1
