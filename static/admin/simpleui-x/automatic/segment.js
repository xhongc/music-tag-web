if (!window.dicts) {
    window.dicts = {}
}

function Segment() {
    //初始化词库
    let mappers = {}

    for (let key in dicts) {
        let array = dicts[key];
        array.map((value, index) => {
            mappers[value.toUpperCase()] = key;
        });
    }
    this.getMappers = function () {
        return mappers;
    }
    this.cut = function (sentence) {
        let start = 0, end = sentence.length - 1;
        while (start !== end) {
            let str = [];
            for (let i = start; i <= end; i++) {
                let s = sentence.substring(i, i + 1);

                str.push(s);
                // 如果在字典中，则添加到分词结果集

                let val = mappers[str.join('').toUpperCase().replace(/ /g, '')];
                if (val) {
                    return val;
                }
            }

            start++;
        }


    }
}

const segment = new Segment();

function getIcon(name, icon) {
    if(!name){
        return;
    }
    let value = 'far fa-circle';
    if (icon) {
        //有默认图标的
        if (icon !== value) {
            return icon;
        }
    }

    return segment.cut(name) || value;
}