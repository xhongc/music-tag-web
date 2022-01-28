# cw-vue-1.0

> cw-vue-1.0

## Build Setup

>建议使用淘宝镜像源 https://registry.npmjs.org

``` bash
npm config set registry http://registry.npm.taobao.org
``` 
>查看是否切换成功


``` bash
npm get registry 
```
>或者使用cnpm代替npm来进行依赖安装

``` bash
npm install -g cnpm --registry=https://registry.npm.taobao.org
```

``` bash
# 安装依赖
npm install

# 服务启动
npm run dev

# 生产环境build
npm run build

# 生产环境build以及文件分析
npm run build --report
```

如果想知道相关的[底层工作原理](http://vuejs-templates.github.io/webpack/) 和 [vue-loader 相关文档](http://vuejs.github.io/vue-loader).
