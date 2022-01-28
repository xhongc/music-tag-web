// 统一引入api模块
import alarmCenter from './apiUrl/system/alarm_center'
import auditLog from './apiUrl/system/audit_log'
import category from './apiUrl/system/category'
import home from './apiUrl/system/home'
import setting from './apiUrl/system/setting'
import user from './apiUrl/system/user'
import showTable from './apiUrl/system/show_table'

import calendar from './apiUrl/template/calendar'
import content from './apiUrl/template/content'
import process from './apiUrl/template/process'
import node from './apiUrl/template/node'
import station from './apiUrl/template/station'
import stationState from './apiUrl/template/station_state'
import varTable from './apiUrl/template/var_table'

import nodeRun from './apiUrl/monitor/node_run'
import processRun from './apiUrl/monitor/process_run'
import processReport from './apiUrl/report/process_report'

import nodeHistory from './apiUrl/history/node_history'
import processHistory from './apiUrl/history/process_history'

export default {
    alarmCenter,
    auditLog,
    category,
    home,
    setting,
    user,
    calendar,
    content,
    process,
    node,
    station,
    stationState,
    varTable,
    nodeRun,
    processRun,
    nodeHistory,
    processHistory,
    processReport,
    showTable
}
