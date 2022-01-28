<template>
    <div id="statusList">
        <ul>
            <li v-for="(item, index) in statusList" :key="index" class="status-box" style="background-color: ;">
                <span class="left-color" :style="{ backgroundColor: item.fill }" :class="[item.key === 'wait' ? 'left-color-border' : '']"></span>
                <span class="right-text">{{item.label}}</span>
            </li>
        </ul>
    </div>
</template>

<script>
    import statusList from './statusList.js'
    export default {
        data() {
            return {
                statusList: statusList
            }
        }
    }
</script>

<style lang="scss" scoped>
    #statusList {
        ul {
            margin: 0;
            padding: 0;

            .status-box {
                list-style-type: none;
                margin-bottom: 14px;

                .left-color {
                    width: 8px;
                    height: 8px;
                    border-radius: 4px;
                    display: inline-block;
                }
                .left-color-border {
                    width: 9px;
                    height: 9px;
                    border-radius: 50%;
                    display: inline-block;
                    border: 1px solid #DCDEE5;
                }

                .right-text {
                    font-size: 12px;
                    color: #63656E;
                    margin-left: 5px;
                }
            }
        }
    }
</style>
