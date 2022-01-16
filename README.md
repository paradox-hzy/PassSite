# PassSite
This website is used to display the password cracking algorithms.



#### 前端

在前端目录下输入命令

```
npm install
npm run serve
```

之后访问http://localhost:8080即可



#### 接口

**LSTM**

"module:lstm,type:\<gen或train\>,email:\<>,epoch:<在gen时为0>,prob:<>,num:<>,len:<>"

**PL**

"module:pl,type:\<gen或train\>,email:<>,extract_len:<>,epoch:<在gen时为0>,struct_prob:<>,final_prob:<>,num:<>,gen_len:<>"

**PassGAN**

"module:gan,type:\<gen或train\>,email:<>,iter:<在gen时为0>,num:<>,len:<>"

