<template>
    <div style="display: flex;">
        <div style="background: #fff;height: 100vh;">
            <div style="width: 350px;margin-top: 20px;margin-left: 10px;">
                <div style="display: flex;align-items: center;">
                    <bk-icon type="arrows-left-shape" @click="backDir" style="cursor: pointer;"></bk-icon>
                    <bk-input :clearable="true" v-model="filePath"
                        @enter="handleSearchFile"
                        :placeholder="'请输入文件夹路径：'"
                        behavior="simplicity">
                    </bk-input>
                </div>
                <transition name="bk-slide-fade-down">
                    <div style="margin-top: 10px;" v-show="fadeShowDir">
                        <bk-tree
                            ref="tree1"
                            :data="treeListOne"
                            :node-key="'id'"
                            :has-border="true"
                            @on-click="nodeClickOne"
                            @on-expanded="nodeExpandedOne">
                        </bk-tree>
                    </div>
                </transition>
            </div>
        </div>
        <div style="background: #fff;height: 100vh;margin-left: 20px;margin-right: 20px;">
            <transition name="bk-slide-fade-left">
                <div style="margin-left: 40px;width: 500px;margin-top: 20px;" v-show="musicInfo.title">
                    <div style="width: 100%;display: flex;">
                        <bk-button :theme="'success'" :loading="isLoading" @click="handleClick" class="mr10"
                            style="width: 50%;">
                            保存信息
                        </bk-button>
                        <bk-select
                            :disabled="false"
                            :clearable="false"
                            v-model="resource"
                            style="width: 200px;"
                            ext-cls="select-custom"
                            ext-popover-cls="select-popover-custom">
                            <bk-option v-for="option in resourceList"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;margin-top: 10px;">
                        <div class="label1">标题：</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.title"></bk-input>
                        </div>
                        <div>
                            <bk-icon type="arrows-right-circle" @click="toggleLock('title')"
                                style="cursor: pointer;font-size: 22px;color: #64c864;margin-left: 10px;"></bk-icon>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;">
                        <div class="label1">艺术家：</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.artist"></bk-input>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;">
                        <div class="label1">专辑：</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.album"></bk-input>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;">
                        <div class="label1">风格：</div>
                        <div style="width: 70%;">
                            <bk-select
                                :disabled="false"
                                v-model="musicInfo.genre"
                                style="width: 250px;background: #fff;"
                                ext-cls="select-custom"
                                ext-popover-cls="select-popover-custom"
                                :placeholder="'请选择歌曲风格'"
                                searchable>
                                <bk-option v-for="option in genreList"
                                    :key="option.id"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;">
                        <div class="label1">年份：</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.year"></bk-input>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;">
                        <div class="label1">歌词：</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.lyrics" type="textarea" :rows="15"
                            ></bk-input>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;">
                        <div class="label1">描述：</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.comment" type="textarea"></bk-input>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;">
                        <div class="label1">专辑封面：</div>
                        <div style="width: 70%;">
                            <div v-if="musicInfo.album_img">
                                <bk-image fit="contain" :src="musicInfo.album_img" style="width: 128px;"
                                    v-if="reloadImg"></bk-image>
                            </div>
                            <div v-if="musicInfo.artwork">
                                <bk-image fit="contain" :src="musicInfo.artwork" style="width: 128px;"
                                    v-if="!musicInfo.album_img"></bk-image>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
        <div style="background: #fff;height: 100vh;">
            <transition name="bk-slide-fade-left">
                <div
                    style="display: flex;flex-direction: column;margin-top: 20px;flex: 1;margin-right: 20px;margin-left: 20px;"
                    v-show="fadeShowDetail">
                    <div v-if="SongList.length === 0">
                        <span style="margin-left: 30%;margin-top: 30%;">暂无歌曲信息</span>
                    </div>
                    <div v-else>
                        <div class="parent">
                            <div class="title2">应用</div>
                            <div class="title2">专辑封面</div>
                            <div class="title2">歌曲名</div>
                            <div class="title2">歌手</div>
                            <div class="title2">专辑</div>
                            <div class="title2">歌词</div>
                            <div class="title2">年份</div>
                        </div>
                        <div v-for="(item,index) in SongList" :key="index" style="margin-bottom: 10px;">
                            <div class="song-card">
                                <div>
                                    <div class="parent">
                                        <bk-icon type="arrows-left-circle" @click="copyAll(item)"
                                            style="font-size: 20px;color: #64c864;margin-right: 5px;cursor: pointer;"></bk-icon>
                                        <bk-image fit="contain" :src="item.album_img"
                                            style="width: 64px;cursor: pointer;"
                                            @click="handleCopy('album_img',item.album_img)">
                                        </bk-image>
                                        <div @click="handleCopy('title',item.name)" class="music-item">
                                            {{
                                                item.name
                                            }}
                                        </div>
                                        <div @click="handleCopy('artist',item.artist)" class="music-item">
                                            {{ item.artist }}
                                        </div>
                                        <div @click="handleCopy('album',item.album)" class="music-item">
                                            {{
                                                item.album
                                            }}
                                        </div>
                                        <div @click="handleCopy('lyric',item.id)" class="music-item">加载歌词</div>
                                        <div @click="handleCopy('year',item.year)" class="music-item">
                                            {{
                                                item.year
                                            }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                treeListOne: [],
                filePath: '/app/media',
                bakDir: '/app/media',
                fileName: '',
                resource: 'netease',
                resourceList: [{id: 'netease', name: '网易云音乐'}, {id: 'migu', name: '咪咕音乐'}],
                musicInfo: {
                    'genre': '流行'
                },
                fadeShowDir: false,
                fadeShowDetail: false,
                isLoading: false,
                SongList: [],
                reloadImg: true,
                genreList: [
                    {'id': '流行', name: '流行'},
                    {'id': '摇滚', name: '摇滚'},
                    {'id': '说唱', name: '说唱'},
                    {'id': '民谣', name: '民谣'},
                    {'id': '电子', name: '电子'},
                    {'id': '爵士', name: '爵士'},
                    {'id': '纯音乐', name: '纯音乐'},
                    {'id': '金属', name: '金属'},
                    {'id': '世界音乐', name: '世界音乐'},
                    {'id': '新世纪', name: '新世纪'},
                    {'id': '古典', name: '古典'},
                    {'id': '独立', name: '独立'},
                    {'id': '氛围音乐', name: '氛围音乐'}
                ]
            }
        },
        created() {
            this.handleSearchFile()
        },
        methods: {
            backDir() {
                this.filePath = this.bakDir
                this.handleSearchFile()
            },
            nodeClickOne(node) {
                console.log(node)
                if (node.icon === 'icon-folder') {
                    this.bakDir = this.filePath
                    this.filePath = this.filePath + '/' + node.name
                    this.handleSearchFile()
                } else {
                    this.musicInfo = {}
                    this.fileName = node.name
                    this.$api.Task.musicId3({'file_path': this.filePath, 'file_name': node.name}).then((res) => {
                        console.log(res)
                        this.musicInfo = res.data
                    })
                }
            },
            handleCopy(k, v) {
                if (k === 'lyric') {
                    this.$api.Task.fetchLyric({'song_id': v, 'resource': this.resource}).then((res) => {
                        console.log(res)
                        if (res.result) {
                            this.musicInfo['lyrics'] = res.data
                        } else {
                            this.$cwMessage('未找到歌词', 'error')
                        }
                    })
                } else if (k === 'album_img') {
                    this.musicInfo[k] = v
                    this.reloadImg = false
                    this.$nextTick(() => {
                        this.reloadImg = true
                    })
                } else {
                    this.musicInfo[k] = v
                }
            },
            copyAll(item) {
                this.handleCopy('title', item.name)
                this.handleCopy('year', item.year)
                this.handleCopy('lyric', item.id)
                this.handleCopy('album', item.album)
                this.handleCopy('artist', item.artist)
                this.handleCopy('album_img', item.album_img)
            },
            nodeExpandedOne(node, expanded) {
                console.log(node)
                console.log(expanded)
            },
            // 查询网易云接口
            toggleLock(mode) {
                if (mode === 'title') {
                    if (!this.musicInfo.title) {
                        this.$cwMessage('标题不能为空', 'error')
                        return
                    }
                    this.fadeShowDetail = false
                    this.$api.Task.fetchId3Title({title: this.musicInfo.title, resource: this.resource}).then((res) => {
                        this.fadeShowDetail = true
                        this.SongList = res.data
                    })
                }
            },
            // 文件目录
            handleSearchFile() {
                this.fadeShowDir = false
                this.$api.Task.fileList({'file_path': this.filePath}).then((res) => {
                    if (res.result) {
                        this.treeListOne = res.data
                        this.fadeShowDir = true
                    }
                })
            },
            // 保存音乐信息
            handleClick() {
                const params = [{
                    'file_full_path': this.filePath + '/' + this.fileName,
                    ...this.musicInfo
                }]
                this.isLoading = true
                this.$api.Task.updateId3({'music_id3_info': params}).then((res) => {
                    this.isLoading = false
                    if (res.result) {
                        this.$cwMessage('修改成功', 'success')
                    }
                })
            }
        }
    }
</script>
<style lang="postcss">
.bk-table-header .custom-header-cell {
    color: inherit;
    text-decoration: underline;
    text-decoration-style: dashed;
    text-underline-position: under;
}

.music-item {
    cursor: pointer;
}

.music-item:hover {
    color: #1facdd;
}

.label1 {
    width: 80px;
}

.parent {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(1, 1fr);
    grid-column-gap: 0;
    grid-row-gap: 0;
    place-items: center;
}

.title2 {
    font-weight: 500;
}

.song-card {
    display: flex;
    align-items: center;
    border-bottom: 1px solid #E2E2E2;
}

.song-card:hover {
    background: #E2E2E2;
}

.add-button {
    width: 24px;
    height: 24px;
    line-height: 20px;
    display: inline-block;
    background-color: transparent;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-left: 5px;
    font-size: 12px;
    color: rgb(97, 97, 97);
    text-align: center;
    cursor: pointer;
}

.delete-button {
    width: 24px;
    height: 24px;
    line-height: 20px;
    display: inline-block;
    background-color: transparent;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-left: 5px;
    font-size: 12px;
    color: rgb(63, 63, 63);
    text-align: center;
    cursor: pointer;
}
</style>
