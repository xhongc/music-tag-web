![](music-tag.png)

# 🚀 Music Tag Web

『音乐标签』Web版是一款可以编辑歌曲的标题，专辑，艺术家，歌词，封面等信息的应用程序， 支持FLAC, APE, WAV, AIFF, WV, TTA, MP3, M4A, OGG, MPC, OPUS, WMA, DSF,
DFF等音频格式。
<div class="column" align="middle">
  <img src="https://img.shields.io/docker/pulls/xhongc/music_tag_web" alt="docker-pull-count" />
</div>

# 🎉 Feature

为什么开发web版？ 在使用Navidrome时，我的音乐都是在远程服务器上的，本地的Musictag和mp3tag不能满足我的需求， 我需要部署在远程服务器上去需改线上的音乐标签，相当于在使用Navidrome的边车应用。

- 该版本是我自用的小工具，如果你也有这个需求，可以使用。欢迎提出issues，我会满足你的需求，在我的能力范围内。
- 支持用户自定义上传标签源
- 支持批量自动修改音乐标签
- 支持音乐指纹识别，即使没有元数据也可以识别音乐
- version：1.1.4 支持整理音乐文件，按艺术家，专辑分组
- version：1.1.5 支持文件排序，按照文件名，文件大小，更新时间排序
- version: 1.1.7 支持plex专辑类型，新增配置显示/隐藏字段
- version： 1.1.8 修复不同类型音频文件的专辑类型
- version： 1.2.0 新增歌曲语言整理文件
- version： 1.2.2 优化自动打标签匹配算法
- version： 1.2.3 新增智能刮削标签源，集成多个平台的标签源，按匹配度排序
- version： 1.2.4 支持繁体匹配，新增消息中心展示自动刮削不匹配的数据
- version： 1.2.5 支持保存专辑封面文件，支持自定义上传专辑封面
- version： 1.2.6 简单适配H5端，支持手机端访问
- [20230907] version:latest 支持wma，wmv格式, 修复自动刮削报错停止的问题
- [20230909] version:latest 音轨号，光盘号 格式优化，优化匹配规则
- [20230911] version:latest 支持无感刮削，对新增的音乐文件后台自动刮削，无感知刮削。修复.ape文件读取报错的问题。
- [20230912] version:latest 新增自定义层数的整理文件，新增根据刮削状态排序，修复大写的音乐后缀名识别不到。
# 🦀 Show Project
DEMO 地址账号密码为：admin/admin

[【音乐标签Web｜Music Tag Web】](http://42.193.218.103:8002/#/)

# 🔨 How to Build

1. docker-compose -f local.yml build
2. docker-compose -f local.yml up

# 💯 How to Use
[【使用手册】](https://xiers-organization.gitbook.io/music-tag-web/)

镜像已上传至阿里云Docker Registry 操作指南：

### 从阿里云Docker Registry拉取镜像

1`docker pull xhongc/music_tag_web:latest`

### dokcer run

2. `docker run -d -p 8001:8001 -v /path/to/your/music:/app/media --restart=always xhongc/music_tag_web:latest`
   
或者 使用portainer stacks部署
   ![img_1.png](img_1.png)

```yaml
version: '3'

services:
  music-tag:
    image: xhongc/music_tag_web:latest
    container_name: music-tag-web
    ports:
      - "8001:8001"
    volumes:
      - /path/to/your/music:/app/media:z
    command: /start
    restart: always
```
ps. `/path/to/your/music` 改成你的音乐文件夹路径！

3 访问在127.0.0.1:8001/admin 默认账号密码 admin/admin 修改默认密码
![img_7.png](img_7.png)

# 📷 User Interface
![img_5.png](img_5.png)
![img_4.png](img_4.png)
![img_6.png](img_6.png)
![img_2.png](img_2.png)

# 💬 Contact me
各位大佬有什么意见需求，欢迎提出issues，我会满足你的需求，在我的能力范围内。
issue 没及时看到的，可以加群讨论！
<div>
<img  src="/img_10.png" width="250">  &nbsp;
</div>
## 发布频道：

[t.me/music_tag_web](https://t.me/music_tag_web)

# 💸 赞助与支持
如果您觉得 music-tag-web 对你有帮助，可以请作者喝杯咖啡。
<div>
<img  src="/WechatIMG377.jpg" width="250" >  &nbsp; 
<img  src="/img_8.png" width="250">  &nbsp;
</div>

# 免责声明
禁止任何形式的商业用途，包括但不仅限于售卖/打赏/获利，不得使用本代码进行任何形式的牟利/贩卖/传播，再次强调仅供个人私下研究学习技术使用，不提供下载音乐本体！ 本项目仅以纯粹的技术目的去学习研究，如有侵犯到任何人的合法权利，请致信408737515@qq.com，我将在第一时间修改删除相关代码，谢谢！

本项目基于 GPL V3.0 许可证发行，以下协议是对于 GPL V3.0 的补充，如有冲突，以以下协议为准。

词语约定：本协议中的“本项目”指music-tag-web项目；“使用者”指签署本协议的使用者；“官方音乐平台”指对本项目内置的包括酷我、网易云、QQ音乐、咪咕、酷狗音乐、酷我音乐等音乐源的官方平台统称；“版权数据”指包括但不限于图像、音频、名字等在内的他人拥有所属版权的数据。

本项目的数据来源原理是从各官方音乐平台的公开服务器中拉取数据，经过对数据简单地筛选与合并后进行展示，因此本项目不对数据的准确性负责。 使用本项目的过程中可能会产生版权数据，对于这些版权数据，本项目不拥有它们的所有权，为了避免造成侵权，使用者务必在24小时内清除使用本项目的过程中所产生的版权数据。 本项目内的官方音乐平台别名为本项目内对官方音乐平台的一个称呼，不包含恶意，如果官方音乐平台觉得不妥，可联系本项目更改或移除。 本项目内使用的部分包括但不限于字体、图片等资源来源于互联网，如果出现侵权可联系本项目移除。 由于使用本项目产生的包括由于本协议或由于使用或无法使用本项目而引起的任何性质的任何直接、间接、特殊、偶然或结果性损害（包括但不限于因商誉损失、停工、计算机故障或故障引起的损害赔偿，或任何及所有其他商业损害或损失）由使用者负责。 本项目完全免费，仅供个人私下小范围研究交流学习 python 技术使用, 且开源发布于 GitHub 面向全世界人用作对技术的学习交流，本项目不对项目内的技术可能存在违反当地法律法规的行为作保证，禁止在违反当地法律法规的情况下使用本项目，对于使用者在明知或不知当地法律法规不允许的情况下使用本项目所造成的任何违法违规行为由使用者承担，本项目不承担由此造成的任何直接、间接、特殊、偶然或结果性责任。 若你使用了本项目，将代表你接受以上协议。
