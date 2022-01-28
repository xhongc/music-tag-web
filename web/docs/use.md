# 使用指南

> cw-vue-1.0


### 主要目录结构 （src下）
* src/api  （后台接口）
   * apiUrl == 存放接口地址
   * axiosconfig == 接口配置
   * index.js == 统一引入 <br/><br/> 

* assets  （静态文件）
    * base ==  框架基础样式，色值，慎动！！！
    * custom ==  自定义开发静态资源
    * index.js == 统一引入 <br/><br/> 

* component （自定义组件）
    * base == 框架基础组件 （头部，导航，body）
    * index.js == 统一挂载组件 <br/><br/>  

* controller （js文件，公共方法）
    * func == 公共方法
    * views == html和js分离开发，存放js文件 <br/><br/>     

* directive （自定义指令）
    * modal == 提示框指令和确认框指令
    * index.js == 统一挂载指令 <br/><br/> 
    
* filter （过滤器）
    * validator == 表单校验插件
    * index.js == 统一引入 <br/><br/> 

* router （路由存放） <br/><br/> 

* views （页面存放） <br/><br/> 

* Vuex （vuex） <br/><br/> 

* App.vue （入口 vue 文件） <br/><br/> 

* main.js （入口文件与 app.vue 相关联）
