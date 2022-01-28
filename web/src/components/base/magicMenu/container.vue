<template>
    <div id="container">
        <keep-alive v-if="keepAliveShow">
            <router-view v-if="$route.path === '/largescreen'"></router-view>
        </keep-alive>
        <router-view v-if="$route.path !== '/largescreen'"></router-view>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                keepAliveShow: true
            }
        },
        watch: {
            $route: function(val, oldval) {
                if (val.name === 'LargeScreen' && oldval.name !== 'ViewDetail') {
                    // 表明从别的页面进入作业监视大屏
                    // 刷新keepAlive
                    this.keepAliveShow = false
                    setTimeout(() => {
                        this.keepAliveShow = true
                    }, 0)
                }
            }
        }
    }
</script>

<style scoped>
    #container {
        height: calc(100vh - 52px);
    }
</style>
