<template>
    <div id="container">
        <router-view></router-view>
    </div>

</template>

<script>
    export default {
        data() {
            return {
            }
        }
    }
</script>

<style scoped>
    #container {
        height: calc(100vh - 52px);
    }
</style>
