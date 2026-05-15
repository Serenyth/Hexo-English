YML 文件字段说明文档
一、基础格式（必填字段）
（一）根级配置字段
字段名	类型	描述	示例值
title	字符串	页面主标题，用于定义当前模块或页面的核心名称	即刻短文
subTitle	字符串	页面副标题，补充说明主标题，提供更具体的主题描述	咸鱼的日常生活。
tips	字符串	提示文本，通常用于简短的功能说明或引导语	随时随地，分享生活
buttonText	字符串	按钮文本，定义页面中功能按钮的显示文案	关于我
buttonLink	字符串	按钮链接，指定按钮点击后跳转的目标地址，支持相对路径或绝对路径	/about/
limit	数字	内容条目限制数，控制列表显示的最大条目数量	30
home_essay	布尔值	首页文章开关，控制是否在首页显示文章列表，true为显示，false为隐藏	true
top_background	字符串	顶部背景图链接，设置页面顶部区域的背景图片地址	https://img02.anheyu.com/adminuploads/1/2022/08/21/630249e2df20f.jpg
essay_list	数组	文章列表，包含多个文章条目，每个条目需至少包含content和date字段	- 内容详见下文essay_list子字段说明
（二）essay_list 子字段（必填）
字段名	类型	描述	示例值
content	字符串	文章内容摘要，简要描述文章的核心内容或主题	支持了 Accesskey 快捷键，可以直接按下 shift + ? 组合键以查看快捷键选项。
date	字符串	发布日期，格式为YYYY/MM/DD或YYYY/MM/DD HH:mm:ss	2023/09/09
2022/10/23 08:00:00
二、可选字段
（一）essay_list 扩展字段（非必填）
字段名	类型	描述	示例值
video	数组	视频链接列表，支持多个视频链接，通常用于嵌入外部视频（如 B 站、自定义视频）	- https://player.bilibili.com/player.html?aid=226886152&bvid=BV1Ch41137tR&cid=1081639816&p=1&autoplay=0
image	数组	图片链接列表，支持多个图片链接，用于展示相关图片资源	- https://img02.anheyu.com/adminuploads/1/2023/07/01/64a033cb2c21e.webp!blogimg
address	字符串	地址信息，用于标注内容相关的地理位置	长沙
from	字符串	来源信息，说明内容的作者或出处	安知鱼
link	字符串	内容链接，指定当前条目的跳转链接，支持相对路径或绝对路径	/posts/e140.html
https://blog.anheyu.com/album/
aplayer	对象	音乐播放器配置，用于嵌入音频资源，包含以下子字段：
- server：音乐平台（如tencent）
- id：音乐资源 ID	server: tencent<br>id: 001FGQba3i10mw
（二）特殊说明
aplayer字段结构
当需要嵌入音乐时，使用aplayer对象，需指定音乐平台和资源 ID，示例：
yaml
aplayer:
  server: tencent  # 腾讯音乐平台
  id: 001FGQba3i10mw  # 音乐资源ID

日期格式兼容性
date字段支持精确到分钟的格式（如2022/10/23 08:00:00），也可仅包含日期（如2023/09/09）。
多资源支持
video和image字段可包含多个链接，按数组顺序依次展示，例如：
yaml
image:
  - https://example.com/image1.jpg
  - https://example.com/image2.jpg

三、示例
```yaml
- title: 即刻短文
  subTitle: 咸鱼的日常生活。
  tips: 随时随地，分享生活
  buttonText: 关于我
  buttonLink: /about/
  limit: 30
  home_essay: true
  top_background: 
- essay_list:
  - content: 安知鱼主题指南
    date: 2023/09/09
    video:
      - https://player.bilibili.com/player.html?aid=226886152&bvid=BV1Ch41137tR&cid=1081639816&p=1&autoplay=0
  - content: 支持了Accesskey快捷键...
    date: 2023/07/01
    video:
      - https://cdn.jsdelivr.net/npm/anzhiyu-blog-static@1.0.0/video/...
    image:
      - https://img02.anheyu.com/...
    address: 长沙
    from: 安知鱼
    link: /posts/e140.html
  - content: 音乐支持参数设置...
    date: 2023/01/02
    link: https://blog.anheyu.com/music/?id=7269231710&server=tencent
  - content: 歌曲推荐
    date: 2022/09/25
    aplayer:
      server: tencent
      id: 001FGQba3i10mw
```

## 基础格式
此 YAML 文件用于配置一个短文展示页面的相关信息，整体采用键值对的形式存储数据，部分值为列表或嵌套结构。

## 字段说明

### 全局配置字段
| 字段名 | 类型 | 是否可选 | 说明 |
| ---- | ---- | ---- | ---- |
| title | 字符串 | 否 | 页面的主标题，用于展示在页面显著位置，这里是“即刻短文” |
| subTitle | 字符串 | 否 | 副标题，对主标题进行补充说明，这里是“咸鱼的日常生活。” |
| tips | 字符串 | 否 | 提示信息，用于引导用户操作或说明页面功能，这里是“随时随地，分享生活” |
| buttonText | 字符串 | 否 | 按钮上显示的文本，这里是“关于我” |
| buttonLink | 字符串 | 否 | 按钮点击后跳转的链接，这里是“/about/” |
| limit | 数字 | 否 | 可能用于限制短文展示数量等，这里设置为 30 |
| home_essay | 布尔值 | 否 | 表示是否在首页展示短文，这里设置为 true |
| top_background | 字符串 | 否 | 页面顶部背景图的链接，这里是一个图片的 URL |

### 短文列表字段（essay_list）
`essay_list` 是一个列表，每个列表项代表一篇短文，每个短文包含以下字段：

| 字段名 | 类型 | 是否可选 | 说明 |
| ---- | ---- | ---- | ---- |
| content | 字符串 | 否 | 短文的具体内容，如文章主题、更新说明等 |
| date | 字符串 | 否 | 短文发布的日期，格式多样，如“2023/09/09”“2022/12/10”“2022/10/23 08:00:00”等 |
| video | 字符串列表 | 是 | 短文关联的视频链接列表，可包含一个或多个视频链接 |
| image | 字符串列表 | 是 | 短文关联的图片链接列表，可包含一个或多个图片链接 |
| address | 字符串 | 是 | 短文相关的地址信息，如“长沙” |
| from | 字符串 | 是 | 短文的来源信息，如“安知鱼” |
| link | 字符串 | 是 | 短文关联的链接，如文章详情页链接、外部视频链接等 |
| aplayer | 对象 | 是 | 音乐播放器相关配置，包含 `server`（音乐平台，如“tencent”）和 `id`（音乐 ID） | 