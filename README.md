<!--
 * @Descripttion: 
 * @version: 
 * @Author: Hansel
 * @Date: 2020-08-01 18:17:30
 * @LastEditors: Hansel
 * @LastEditTime: 2020-08-02 11:01:33
--> 
# 僵尸企业网站使用说明 #
## ##
HTML5端服务
PC浏览器访问 
  
#### 使用

1. 访问网址，点击"get start"按钮，弹出对话框
2. 对话框中有两个标签页，分别对应 "csv上传" "结果预览"  `说明：结果预览在文件预测完成之后才会渲染数据`
3. 上传文件---->按住Ctrl选择四份需要预测的文件，上传的csv大于4份开放`预测按钮`
4. 预测结果---->点击`预测`按钮，开始预测，大概等待1~2分钟，预测完成---->此时开放下载按钮，结果预览页渲染数据
5. 点击下载按钮---->将预测好的数据下载到本地
6. 结束
#### 待完善
1. 数据查询功能---->结果预览页查询功能还未做
2. 文件删除功能---->点上传文件后的文件列表中的删除按钮，目前只有前端的回调，后台数据并不会被删除
3. 文件分类---->目前上传后的文件都放置于相同的文件夹中，未按用户进行分类储存，多人同时操作时，脚本会读取到别人的数据。也就是并不支持多人同时操作
4. 文件限制---->目前做到了仅限用户上传csv，但未对其上传的csv进行检查，也就是说上传了预测集以外的数据时，脚本也会执行

## 安装依赖
```
npm run pre || yarn install || cnpm install || npm install --registry https://registry.npm.taobao.org
```
### 本地运行
```
npm run start || cnpm run start || yarn run start  
```
### 容器搭建
#### 1.创建容器
```
git clone http://git.inforsecur.cn/zombiecompany/zombie-backend.git
cp zombie-backend/Dockerfile/dockerfile ./dockerfile
docker build -t zombie-backend .
docker run -d -p 3300:3300 -p 4430:443 --name zombie-backend --restart always zombie-backend
```
#### 2.配置nginx
内网配置:
```
    server {
	   listen 80;
	   server_name zombie.inforsecur.cn;
        root /usr/share/nginx/html/Zombie-UI/build;
	   index index.html;
	   client_max_body_size 20m;
        location ^~ /apis {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'OPTION, POST, GET';
            add_header 'Access-Control-Allow-Headers' 'X-Requested-With, Content-Type';
            proxy_read_timeout 600;
            proxy_pass https://inforsecur.cn:4430;
        }
    }
```
外网配置:
```
    server {
        listen 80;
        server_name  zombie.wublubdubda.cn;
        proxy_set_header Host "zombie.inforsecur.cn";
        location / {
            proxy_pass http://localhost:7000/; # 路由模式history的修改
        }
    }
```
#### 3.配置frp
```
[zombie]
type = http
local_port = 80
custom_domains = zombie.inforsecur.cn
```

### 相关文档
See  
[NodeJS中Mongodb驱动](https://www.mongodb.org.cn/drivers/5.html)  
[ExpressJs](https://www.expressjs.com.cn/)  
[PostMan使用教程](https://www.bilibili.com/video/BV1Bb411e7jG?from=search&seid=18438246015708729910)  
[Git-flow](https://nvie.com/posts/a-successful-git-branching-model/)  