# PassSite
This website is used to display the password cracking algorithms.



### 后端

> 相关需求：
>
> python==3.7
>
> django==2.2.1
>
> django-cors-headers==3.11.0
>
> tensorflow==2.3.0

在后端目录下输入命令

```
python3 manage.py runserver
```



### 前端

在前端目录下输入命令

```
npm install
npm run serve
```

之后访问http://localhost:8080即可



### 接口

**LSTM**

"id:<>,module:lstm,type:\<gen或train\>,email:\<>,epoch:<在gen时为0>,prob:<>,num:<>,len:<>"

**PL**

"id:<>,module:pl,type:\<gen或train\>,email:<>,extract_len:<>,epoch:<在gen时为0>,struct_prob:<>,final_prob:<>,num:<>,gen_len:<>"

**PassGAN**

"id:<>,module:gan,type:\<gen或train\>,email:<>,iter:<在gen时为0>,num:<>,len:<>"

**PSM**

输入："id:<>,module:psm,password:<>"

返回："<密码打分[0,100]>"



### TODO

+ LSTM，PL，PassGAN的介绍文本，放在/frontend/src/components/对应的文件中
+ PSM的介绍文本，放在/frontend/src/components/PSM.vue中
+ PSM代码放在/backend/module/psm中

