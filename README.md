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

"module:lstm,type:\<gen或train\>,email:\<>,epoch:<在gen时为0>,prob:<>,num:<>,len:<>"

**PL**

"module:pl,type:\<gen或train\>,email:<>,extract_len:<>,epoch:<在gen时为0>,struct_prob:<>,final_prob:<>,num:<>,gen_len:<>"

**PassGAN**

"module:gan,type:\<gen或train\>,email:<>,iter:<在gen时为0>,num:<>,len:<>"



### TODO

+ LSTM，PL，PassGAN的介绍文本，放在/frontend/src/components/对应的文件中
+ LSTM，PL，PassGAN的封装模型，放在/backend/module/中
  + 构造方法：提供参数para（dict类型，参考上面的**接口**）
  + 调用predict方法在/backend/result/中生成\<id\>.txt文件（id在para参数中）
+ 完成模型后修改/backend/server/views.py，连接上3个模型

