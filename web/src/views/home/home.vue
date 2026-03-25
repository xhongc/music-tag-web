<template>
    <div style="display: flex;flex-wrap: wrap;">
        <div class="file-section">
            <div style="width: 95%;margin-top: 20px;margin-left: 10px;">
                <div style="display: flex;align-items: center;">
                    <bk-icon type="arrows-left-shape" @click="backDir" style="cursor: pointer;"></bk-icon>
                    <bk-input :clearable="true" v-model="filePath"
                        @enter="handleSearchFile"
                        :placeholder="'Enter folder path:'"
                        behavior="simplicity">
                    </bk-input>
                    <bk-icon type="arrows-down-shape" @click="handleSearchFile" style="cursor: pointer;"></bk-icon>
                </div>
                <div style="margin-top: 10px;display: flex;align-items: center;">
                    <bk-input type="text" v-model="searchWord" placeholder="Search by filename" @enter="handleSearch"></bk-input>
                    <div style="margin-left: 10px;margin-right: 5px;">
                        <bk-dropdown-menu :align="'right'">
                            <template slot="dropdown-trigger">
                                <span class="dropdown-trigger-btn bk-icon icon-sort"
                                    style="cursor: pointer;font-size: 20px;"></span>
                            </template>
                            <ul class="bk-dropdown-list" slot="dropdown-content">
                                <li><a href="javascript:;" @click="changeSorted('name')"
                                    :class="{ 'isSelected': sortedField.includes('name') }">Name</a></li>
                                <li><a href="javascript:;" @click="changeSorted('update_time')"
                                    :class="{ 'isSelected': sortedField.includes('update_time') }">Modified Time</a></li>
                                <li><a href="javascript:;" @click="changeSorted('size')"
                                    :class="{ 'isSelected': sortedField.includes('size') }">Size</a></li>
                            </ul>
                        </bk-dropdown-menu>
                    </div>
                </div>
                <transition name="bk-slide-fade-down">
                    <div style="margin-top: 10px;" v-show="fadeShowDir">
                        <bk-tree
                            ref="tree1"
                            :data="treeListOne"
                            :multiple="true"
                            :node-key="'id'"
                            :has-border="true"
                            :tpl="tpl"
                            :draggable="true"
                            :drag-sort="true"
                            @on-click="nodeClickOne"
                            @on-check="nodeCheckTwo"
                            @on-expanded="nodeExpandedOne">
                        </bk-tree>
                    </div>
                </transition>
            </div>
        </div>
        <div class="edit-section">
            <transition name="bk-slide-fade-left">
                <div style="margin-left: 40px;width: 500px;margin-top: 20px;"
                    v-show="musicInfo.title && checkedIds.length === 0">
                    <div style="width: 100%;display: flex;align-items: center;">
                        <bk-button :theme="'success'" :loading="isLoading" @click="handleClick" class="mr10"
                            style="width: 87%;">
                            Save Info
                        </bk-button>
                        <div style="margin-left: 6px;cursor: pointer;" @click="exampleSetting3.primary.visible = true">
                            <bk-icon type="cog-shape"></bk-icon>
                        </div>
                    </div>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;margin-top: 10px;">
                        <div class="label1 can-copy" v-bk-tooltips="'Variable: ${title}'" v-bk-copy="'${title}'">Title:</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.title"></bk-input>
                        </div>
                        <div>
                            <bk-icon type="arrows-right-shape" @click="toggleLock('title')"
                                style="cursor: pointer;color: #64c864;margin-left: 20px;">
                            </bk-icon>
                        </div>
                    </div>
                    <div v-for="(item, index) in showFields" :key="'l1' + index">
                        <div class="edit-item" v-if="item === 'filename'">
                            <div class="label1 can-copy" v-bk-tooltips="'Variable: ${filename}'" v-bk-copy="'${filename}'">
                                Filename:
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.filename"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item can-copy" v-else-if="item === 'artist'">
                            <div class="label1" v-bk-tooltips="'Variable: ${artist}'" v-bk-copy="'${artist}'">Artist:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.artist"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item can-copy" v-else-if="item === 'album'">
                            <div class="label1" v-bk-tooltips="'Variable: ${album}'" v-bk-copy="'${album}'">Album:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.album"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item can-copy" v-else-if="item === 'albumartist'">
                            <div class="label1" v-bk-tooltips="'Variable: ${albumartist}'" v-bk-copy="'${albumartist}'">
                                Album Artist:
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.albumartist"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'genre'">
                            <div class="label1">Genre:</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfo.genre"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'Select genre'"
                                    searchable>
                                    <bk-option v-for="option in genreList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'language'">
                            <div class="label1">Language:</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfo.language"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'Select language'"
                                    searchable>
                                    <bk-option v-for="option in languageList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'year'">
                            <div class="label1">Year:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.year"></bk-input>
                            </div>
                        </div>
                        <div style="display: flex;margin-bottom: 10px;flex-direction: column;"
                            v-else-if="item === 'lyrics'">
                            <div style="display: flex;">
                                <div class="label1">Lyrics:</div>
                                <div style="width: 70%;">
                                    <bk-input :clearable="true" v-model="musicInfo.lyrics" type="textarea" :rows="15">
                                    </bk-input>
                                </div>
                                <div>
                                    <bk-icon type="arrows-right-shape" @click="translation()"
                                        style="cursor: pointer;color: #64c864;margin-left: 20px;">
                                    </bk-icon>
                                </div>
                            </div>
                            <div style="display: flex;margin-top: 10px;">
                                <div class="label1">Save Lyrics:</div>
                                <bk-switcher v-model="musicInfo.is_save_lyrics_file"></bk-switcher>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'comment'">
                            <div class="label1">Comment:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.comment" type="textarea"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album_img'">
                            <div class="label1">Album Cover:</div>
                            <div style="display: flex;flex-direction: column;">
                                <div style="width: 70%;display: flex;flex-direction: column;" v-if="reloadImg">
                                    <div>
                                        <bk-upload
                                            :files="files1"
                                            :theme="'picture'"
                                            :multiple="false"
                                            :with-credentials="true"
                                            :header="uploadHeader"
                                            :handle-res-code="handleRes"
                                            :size="{ maxFileSize: 5, maxImgSize: 5 }"
                                            :url="uploadUrl"
                                            name="upload_file"
                                        ></bk-upload>
                                    </div>
                                    <div style="color: #63656e;font-size: 12px;display: flex;">
                                        <div>({{ musicInfo.artwork_w }}*{{ musicInfo.artwork_h }})</div>
                                        <div>{{ musicInfo.artwork_size }}MB</div>
                                    </div>
                                </div>
                                <div style="display: flex;margin-top: 10px;">
                                    <div class="label1">Save Image:</div>
                                    <bk-switcher v-model="musicInfo.is_save_album_cover"></bk-switcher>
                                </div>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'discnumber'">
                            <div class="label1">Disc Number:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.discnumber"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'tracknumber'">
                            <div class="label1">Track Number:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.tracknumber"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'duration'">
                            <div class="label1">Duration:</div>
                            <div style="width: 70%;color: #63656e;font-size: 14px;">
                                {{ musicInfo.duration }} s
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'bit_rate'">
                            <div class="label1">Bit Rate:</div>
                            <div style="width: 70%;color: #63656e;font-size: 14px;">
                                {{ musicInfo.bit_rate }} kbps
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'size'">
                            <div class="label1">File Size:</div>
                            <div style="width: 70%;color: #63656e;font-size: 14px;">
                                {{ musicInfo.size }} MB
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album_type'">
                            <div class="label1">Album Type:</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfo.album_type"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'Select album type'"
                                    searchable>
                                    <bk-option v-for="option in albumTypeList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
            <transition name="bk-slide-fade-left">
                <div style="margin-left: 40px;width: 500px;margin-top: 20px;" v-show="checkedIds.length > 0">
                    <div style="width: 100%;display: flex;">
                        <bk-button :theme="'primary'" :loading="isLoading" @click="handleBatch" class="mr10"
                            style="width: 100%;">
                            Manual Modify
                        </bk-button>
                    </div>
                    <div style="width: 100%;display: flex;margin-top: 10px;">
                        <bk-button :theme="'success'" :loading="isLoading"
                            @click="exampleSetting1.primary.visible = true" class="mr10"
                            style="width: 50%;">
                            Auto Modify
                        </bk-button>
                        <bk-button :theme="'success'" :loading="isLoading"
                            @click="exampleSetting2.primary.visible = true" class="mr10"
                            style="width: 50%;">
                            Organize Folder
                        </bk-button>
                    </div>
                    <bk-divider>
                        <div style="color: gray;font-size: 12px;">Manual Modify Parameters</div>
                    </bk-divider>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;margin-top: 10px;">
                        <div class="label1 can-copy" v-bk-tooltips="'Variable: ${title}'" v-bk-copy="'${title}'">Title:</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfoManual.title"
                                :placeholder="'Supports batch variable modification'"></bk-input>
                        </div>
                    </div>
                    <div v-for="(item, index) in showFields" :key="'l2' + index">
                        <div class="edit-item" v-if="item === 'filename'">
                            <div class="label1 can-copy" v-bk-tooltips="'Variable: ${filename}'" v-bk-copy="'${filename}'">
                                Filename:
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.filename"
                                    :placeholder="'Example: ${title}-${album}'"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'artist'">
                            <div class="label1 can-copy" v-bk-tooltips="'Variable: ${artist}'" v-bk-copy="'${artist}'">Artist:
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.artist"
                                    :placeholder="'Hover over title to see available variables'"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album'">
                            <div class="label1 can-copy" v-bk-tooltips="'Variable: ${album}'" v-bk-copy="'${album}'">Album:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.album"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'albumartist'">
                            <div class="label1 can-copy" v-bk-tooltips="'Variable: ${albumartist}'"
                                v-bk-copy="'${albumartist}'">Album Artist:
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.albumartist"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'genre'">
                            <div class="label1">Genre:</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfoManual.genre"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'Select genre'"
                                    searchable>
                                    <bk-option v-for="option in genreList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'language'">
                            <div class="label1">Language:</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfoManual.language"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'Select language'"
                                    searchable>
                                    <bk-option v-for="option in languageList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'year'">
                            <div class="label1">Year:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.year"></bk-input>
                            </div>
                        </div>
                        <div style="display: flex;margin-bottom: 10px;flex-direction: column;"
                            v-else-if="item === 'lyrics'">
                            <div style="display: flex;">
                                <div class="label1">Lyrics:</div>
                                <div style="width: 70%;">
                                    <bk-input :clearable="true" v-model="musicInfoManual.lyrics" type="textarea"
                                        :rows="15"
                                    ></bk-input>
                                </div>
                            </div>
                            <div style="display: flex;margin-top: 10px;">
                                <div class="label1">Save Lyrics:</div>
                                <bk-switcher v-model="musicInfoManual.is_save_lyrics_file"></bk-switcher>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'comment'">
                            <div class="label1">Comment:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.comment"
                                    type="textarea"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album_img'">
                            <div class="label1">Album Cover:</div>
                            <div style="display: flex;flex-direction: column;">
                                <div style="width: 70%;display: flex;flex-direction: column;" v-if="reloadImg">
                                    <div>
                                        <bk-upload
                                            :files="files1"
                                            :theme="'picture'"
                                            :multiple="false"
                                            :with-credentials="true"
                                            :header="uploadHeader"
                                            :handle-res-code="handleResBatch"
                                            :size="{ maxFileSize: 5, maxImgSize: 5 }"
                                            :url="uploadUrl"
                                            name="upload_file"
                                        ></bk-upload>
                                    </div>
                                </div>
                                <div style="display: flex;margin-top: 10px;">
                                    <div class="label1">Save Image:</div>
                                    <bk-switcher v-model="musicInfoManual.is_save_album_cover"></bk-switcher>
                                </div>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'discnumber'">
                            <div class="label1" v-bk-tooltips="'Variable: ${discnumber}'">Disc Number:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.discnumber"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'tracknumber'">
                            <div class="label1" v-bk-tooltips="'Variable: ${tracknumber}'">Track Number:</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.tracknumber"></bk-input>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
        <div class="resource-section">
            <transition name="bk-slide-fade-left">
                <div
                    style="display: flex;flex-direction: column;margin-top: 20px;flex: 1;margin-right: 20px;margin-left: 20px;"
                    v-show="fadeShowDetail">
                    <div v-if="SongList.length === 0">
                        <span style="margin-left: 30%;margin-top: 30%;">No song information available</span>
                    </div>
                    <div v-else>
                        <div class="parent">
                            <div class="title2">Apply</div>
                            <div class="title2">Cover</div>
                            <div class="title2">Title</div>
                            <div class="title2">Artist</div>
                            <div class="title2">Album</div>
                            <div class="title2">Lyrics</div>
                            <div class="title2">Year</div>
                        </div>
                        <div v-for="(item,index) in SongList" :key="index" style="margin-bottom: 10px;" class="parent">
                            <bk-icon type="arrows-left-shape" @click="copyAll(item)"
                                style="margin-right: 5px;cursor: pointer;"></bk-icon>
                            <div v-if="resource === 'smart_tag'">
                                <bk-badge class="mr40" :theme="'warning'" :val="item.score" radius="20%">
                                    <bk-image fit="contain" :src="item.album_img"
                                        style="width: 64px;cursor: pointer;"
                                        @click="handleCopy('album_img',item.album_img)">
                                    </bk-image>
                                </bk-badge>
                            </div>
                            <div v-else>
                                <bk-image fit="contain" :src="item.album_img"
                                    style="width: 64px;cursor: pointer;"
                                    @click="handleCopy('album_img',item.album_img)">
                                </bk-image>
                            </div>
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
                            <div @click="handleCopy('lyric',item)" class="music-item">Load Lyrics</div>
                            <div @click="handleCopy('year',item.year)" class="music-item">
                                {{
                                    item.year
                                }}
                            </div>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                        </div>
                    </div>
                </div>
            </transition>
            <transition name="bk-slide-fade-left">
                <div v-show="showTranslation">
                    <div style="display: flex;height: 100%;">
                        <bk-icon type="arrows-left-shape" @click="handleCopy('lyric_tran',translationText)"
                            style="margin-right: 5px;margin-left: 15px;margin-top: 50%;cursor: pointer;"></bk-icon>
                        <div style="width: 100%;height: 100%;">
                            <bk-input :clearable="true" v-model="translationText" type="textarea" :rows="50"
                                style="height: 100%;">
                            </bk-input>
                        </div>
                    </div>
                </div>
            </transition>
            <div v-show="!fadeShowDetail && !showTranslation"
                style="width: 90%;height: 90%; margin: 50px 20px 20px 50px;">
                <bk-image fit="contain" :src="'/static/dist/img/music_null-cutout.png'"
                    style="width: 100%;height: 98%;"></bk-image>
            </div>
        </div>
        <bk-dialog v-model="exampleSetting1.primary.visible"
            theme="primary"
            :mask-close="false"
            @confirm="handleBatchAuto"
            :header-position="exampleSetting1.primary.headerPosition"
            title="Auto Batch Modify">
            <p>Loose mode: Match metadata only by title, may include covers or remixes.</p>
            <p>Strict mode: Match metadata by title and artist, or title and album, more accurate.</p>
            <bk-radio-group v-model="selectAutoMode">
                <bk-radio-button value="simple">
                    Loose Mode
                </bk-radio-button>
                <bk-radio-button value="hard">
                    Strict Mode
                </bk-radio-button>
            </bk-radio-group>
            <div>Music Source Order</div>
            <bk-select style="width: 250px;"
                searchable
                multiple
                show-select-all
                v-model="sourceList">
                <bk-option v-for="option in resourceListBatch"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
        </bk-dialog>
        <bk-dialog v-model="exampleSetting2.primary.visible"
            theme="primary"
            :mask-close="false"
            @confirm="handleTidy"
            :header-position="exampleSetting2.primary.headerPosition"
            title="Organize Folder">
            <p>Organize folder by selected information for first and second level directories</p>
            <div>Root directory after organization</div>
            <div class="input-demo">
                <bk-input v-model="tidyFormData.root_path">
                </bk-input>
            </div>
            <div>First level directory</div>
            <bk-select style="width: 250px;"
                :clearable="false"
                v-model="tidyFormData.first_dir">
                <bk-option v-for="option in tidyList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
            <div>Second level directory</div>
            <bk-select style="width: 250px;"
                v-model="tidyFormData.second_dir">
                <bk-option v-for="option in tidyList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
        </bk-dialog>
        <bk-dialog v-model="exampleSetting3.primary.visible"
            theme="primary"
            :mask-close="false"
            @confirm="handleSettings"
            :header-position="exampleSetting3.primary.headerPosition"
            title="Settings">
            <p>Select your settings, browser will save your defaults</p>
            <div>Tag Source</div>
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
            <div>Display Fields and Order</div>
            <bk-select style="width: 350px;margin-top: 10px;"
                searchable
                :clearable="false"
                multiple
                display-tag
                v-model="showFields">
                <bk-option v-for="option in fieldList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
        </bk-dialog>
    </div>
