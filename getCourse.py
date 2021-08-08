import requests
import json
from time import sleep

s = '_uab_collina=162790230655834173919529; _sensors_dapeng_anonymous_uuid=%223b757e4d-c0ff-41f7-a5f5-a4703068ba39%22; _pk_ref.3.fd4d=%5B%22%22%2C%22%22%2C1627902309%2C%22https%3A%2F%2Fblog.csdn.net%2Fsakura_ting%2Farticle%2Fdetails%2F119236876%22%5D; _pk_ses.3.fd4d=1; enter_dapeng=enter_dapeng; dptoken=7bf24792-47bf-4e83-a1cc-11b8d7a610b5; _sensors_dapeng_login_id=%22k0epfvneff%22; userinfo=%7B%22userId%22%3A%22k0epfvneff%22%2C%22nickname%22%3A%22May0919%22%2C%22avatar%22%3A%22https%3A%2F%2Fimage.dapengjiaoyu.com%2Fimages%2Favatars%2F28avatar.jpg%22%2C%22dpAccount%22%3A%22dp65239857%22%2C%22mobile%22%3A%2213177322377%22%2C%22loginName%22%3A%22May0919%22%2C%22studentSatusId%22%3Anull%7D; looyu_id=7925bb63ebc56565de0dabde52486426_20004236%3A2; looyu_20004236=v%3A0acf59f8652811748bbe4ab8e5e0ab8e%2Cref%3A%2Cr%3A%2Cmon%3A//m6815.talk99.cn/monitor%2Cp0%3Ahttps%253A//www.dapengjiaoyu.cn/personal-center/course/formal%253FuserId%253Dk0epfvneff%2526faid%253D3b757e4d-c0ff-41f7-a5f5-a4703068ba39%2526said%253D3b757e4d-c0ff-41f7-a5f5-a4703068ba39%2526fuid%253Dk0epfvneff%2526suid%253D%2526d%253D0%2526suu%253De70c047f-fd91-44d7-9cfd-57fc76936ae0%2526suc%253D1%2526college%253Dj5m48deg; _99_mon=%5B0%2C0%2C0%5D; _pk_id.3.fd4d=14718c05a40a3094.1627902309.1.1627906420.1627902309.'

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
