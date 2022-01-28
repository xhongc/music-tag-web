function getMonthLength(date) {
    const d = new Date(date)
    d.setMonth(d.getMonth() + 1)
    d.setDate('1')
    d.setDate(d.getDate() - 1)
    return d.getDate()
}

export function getYearWeekDay(str) {
    const arr = []
    for (let i = 1; i <= 12; i++) {
        const days = getMonthLength(`${str}-${i}-01`)
        for (let j = 1; j <= days; j++) {
            if (new Date(`${str}-${i}-${j}`).getDay() === 0 || new Date(`2021-${i}-${j}`).getDay() === 6) {
                if ((i > 0 && i < 10) && (j > 0 && j < 10)) {
                    arr.push(`${str}-0${i}-0${j}`)
                }
                if ((i > 0 && i < 10) && j >= 10) {
                    arr.push(`${str}-0${i}-${j}`)
                }
                if (i >= 10 && (j > 0 && j < 10)) {
                    arr.push(`${str}-${i}-0${j}`)
                }
                if (i >= 10 && j >= 10) {
                    arr.push(`${str}-${i}-${j}`)
                }
            }
        }
    }
    return arr
}

export function getWorkDays(str) {
    const arr = []
    for (let i = 1; i <= 12; i++) {
        const days = getMonthLength(`${str}-${i}-01`)
        for (let j = 1; j <= days; j++) {
            if (new Date(`${str}-${i}-${j}`).getDay() !== 0 && new Date(`2021-${i}-${j}`).getDay() !== 6) {
                if ((i > 0 && i < 10) && (j > 0 && j < 10)) {
                    arr.push(`${str}-0${i}-0${j}`)
                }
                if ((i > 0 && i < 10) && j >= 10) {
                    arr.push(`${str}-0${i}-${j}`)
                }
                if (i >= 10 && (j > 0 && j < 10)) {
                    arr.push(`${str}-${i}-0${j}`)
                }
                if (i >= 10 && j >= 10) {
                    arr.push(`${str}-${i}-${j}`)
                }
            }
        }
    }
    return arr
}