</template>
<script>
    import {mapGetters} from 'vuex'

    export default {
        data() {
            return {
                files1: [],
                uploadUrl: '/api/upload_image/',
                uploadHeader: [
                    {name: 'X-CSRFToken', value: this.getCookie('django_vue_cli_csrftoken')},
                    {name: 'AUTHORIZATION', value: this.getCookie('AUTHORIZATION')}
                ],
                showFields: localStorage.getItem('showFields') ? JSON.parse(localStorage.getItem('showFields')) : ['filename', 'artist', 'album', 'albumartist', 'genre', 'year', 'lyrics', 'comment', 'album_img'],
                fieldList: [
                    {id: 'filename', name: 'Filename'},
                    {id: 'artist', name: 'Artist'},
                    {id: 'album', name: 'Album'},
                    {id: 'album_type', name: 'Album Type'},
                    {id: 'albumartist', name: 'Album Artist'},
                    {id: 'discnumber', name: 'Disc Number'},
                    {id: 'tracknumber', name: 'Track Number'},
                    {id: 'genre', name: 'Genre'},
                    {id: 'year', name: 'Year'},
                    {id: 'lyrics', name: 'Lyrics'},
                    {id: 'comment', name: 'Comment'},
                    {id: 'album_img', name: 'Album Cover'},
                    {id: 'duration', name: 'Duration'},
                    {id: 'size', name: 'File Size'},
                    {id: 'bit_rate', name: 'Bit Rate'},
                    {id: 'language', name: 'Language'}
                ],
                albumTypeList: [
                    {id: 'album;compilation', name: 'Compilation'},
                    {id: 'album;live', name: 'Live'},
                    {id: 'album;remix', name: 'Remix'},
                    {id: 'album;soundtrack', name: 'Soundtrack'},
                    {id: 'album;demo', name: 'Demo'},
                    {id: 'album;album', name: 'Album'},
                    {id: 'ep', name: 'EP'},
                    {id: 'single', name: 'Single'}
                ],
                searchWord: '',
                treeListOne: [],
                fullPath: '',
                fileName: '',
                resource: localStorage.getItem('resource') ? localStorage.getItem('resource') : 'netease',
                translationText: '',
                resourceList: [
                    {id: 'acoustid', name: 'Fingerprint Recognition'},
                    {id: 'netease', name: 'Netease Music'},
                    {id: 'migu', name: 'Migu Music'},
                    {id: 'qmusic', name: 'QQ Music'},
                    {id: 'kugou', name: 'Kugou Music'},
                    {id: 'smart_tag', name: 'Smart Tag'}
                ],
                resourceListBatch: [
                    {id: 'netease', name: 'Netease Music'},
                    {id: 'migu', name: 'Migu Music'},
                    {id: 'qmusic', name: 'QQ Music'},
                    {id: 'kugou', name: 'Kugou Music'}
                ],
                tidyList: [
                    {id: 'title', name: 'Title'},
                    {id: 'artist', name: 'Artist'},
                    {id: 'album', name: 'Album'},
                    {id: 'albumartist', name: 'Album Artist'},
                    {id: 'album_type', name: 'Album Type'},
                    {id: 'genre', name: 'Genre'},
                    {id: 'language', name: 'Language'},
                    {id: 'comment', name: 'Comment'}
                ],
                baseMusicInfo: {
                    'genre': 'Pop',
                    'is_save_lyrics_file': false,
                    'is_save_album_cover': false
                },
                musicInfo: {
                    'genre': 'Pop',
                    'is_save_lyrics_file': false,
                    'is_save_album_cover': false
                },
                musicInfoManual: {
                    'genre': 'Pop',
                    'is_save_lyrics_file': false,
                    'is_save_album_cover': false
                },
                fadeShowDir: false,
                fadeShowDetail: false,
                showTranslation: false,
                isLoading: false,
                SongList: [],
                reloadImg: true,
                genreList: [
                    {'id': 'Pop', name: 'Pop'},
                    {'id': 'Rock', name: 'Rock'},
                    {'id': 'Rap', name: 'Rap'},
                    {'id': 'Folk', name: 'Folk'},
                    {'id': 'Electronic', name: 'Electronic'},
                    {'id': 'Jazz', name: 'Jazz'},
                    {'id': 'Instrumental', name: 'Instrumental'},
                    {'id': 'Metal', name: 'Metal'},
                    {'id': 'World Music', name: 'World Music'},
                    {'id': 'New Age', name: 'New Age'},
                    {'id': 'Classical', name: 'Classical'},
                    {'id': 'Indie', name: 'Indie'},
                    {'id': 'Ambient', name: 'Ambient'}
                ],
                languageList: [
                    {'id': 'Chinese', name: 'Chinese'},
                    {'id': 'English', name: 'English'},
                    {'id': 'Japanese', name: 'Japanese'},
                    {'id': 'Korean', name: 'Korean'},
                    {'id': 'Thai', name: 'Thai'},
                    {'id': 'Unknown', name: 'Unknown'}
                ],
                checkedIds: [],
                checkedData: [],
                selectAutoMode: 'hard',
                sourceList: [],
                tidyFormData: {
                    root_path: '/app/media/',
                    first_dir: 'artist',
                    second_dir: ''
                },
                exampleSetting1: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    }
                },
                exampleSetting2: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    }
                },
                exampleSetting3: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    }
                },
                sortedField: localStorage.getItem('sortedField') ? JSON.parse(localStorage.getItem('sortedField')) : []
            }
        },
        computed: {
            ...mapGetters(['geFullPath']),
            filePath: {
                get() {
                    if (this.geFullPath) {
                        console.log(this.geFullPath)
                        const fullPath = this.geFullPath
                        this.$store.commit('setFullPath', '')
                        this.$nextTick(() => {
                            this.handleSearchFile()
                        })
                        return fullPath
                    } else {
                        return '/app/media/'
                    }
                },
                set(value) {
                    this.$store.commit('setFullPath', value)
                }
            }
        },
        created() {
            this.handleSearchFile()
        },
        methods: {
            tpl(node, ctx) {
                // If h is not auto-injected, it will be the first parameter, but currently it's at the end to avoid breaking existing usage.
                const titleClass = node.selected ? 'node-title node-selected' : 'node-title ' + node.state
                if (node.title.length > 25) {
                    return <span>
                    <span class={titleClass} domPropsInnerHTML={node.title.slice(0, 25)}
                        onClick={() => {
                            this.nodeClickOne(node)
                        }} v-bk-tooltips={node.title}>
                    </span>
                    </span>
                } else {
                    return <span>
                    <span class={titleClass} domPropsInnerHTML={node.title.slice(0, 25)}
                        onClick={() => {
                            this.nodeClickOne(node)
                        }}>
                    </span>
                    </span>
                }
            },
            backDir() {
                this.filePath = this.backPath(this.filePath)
            },
            backPath(path) {
                const regex = /\/([^\/]+)\/?$/
                const match = regex.exec(path)

                if (match) {
                    const parentPath = path.slice(0, match.index)
                    return parentPath
                }

                return path
            },
            nodeClickOne(node) {
                if (node.icon === 'icon-folder') {
                    this.filePath = this.filePath + '/' + node.name
                } else {
                    if (node.children && node.children.length > 0) {
                        return
                    }
                    this.musicInfo = this.baseMusicInfo
                    this.fileName = node.name
                    this.fullPath = this.filePath + '/' + node.name
                    this.$api.Task.musicId3({'file_path': this.filePath, 'file_name': node.name}).then((res) => {
                        console.log(res)
                        if (res.result) {
                            this.musicInfo = res.data
                            this.musicInfo.is_save_lyrics_file = false
                            this.musicInfo.is_save_album_cover = false
                            this.files1 = [
                                {
                                    name: 'cover.png',
                                    status: 'done',
                                    url: this.musicInfo.artwork
                                }
                            ]
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                    })
                }
            },
            nodeCheckTwo(node, checked) {
                console.log(node, checked)
                if (checked) {
                    this.musicInfo = this.baseMusicInfo
                    if (node.children && node.children.length > 0) {
                        this.checkedData = []
                        this.checkedIds = []
                        node.children.forEach(el => {
                            this.checkedData.push({
                                checked: el.checked,
                                icon: el.icon,
                                id: el.id,
                                name: el.name,
                                title: el.title
                            })
                            this.checkedIds.push(el.id)
                        })
                    } else {
                        this.checkedData.push({
                            checked: node.checked,
                            icon: node.icon,
                            id: node.id,
                            name: node.name,
                            title: node.title
                        })
                        this.checkedIds.push(node.id)
                    }
                } else {
                    if (node.children && node.children.length > 0) {
                        this.checkedData = []
                        this.checkedIds = []
                    } else {
                        const index = this.checkedIds.indexOf(node.id)
                        if (index !== -1) {
                            this.checkedData.splice(index, 1)
                            this.checkedIds.splice(index, 1)
                        }
                    }
                }
                console.log(this.checkedIds)
            },
            handleCopy(k, v) {
                if (k === 'lyric') {
                    const resurce = this.resource !== 'smart_tag' ? this.resource : v.resource
                    this.$api.Task.fetchLyric({'song_id': v.id, 'resource': resurce}).then((res) => {
                        if (res.result) {
                            this.musicInfo['lyrics'] = res.data
                        } else {
                            this.$cwMessage('Lyrics not found', 'error')
                        }
                    })
                } else if (k === 'album_img') {
                    this.musicInfo[k] = v
                    this.files1 = [
                        {
                            name: 'cover.png',
                            status: 'done',
                            url: v
                        }
                    ]
                    this.reloadImg = false
                    this.$nextTick(() => {
                        this.reloadImg = true
                    })
                } else if (k === 'lyric_tran') {
                    this.musicInfo['lyrics'] = v
                } else {
                    this.musicInfo[k] = v
                }
            },
            copyAll(item) {
                this.handleCopy('title', item.name)
                this.handleCopy('year', item.year)
                this.handleCopy('lyric', item)
                this.handleCopy('album', item.album)
                this.handleCopy('artist', item.artist)
                this.handleCopy('album_img', item.album_img)
            },
            nodeExpandedOne(node, expanded) {
            },
            toggleLock(mode) {
                if (mode === 'title') {
                    if (!this.musicInfo.title) {
                        this.$cwMessage('Title cannot be empty', 'error')
                        return
                    }
                    this.showTranslation = false
                    this.fadeShowDetail = false
                    this.$api.Task.fetchId3Title({
                        title: this.musicInfo.title,
                        resource: this.resource,
                        full_path: this.fullPath
                    }).then((res) => {
                        this.fadeShowDetail = true
                        this.SongList = res.data
                    })
                }
            },
            translation() {
                if (!this.musicInfo.lyrics) {
                    this.$cwMessage('Lyrics cannot be empty', 'error')
                }
                this.fadeShowDetail = false
                this.showTranslation = true
                this.$api.Task.translationLyc({
                    lyc: this.musicInfo.lyrics
                }).then((res) => {
                    this.showTranslation = true
                    this.translationText = res.data
                })
            },
            handleSearchFile() {
                this.fadeShowDir = false
                this.checkedData = []
                this.checkedIds = []
                this.$api.Task.fileList({'file_path': this.filePath, sorted_fields: this.sortedField}).then((res) => {
                    if (res.result) {
                        this.treeListOne = res.data
                        this.fadeShowDir = true
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                })
            },
            handleSearch() {
                this.$refs.tree1.searchNode(this.searchWord)
                const searchResult = this.$refs.tree1.getSearchResult()
                this.isEmpty = searchResult.isEmpty
            },
            handleClick() {
                console.log(this.musicInfo)
                const params = [{
                    'file_full_path': this.filePath + '/' + this.fileName,
                    ...this.musicInfo
                }]
                this.isLoading = true
                this.$api.Task.updateId3({'music_id3_info': params}).then((res) => {
                    this.isLoading = false
                    if (res.result) {
                        this.$cwMessage('Save successful', 'success')
                        this.$store.commit('setHasMsg', true)
                    } else {
                        this.$cwMessage('Save failed', 'error')
                    }
                })
            },
            handleBatch() {
                this.$bkInfo({
                    title: 'Confirm batch modification?',
                    confirmLoading: true,
                    confirmFn: () => {
                        try {
                            this.isLoading = true

                            this.$api.Task.batchUpdateId3({
                                'file_full_path': this.filePath,
                                'select_data': this.checkedData,
                                'music_info': this.musicInfoManual
                            }).then((res) => {
                                this.isLoading = false
                                console.log(res)
                                if (res.result) {
                                    this.$cwMessage('Save successful', 'success')
                                }
                            })
                            return true
                        } catch (e) {
                            console.warn(e)
                            return false
                        }
                    }
                })
            },
            handleBatchAuto() {
                this.$bkInfo({
                    title: 'Confirm batch modification?',
                    confirmLoading: true,
                    confirmFn: () => {
                        try {
                            this.isLoading = true
                            this.musicInfoManual['select_mode'] = this.selectAutoMode
                            this.musicInfoManual['source_list'] = this.sourceList
                            this.$api.Task.batchAutoUpdateId3({
                                'file_full_path': this.filePath,
                                'select_data': this.checkedData,
                                'music_info': this.musicInfoManual
                            }).then((res) => {
                                this.isLoading = false
                                console.log(res)
                                if (res.result) {
                                    this.$cwMessage('Batch processing created successfully', 'success')
                                    this.$store.commit('setHasMsg', true)
                                }
                            })
                            return true
                        } catch (e) {
                            console.warn(e)
                            return false
                        }
                    }
                })
            },
            handleTidy() {
                this.$bkInfo({
                    title: 'Confirm folder organization?',
                    confirmLoading: true,
                    confirmFn: () => {
                        try {
                            this.isLoading = true
                            this.tidyFormData['file_full_path'] = this.filePath
                            this.tidyFormData['select_data'] = this.checkedData
                            this.$api.Task.tidyFolder(this.tidyFormData).then((res) => {
                                this.isLoading = false
                                console.log(res)
                                if (res.result) {
                                    this.$cwMessage('Folder organization completed', 'success')
                                    this.handleSearchFile()
                                } else {
                                    this.$cwMessage('Folder organization failed', 'error')
                                }
                            })
                            return true
                        } catch (e) {
                            console.warn(e)
                            return false
                        }
                    }
                })
            },
            changeSorted(element) {
                if (this.sortedField.includes(element)) {
                    this.sortedField.splice(this.sortedField.indexOf(element), 1)
                } else {
                    this.sortedField.push(element)
                }
                const obj = JSON.stringify(this.sortedField)
                window.localStorage.setItem('sortedField', obj)
                this.handleSearchFile()
            },
            handleSettings() {
                const obj = JSON.stringify(this.showFields)
                window.localStorage.setItem('showFields', obj)
                window.localStorage.setItem('resource', this.resource)
            },
            handleRes(response) {
                if (response.result) {
                    this.musicInfo.album_img = response.data
                    return true
                } else {
                    return false
                }
            },
            handleResBatch(response) {
                if (response.result) {
                    this.musicInfoManual.album_img = response.data
                    return true
                } else {
                    return false
                }
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
    margin-bottom: 15px;
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

@media (max-width: 500px) {
    .file-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: scroll;
        width: 100vh;
        border: 1px solid #173769;
        margin: 10px 0 10px 10px;
        border-radius: 20px;
    }
    .edit-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: scroll;
        width: 100vh;
        border: 1px solid #173769;
        margin: 10px 10px 10px 10px;
        border-radius: 20px;
    }

    .resource-section {
        background: #fff;
        height: calc(100vh - 75px);
        width: 100vh;
        flex: 1;
        overflow: scroll;
        border: 1px solid #173769;
        margin: 10px 10px 10px 0;
        border-radius: 20px;
    }
}

@media (min-width: 400px) {
    .file-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: scroll;
        min-width: 400px;
        border: 1px solid #173769;
        margin: 10px 0 10px 10px;
        border-radius: 20px;
    }

    .edit-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: scroll;
        border: 1px solid #173769;
        margin: 10px 10px 10px 10px;
        border-radius: 20px;
    }

    .resource-section {
        background: #fff;
        height: calc(100vh - 75px);
        min-width: 400px;
        flex: 1;
        overflow: scroll;
        border: 1px solid #173769;
        margin: 10px 10px 10px 0;
        border-radius: 20px;
    }
}

