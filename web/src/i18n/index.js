import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)

const messages = {
  en: {
    common: {
      save: 'Save',
      cancel: 'Cancel',
      submit: 'Submit',
      delete: 'Delete',
      edit: 'Edit',
      back: 'Back',
      search: 'Search',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success'
    },
    home: {
      enterFolderPath: 'Enter folder path:',
      searchByFilename: 'Search by filename',
      name: 'Name',
      modifiedTime: 'Modified Time',
      size: 'Size',
      saveInfo: 'Save Info',
      title: 'Title',
      filename: 'Filename',
      artist: 'Artist',
      album: 'Album',
      albumArtist: 'Album Artist',
      genre: 'Genre',
      language: 'Language',
      year: 'Year',
      lyrics: 'Lyrics',
      saveLyrics: 'Save Lyrics',
      comment: 'Comment',
      albumCover: 'Album Cover',
      saveImage: 'Save Image',
      discNumber: 'Disc Number',
      trackNumber: 'Track Number',
      duration: 'Duration',
      bitRate: 'Bit Rate',
      fileSize: 'File Size',
      albumType: 'Album Type',
      manualModify: 'Manual Modify',
      autoModify: 'Auto Modify',
      organizeFolder: 'Organize Folder',
      configuration: 'Configuration',
      tagSource: 'Tag Source',
      displayFields: 'Display Fields and Order'
    },
    login: {
      username: 'Username',
      password: 'Password',
      login: 'Login',
      signup: 'Sign up'
    }
  },
  zh: {
    common: {
      save: '保存',
      cancel: '取消',
      submit: '提交',
      delete: '删除',
      edit: '编辑',
      back: '返回',
      search: '搜索',
      loading: '加载中...',
      error: '错误',
      success: '成功'
    },
    home: {
      enterFolderPath: '请输入文件夹路径：',
      searchByFilename: '根据文件名称搜索',
      name: '名称',
      modifiedTime: '修改时间',
      size: '大小',
      saveInfo: '保存信息',
      title: '标题',
      filename: '文件名',
      artist: '艺术家',
      album: '专辑',
      albumArtist: '专辑艺术家',
      genre: '风格',
      language: '语言',
      year: '年份',
      lyrics: '歌词',
      saveLyrics: '保存歌词',
      comment: '描述',
      albumCover: '专辑封面',
      saveImage: '保存图片',
      discNumber: '光盘编号',
      trackNumber: '音轨号',
      duration: '时长',
      bitRate: '比特率',
      fileSize: '文件大小',
      albumType: '专辑类型',
      manualModify: '手动修改',
      autoModify: '自动修改',
      organizeFolder: '整理文件夹',
      configuration: '配置',
      tagSource: '标签来源',
      displayFields: '展示的字段以及顺序'
    },
    login: {
      username: '用户名',
      password: '密码',
      login: '登录',
      signup: '注册'
    }
  }
}

const i18n = new VueI18n({
  locale: localStorage.getItem('app-language') || 'en',
  messages
})

export default i18n