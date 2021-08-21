import requests
import json
from time import sleep

#cookies
s = ''

#处理cookies的方式
cookies = {}
s = s.encode('utf-8').decode('latin1')   #如果cookies有中文，这样处理编码就不会报错了
for k_v in s.split(';'):
    k,v = k_v.split('=',1)
    cookies[k.strip()] = v.replace('"','')

page=1
flag=False
all_data=[]
while not flag:
    url='https://www.dapengjiaoyu.cn/api/old/courses/open?type=VIP&collegeId=j5m48deg&page='+str(page)+'&size=10'
    headers = {   #防盗链建议加上
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Host': 'www.dapengjiaoyu.cn'
        #'Referer': 'https://www.dapengjiaoyu.cn/personal-center/course/formal?userId=k0epfvneff&faid=3b757e4d-c0ff-41f7-a5f5-a4703068ba39&said=3b757e4d-c0ff-41f7-a5f5-a4703068ba39&fuid=k0epfvneff&suid=&d=0&suu=e70c047f-fd91-44d7-9cfd-57fc76936ae0&suc=1&college=j5m48deg'
   }
    res=requests.get(url=url,headers=headers,cookies=cookies)
    if res.text=='[]':
        flag=True
    page+=1
    res=json.loads(res.text)

    for data in res:
        id=data['id']
        title=data['title']
        print(title)
        all_data.append((id,title))
    sleep(1)
print('获取'+str(len(all_data))+'门课程')
all_course=[]
for data in all_data:
    url='https://www.dapengjiaoyu.cn/api/old/courses/stages?courseId='+data[0]
    res=requests.get(url=url,headers=headers,cookies=cookies)
    #print(res.text)
    res=json.loads(res.text)
    #print(res)
    print(data)
    print(res)
    if res['liveStage']==None:
        continue
    key=res['liveStage'][0]['id']
    all_course.append((key,data[0],data[1]))
    sleep(1)
print(all_course)
