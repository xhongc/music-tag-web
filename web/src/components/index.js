// import container from './base/container'
// import header from './base/header'
// import headerMenu from './base/headerMenu'
// import leftMenu from './base/leftMenu'
// import CWView from './element/iView'
// import iViewTwo from './element/iViewTwo'
// import Buttons from './element/Buttons'
// import CWCollapse from './collapse/cw-collapse'
// import CWTable from './table/cw-table'
// import CWTransfer from './transfer/CWTransfer.vue'
// import CWDropDown from './dropDown/dropDown.vue'
// import CWCodeMirror from './codeMirror/codeMirror.vue'

const components = [
    // container,
    // header,
    // headerMenu,
    // leftMenu,
    // CWView,
    // CWTable,
    // CWDropDown,
    // iViewTwo,
    // Buttons,
    // CWCollapse,
    // CWCodeMirror,
    // CWTransfer
]

const install = function(Vue) {
    components.forEach(component => {
        Vue.component(component.name, component)
    })
}
export default install