.bk-form-checkbox {
    margin-right: 10px;
}

.success {
    color: #d1cfc5;
}

.failed {
    color: #ac354b;
}

.null {
    color: #333146;
}

button.bk-success {
    background-color: rgb(17, 64, 108) !important;
    border-color: rgb(17, 64, 108) !important;
}

button.bk-primary {
    background-color: rgb(17, 64, 108) !important;
    border-color: rgb(17, 64, 108) !important;
}

button.bk-button-text {
    background-color: transparent !important;
}

.bk-form-checkbox.is-checked .bk-checkbox {
    border-color: rgb(17, 64, 108) !important;
    background-color: rgb(17, 64, 108) !important;
    background-clip: border-box !important;
}

.bk-button-group .bk-button.is-selected {
    border-color: rgb(17, 64, 108) !important;
    color: rgb(17, 64, 108) !important;
}

.bk-button.bk-default:hover {
    border-color: rgb(17, 64, 108) !important;
    color: rgb(17, 64, 108) !important;
}

.bk-form-radio input[type=radio].is-checked {
    color: rgb(17, 64, 108) !important;
}

.bk-steps .bk-step.current .bk-step-icon, .bk-steps .bk-step.current .bk-step-number, .bk-steps .bk-step.current .bk-step-text {
    border-color: rgb(17, 64, 108) !important;
    background-color: rgb(17, 64, 108) !important;
}

.bk-steps .bk-step.done .bk-step-icon, .bk-steps .bk-step.done .bk-step-number, .bk-steps .bk-step.done .bk-step-text {
    border-color: rgb(17, 64, 108) !important;
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-left-circle {
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-right-circle {
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-right-shape {
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-right-shape:hover {
    color: #df4d40 !important;
}

.bk-icon.icon-arrows-left-shape:hover {
    color: #df4d40 !important;
}

.bk-icon.icon-arrows-down-shape:hover {
    color: #df4d40 !important;
}

::-webkit-scrollbar {
    width: 0;
    background-color: transparent;
}

::-webkit-scrollbar-thumb {
    background-color: #f4f5f0;
}

.isSelected {
    background-color: #ecf3fe;
}

.edit-item {
    display: flex;
    margin-bottom: 10px;
    align-items: center;
}

.can-copy {
    cursor: pointer;
}
</style>
