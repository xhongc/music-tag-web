<template>
    <bk-navigation :default-open="false" navigation-type="top-bottom" :header-title="headerTitle" :side-title="title"
        @toggle="handleToggle" :need-menu="false" class="bk-wrapper">
        <!--      头部菜单      -->
        <template slot="header">
            <top-header></top-header>
        </template>
        <template slot="side-icon" class="monitor-logo">
            <img class="monitor-logo-icon" src="/static/dist/img/favicon_64.ico">
        </template>
        <container>
        </container>
    </bk-navigation>
</template>

<script>
    import topHeader from './header.vue'
    import leftMenu from './leftMenu.vue'
    import container from './container.vue'

    export default {
        components: {
            topHeader,
            leftMenu,
            container
        },
        data() {
            return {
                title: '音乐标签Web版',
                headerTitle: '',
                imgSrc: '',
            }
        },
        computed: {
            imgPath() {
                return require('@/assets/base/img/execute.png')
            }
        },
        created() {
            // this.initLogo()
        },
        mounted() {
            const defaultTableHeight = document.documentElement.clientHeight - 52 - 40
            this.$store.commit('setDefaultTableHeight', defaultTableHeight)
        },
        methods: {
            handleToggle(v) {
                this.$nextTick(() => {
                    this.$refs.leftMenu.nav.toggle = v
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
.monitor-logo {
    width: 32px;
    height: 32px;
}

.monitor-logo-icon {
    width: 32px;
    height: 32px;
}
</style>
<style lang="scss">
.bk-wrapper {
    .bk-navigation-wrapper {
        .navigation-container {
            max-width: calc(100%) !important;

            .container-content {
                padding: 0;
            }
        }
    }
}
.bk-navigation-header {
    background-color: #ffffff !important;
    border-bottom: 1px solid #dcdee5;
}
</style>
