module.exports = {
    "extends": [
    ],
    "plugins": [
        "stylelint-scss"
    ],
    "rules": {
        // http://stylelint.cn/user-guide/rules/
        // 要求在 at 规则之后有一个一个空格
        "at-rule-name-space-after": "always",

        // 禁止使用未知的 at 规则
        "at-rule-no-unknown": true,

        // 要求在 at 规则的分号之后有一个换行符
        "at-rule-semicolon-newline-after": "always",

        // 在开括号之后要求有一个换行符
        "block-opening-brace-newline-after": "always",

        // 在括开号之前要求有空白
        "block-opening-brace-space-before": "always",

        // 禁止在闭括号之前有空行
        "block-closing-brace-empty-line-before": "never",

        // 在闭括号之后要求有一个换行符，或禁止有空白
        "block-closing-brace-newline-after": "always",

        // 在闭括号之前要求有一个换行符
        "block-closing-brace-newline-before": "always",

        // 禁止出现空块
        "block-no-empty": true,

        // 指定十六进制颜色不使用缩写
        // "color-hex-length": "short",

        // 不止使用命名的颜色
        "color-named": "never",

        // 禁止使用无效的十六进制颜色
        "color-no-invalid-hex": true,

        // 禁止空注释
        "comment-no-empty": true,

        // 在感叹号之后禁止有空白。
        "declaration-bang-space-after": "never",

        // 在感叹号之前要求有一个空格
        "declaration-bang-space-before": "always",

        // 在声明的块中中禁止出现重复的属性
        "declaration-block-no-duplicate-properties": true,

        // 禁止使用可以缩写却不缩写的属性（试用）
        "declaration-block-no-redundant-longhand-properties": true,

        // 在声明块的分号之后要求有一个换行符
        "declaration-block-semicolon-newline-after": "always-multi-line",

        // 在声明块的分号之前要求禁止有空白
        "declaration-block-semicolon-newline-before": "never-multi-line",

        // 在声明块的分号之后前要求禁止有空白
        "declaration-block-semicolon-space-before": "never",

        // 限制单行声明块中声明的数量
        "declaration-block-single-line-max-declarations": 1,

        // 要求在声明块中使用拖尾分号
        "declaration-block-trailing-semicolon": "always",

        // 在冒号之后要求有一个空格
        "declaration-colon-space-after": "always",

        // 在冒号之前要求禁止有空白
        "declaration-colon-space-before": "never",

        // 禁止在声明语句之前有空行
        "declaration-empty-line-before": "never",

        // 禁止使用重复的字体名称
        "font-family-no-duplicate-names": true,

        // 禁止在 calc 函数内使用不加空格的操作符
        "function-calc-no-unspaced-operator": true,

        // 在函数的逗号之后要求有一个空格
        "function-comma-space-after": "always",

        // 在函数的逗号之前要求禁止有空白
        "function-comma-space-before": "never",

        // 指定函数名称的大小写
        "function-name-case": "lower",

        // 指定缩进
        "indentation": 4,

        // 长度为0时，禁止使用单位
        "length-zero-no-unit": true,

        // 限制相邻空行的数量
        "max-empty-lines": 1,

        // 在 media 特性中的冒号之后要求有一个空格
        "media-feature-colon-space-after": "always",

        // 在 media 特性中的冒号之前要求禁止有空白
        "media-feature-colon-space-before": "never",

        // 禁止低优先级的选择器出现在高优先级的选择器之后
        // "no-descending-specificity": true,

        // 在一个样式表中禁止出现重复的选择器
        // "no-duplicate-selectors": true,

        // 禁止空源
        "no-empty-source": true,

        // 禁止行尾空格
        "no-eol-whitespace": true,

        // 禁止多余的分号
        "no-extra-semicolons": true,

        // 禁用 CSS 不支持的双斜线注释 (//...)
        "no-invalid-double-slash-comments": true,

        // 禁止动画名称与 @keyframes 声明不符
        "no-unknown-animations": true,

        // 禁止数字中的拖尾 0
        "number-no-trailing-zeros": true,

        // 指定属性的大小写
        "property-case": "lower",

        // 禁止使用未知属性
        "property-no-unknown": true,

        // 禁止属性使用浏览器引擎前缀
        // "property-no-vendor-prefix": true,

        // 在嵌套的规则中禁止有空行
        // "rule-nested-empty-line-before": "never",

        // 在非嵌套的规则之前要有空行
        // "rule-non-nested-empty-line-before": "always",

        // 在特性选择器的方括号内要求有空格或禁止有空白
        "selector-attribute-brackets-space-inside": "never",

        // 在特性选择器的操作符之后要求有一个空格
        // "selector-attribute-operator-space-after": "always",

        // 在特性选择器的操作符之前要求有一个空格
        // "selector-attribute-operator-space-before": "always",

        // 要求特性值使用引号(试用)
        "selector-attribute-quotes": "always",

        // 在关系选择符之后要求有一个空格
        "selector-combinator-space-after": "always",

        // 在关系选择符之前要求有一个空格
        "selector-combinator-space-before": "always",

        // 确保包含选择符只使用一个空格，而且保证没有 tab，换行符或多个空格
        "selector-descendant-combinator-no-non-space": true,

        // 要求在选择器列表的逗号之后有一个空格
        "selector-list-comma-space-after": "always-single-line",

        // 要求在选择器列表的逗号之前禁止有空白
        "selector-list-comma-space-before": "never",

        // 指定伪类选择器的大小写
        "selector-pseudo-class-case": "lower",

        // 禁止使用未知的伪类选择器
        "selector-pseudo-class-no-unknown": true,

        // 在伪类选择器的括号内要求禁止有空白(试用)
        "selector-pseudo-class-parentheses-space-inside": "never",

        // 指定伪元素的大小写
        "selector-pseudo-element-case": "lower",

        // 指定伪元素使用单冒号还是双冒号
        // https://developer.mozilla.org/zh-CN/docs/Learn/CSS/Building_blocks/Selectors/Pseudo-classes_and_pseudo-elements
        "selector-pseudo-element-colon-notation": "double",

        // 禁止使用未知的伪元素
        "selector-pseudo-element-no-unknown": true,

        // 指定类型选择器的大小写
        "selector-type-case": "lower",

        // 禁用未知的类型选择器
        "selector-type-no-unknown": true,

        // 指定字符串使用双引号
        "string-quotes": "double",

        // 指定单位的大小写
        "unit-case": "lower",

        // 禁止使用未知单位
        "unit-no-unknown": true
    }
}
