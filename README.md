# 验证码识别接口

*（接口能力由[ddddocr](https://github.com/sml2h3/ddddocr)及[ocr_api_server](https://github.com/sml2h3/ocr_api_server)提供支持）*

## 接口说明

1. 测试接口：

   地址：[/ping](/ping)

   请求方式：GET

   携带参数：无

   说明：提供接口能力验证功能，返回`pong`则服务正常。

2. 图片验证码识别（base64）：

   base64方式地址：[/ocr](/ocr) 或 [/ocr/base64](/ocr/base64)

   文件上传方式地址：[/ocr/file](/ocr/file)

   请求方式：GET或POST

   携带参数：

   1. `image`: 验证码图片base64或文件
   2. （可选）`rerurn_type`: 返回值格式    可选项：`json`或`text`    默认值：`json`

   返回值：

   ​    `"status"`: 状态码,

   ​    `"result"`: 识别的结果,

   ​    `"msg"`: 消息,

   ​    `"time"`: 当前时间

3. 目标检测识别（base64或文件上传）：

   base64方式地址：[/det](/det) 或 [/det/base64](/det/base64)

   文件上传方式地址：[/det/file](/det/file)

   请求方式：GET或POST

   携带参数：

   1. ​	image`: 验证码图片base64`
   2. （可选）`rerurn_type`: 返回值格式    可选项：`json`或`text`    默认值：`json`

   返回值：

   ​    `"status"`: 状态码,

   ​    `"result"`: 识别的结果,

   ​    `"msg"`: 消息,

   ​    `"time"`: 当前时间
   
4. 滑块识别：暂未启动




