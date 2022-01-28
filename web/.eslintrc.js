/**
 * @file eslint config
 * @author
 */
module.exports = {
    // 无需向父目录查找eslint文件
    root: true,

    // 使用babel-eslint解析器
    parserOptions: {
        parser: 'babel-eslint',
        sourceType: 'module'
    },

    // 指定脚本的运行环境,每种环境都有一组特定的预定义全局变量
    env: {
        browser: true
    },

    // 数组形式，每个配置继承它前面的配置
    extends: [
        'plugin:vue/recommended',
        'standard'
    ],
    // 省略包名的前缀 eslint-plugin-
    // required to lint *.vue files
    plugins: [
        'vue'
    ],

    // 配置额外的全局变量
    globals: {
        // value 为 true 允许被重写，为 false 不允许被重写
        NODE_ENV: false
    },

    // 自定义规则
    rules: {
        // 使用单引号
        /* 示例
            // bad code
            let str = "hello world"

            // good code
            let str = 'hello world'
        */
        'quotes': ['error', 'single'],

        // 三等号
        /* 示例
            // bad code
            if (a == b) {}

            // good code
            if (a === b) {}
        */
        'eqeqeq': ['error', 'always'],

        // 禁止出现未使用过的变量
        'no-unused-vars': 'error',

        // 强制在关键字前后使用一致的空格
        /* 示例
            // bad code
            if (foo) {
                //...
            }else if (bar) {
                //...
            }else {
                //...
            }

            // good code
            if (foo) {
                //...
            } else if (bar) {
                //...
            } else {
                //...
            }
        */
        'keyword-spacing': [
            'error',
            {
                'overrides': {
                    'if': {
                        'after': true
                    },
                    'for': {
                        'after': true
                    },
                    'while': {
                        'after': true
                    },
                    'else': {
                        'after': true
                    }
                }
            }
        ],

        // https://eslint.org/docs/rules/camelcase
        'camelcase': ['error', {'properties': 'never'}],

        // 缩进使用 4 个空格，并且 switch 语句中的 Case 需要缩进
        // https://eslint.org/docs/rules/indent
        'indent': ['error', 4, {
            'SwitchCase': 1,
            'flatTernaryExpressions': true
        }],

        // 数组的括号内的前后禁止有空格
        // https://eslint.org/docs/rules/array-bracket-spacing
        /* 示例
            // bad code
            const foo = [ 'foo' ];
            const foo = [ 'foo'];
            const foo = ['foo' ];
            const foo = [ 1 ];

            // good code
            const foo = ['foo'];
            const foo = [1];
        */
        'array-bracket-spacing': ['error', 'never'],

        // 需要在操作符之前放置换行符
        // https://eslint.org/docs/rules/operator-linebreak
        // 'operator-linebreak': ['error', 'before'],

        // 在开发阶段打开调试 (区分stag prod)
        // https://eslint.org/docs/rules/no-debugger
        'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',

        // 只有一个参数时，箭头函数体可以省略圆括号
        // https://eslint.org/docs/rules/arrow-parens
        'arrow-parens': 'off',

        // 禁止空语句（可在空语句写注释避免），允许空的 catch 语句
        // https://eslint.org/docs/rules/no-empty
        /* 示例
            // bad code
            if (foo) {
            }

            while (foo) {
            }

            // good code
            if (foo) {
                // empty
            }
        */
        'no-empty': ['error', {'allowEmptyCatch': true}],

        // 禁止在语句末尾使用分号
        // https://eslint.org/docs/rules/semi
        /* 示例
            // bad code
            const obj = {};

            // good code
            const obj = {}
        */
        'semi': ['error', 'never'],

        // 函数圆括号之前没有空格（挺有争议的）
        // https://eslint.org/docs/rules/space-before-function-paren
        /* 示例
            // bad code
            function foo () {
                // ...
            }

            const bar = function () {
                // ...
            }

            // good code
            function foo() {
                // ...
            }

            const bar = function() {
                // ...
            }
        */
        'space-before-function-paren': ['error', {
            'anonymous': 'never', // 匿名函数表达式
            'named': 'never', // 命名的函数表达式
            'asyncArrow': 'never' // 异步的箭头函数表达式
        }],

        // 禁止行尾有空格
        // https://eslint.org/docs/rules/no-trailing-spaces
        'no-trailing-spaces': ['error'],


        // 注释的斜线或 * 后必须有空格
        // https://eslint.org/docs/rules/spaced-comment
        /* 示例
            // bad code
            //This is a comment with no whitespace at the beginning

            // good code
            // This is a comment with a whitespace at the beginning
        */
        'spaced-comment': ['error', 'always', {
            'line': {
                'markers': ['*package', '!', '/', ',', '=']
            },
            'block': {
                // 前后空格是否平衡
                'balanced': false,
                'markers': ['*package', '!', ',', ':', '::', 'flow-include'],
                'exceptions': ['*']
            }
        }],

        // https://eslint.org/docs/rules/no-template-curly-in-string
        // 禁止在字符串中使用字符串模板。不限制
        'no-template-curly-in-string': 'off',

        // https://eslint.org/docs/rules/no-useless-escape
        // 禁止出现没必要的转义。不限制
        'no-useless-escape': 'off',

        // https://eslint.org/docs/rules/no-var
        // 禁止使用 var
        'no-var': 'error',

        // https://eslint.org/docs/rules/prefer-const
        // 如果一个变量不会被重新赋值，必须使用 `const` 进行声明。
        /* 示例
            // bad code
            let a = 3
            console.log(a)

            // good code
            const a = 3
            console.log(a)
        */
        'prefer-const': 'error',

        // eslint-plugin-vue@7 新增的规则，暂时先全部关闭
        'vue/no-dupe-v-else-if': 'off',
        'vue/component-definition-name-casing': 'off',
        'vue/one-component-per-file': 'off',
        'vue/v-slot-style': 'off',
        'vue/no-arrow-functions-in-watch': 'off',
        'vue/no-custom-modifiers-on-v-model': 'off',
        'vue/no-multiple-template-root': 'off',
        'vue/no-mutating-props': 'off',
        'vue/no-v-for-template-key': 'off',
        'vue/no-v-model-argument': 'off',
        'vue/valid-v-bind-sync': 'off',
        'vue/valid-v-slot': 'off',
        'vue/experimental-script-setup-vars': 'off',
        'vue/no-lone-template': 'off',

        // 不允许数组括号内有空格
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/array-bracket-spacing.md
        /** 
         * 示例
         * bad code
         * var arr = [ 'foo', 'bar' ];
         * var arr = ['foo', 'bar' ];
         * var [ x, y ] = z;
         * 
         * good code
         * var arr = ['foo', 'bar', 'baz'];
         * var arr = [['foo'], 'bar', 'baz'];
         * var [x, y] = z;
         */
        'vue/array-bracket-spacing': ['error', 'never'],

        // 在箭头函数的箭头之前/之后需要空格
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/arrow-spacing.md
        /** 
         * 示例
         * bad code
         * ()=> {};
         * () =>{};
         * (a)=> {};
         * (a) =>{};
         * 
         * good code
         * () => {};
         * (a) => {};
         * a => a;
         * () => {'\n'};
         */
        'vue/arrow-spacing': ['error', {'before': true, 'after': true}],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/attribute-hyphenation.md
        // vue html 属性小写，连字符
        /** 
         * 示例
         * bad code
         * <MyComponent myProp="prop" />
         * 
         * good code
         * <MyComponent my-prop="prop" />
         */
        'vue/attribute-hyphenation': ['error', 'always'],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/attributes-order.md
        // 属性顺序，不限制
        'vue/attributes-order': 'off',
        
        // 在打开块之后和关闭块之前强制块内的空格
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/block-spacing.md
        /** 
         * 示例
         * bad code
         * function foo() {return true;}
         * if (foo) { bar = 0;}
         * (a) =>{};function baz() {let i = 0;
         * return i;
         * }
         * 
         * good code
         * function foo() { return true; }
         * if (foo) { bar = 0; }
         */
        'vue/block-spacing': ['error', 'always'],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/camelcase.md
        // 后端数据字段经常不是驼峰，所以不限制 properties，也不限制解构
        /** 
         * 示例
         * bad code
         * import { no_camelcased } from "external-module"
         * var my_favorite_color = "#112C85";
         * obj.do_something = function() {
         * // ...
         * };
         * 
         * good code
         * import { no_camelcased as camelCased } from "external-module";
         * var myFavoriteColor   = "#112C85";
         * var _myFavoriteColor  = "#112C85";
         * var myFavoriteColor_  = "#112C85";
         */
        'vue/camelcase': ['error', {'properties': 'never'}],
        
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/comma-dangle.md
        // 禁止使用拖尾逗号，如 {demo: 'test',}
        /** 
         * 示例
         * bad code
         * var foo = {
         * bar: "baz",
         * qux: "quux",
         * var arr = [1,2,];
         * };
         * 
         * good code
         * var foo = {
         * bar: "baz",
         * qux: "quux"
         * var arr = [1,2];
         */
        'vue/comma-dangle': ['error', 'never'],
        
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/comment-directive.md
        // vue 文件 template 中允许 eslint-disable eslint-enable eslint-disable-line eslint-disable-next-line
        // 行内注释启用/禁用某些规则，配置为 1 即允许
        /** 
         * 示例
         * bad code
         * <div a="1" />
         * 
         * good code
         * <div a="1" b="2" c="3" d="4" />
         */
        'vue/comment-directive': 'error',
        
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/component-name-in-template-casing.md
        // 组件 html 标签的形式，连字符形式，所有 html 标签均会检测，如引入第三方不可避免，可通过 ignores 配置，支持正则，不限制
        'vue/component-name-in-template-casing': 'off',
        
        // 需要 === 和 !==,不将此规则应用于null
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/eqeqeq.md
        /** 
         * 示例
         * bad code
         * if (x == 42) { }
         * if ("" == text) { }
         * if (obj.getStuff() != undefined) { }
         * var arr = [1,2,];
         * };
         * 
         * good code
         * a === b
         * foo === true
         * bananas !== 1
         * value === undefined
         */
        'vue/eqeqeq': ['error', 'always', {'null': 'ignore'}],
        
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-closing-bracket-newline.md
        // 单行写法不需要换行，多行需要，不限制
        'vue/html-closing-bracket-newline': 'off',

        // 自关闭标签需要空格
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-closing-bracket-spacing.md
        /* 示例
            <!-- bad code -->
            <div >
                <div foo="bar" ></div >
            <div/>
            <div foo/>
            <div foo="bar"/>

            <!-- ✓ GOOD -->
            <div>
                <div foo="bar"></div>
            <div />
            <div foo />
            <div foo="bar" />
        */
        'vue/html-closing-bracket-spacing': ['error', {
            'startTag': 'never',
            'endTag': 'never',
            'selfClosingTag': 'always'
        }],

        // 标签必须有结束标签
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-end-tags.md
        /* 示例
            <!-- bad code -->
            <div>
            <p> 

            <!-- good code -->
            <div></div>
            <p></p>
        */
        'vue/html-end-tags': 'error',

        // html的缩进.在多行情况下，属性不与第一个属性垂直对齐
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-indent.md
        /* 示例
            <!-- bad code -->
            <div id=""
                
                 some-attr=""
            />

            <!-- good code -->
            <div id=""
               
                some-attr=""
            />
        */
        'vue/html-indent': ['error', 4, {
            'attribute': 1,
            'baseIndent': 1,
            'closeBracket': 0,
            'alignAttributesVertically': false, // 在多行情况下，属性是否应与第一个属性垂直对齐
            'ignores': []
        }],

        // html属性引用采用双引号
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-quotes.md
        /* 示例
            <!-- bad code -->
            <img src='./logo.png' />

            <!-- good code -->
            <img src="./logo.png" />
        */
        'vue/html-quotes': ['error', 'double'],


        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-self-closing.md
        // html tag 是否自闭和，不限制
        'vue/html-self-closing': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/jsx-uses-vars.md
        // 当变量在 `JSX` 中被使用了，那么 eslint 就不会报出 `no-unused-vars` 的错误。需要开启 eslint no-unused-vars 规则才适用
        /*
            import HelloWorld from './HelloWorld';

            export default {
                render () {
                    return (
                        <HelloWorld msg="world"/>
                    )
                },
            }
            此时不会报 `no-unused-vars` 的错误，仅警告
        */
        'vue/jsx-uses-vars': 'warn',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/key-spacing.md
        // 属性定义，冒号前没有空格，后面有空格
        /* 示例
            // bad code
            const obj = { a:1 }

            // good code
            const obj = { a: 1 }
        */
        'vue/key-spacing': ['error', {'beforeColon': false, 'afterColon': true}],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/match-component-file-name.md
        // 组件名称属性与其文件名匹配，不限制
        'vue/match-component-file-name': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/max-attributes-per-line.md
        // 每行属性的最大个数，不限制
        'vue/max-attributes-per-line': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/multiline-html-element-content-newline.md
        // 在多行元素的内容前后需要换行符，不限制
        'vue/multiline-html-element-content-newline': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/mustache-interpolation-spacing.md
        // template 中 {{var}}，不限制
        'vue/mustache-interpolation-spacing': 'off',

        // name属性强制使用连字符形式
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/name-property-casing.md
        /* 示例
            // bad code 
            export default {
                name: 'MyComponent'
            }
        
            // good code
            export default {
                name: 'my-component'
            }
        */
        'vue/name-property-casing': ['error', 'kebab-case'],

        // 禁止在计算属性中执行异步操作
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-async-in-computed-properties.md
        /* 示例
            computed: {
                // bad code
                pro () {
                  return Promise.all([new Promise((resolve, reject) => {})])
                },
                foo1: async function () {
                  return await someFunc()
                },
                bar () {
                  return fetch(url).then(response => {})
                },
                tim () {
                  setTimeout(() => { }, 0)
                },
                inter () {
                  setInterval(() => { }, 0)
                },
                anim () {
                  requestAnimationFrame(() => {})
                },

                // good code
                foo () {
                  var bar = 0
                  try {
                    bar = bar / this.a
                  } catch (e) {
                    return 0
                  } finally {
                    return bar
                  }
                },
            }
        */
        'vue/no-async-in-computed-properties': 'error',

        // 禁止布尔默认值，不限制
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-boolean-default.md
        'vue/no-boolean-default': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-confusing-v-for-v-if.md
        'vue/no-confusing-v-for-v-if': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-dupe-keys.md
        // 属性名禁止重复
        /* 示例
            // bad code
            person: {
               age: '',
               age: ''
            }

            // good code
            person: {
               age: '',
               name: ''
            }
        */
        'vue/no-dupe-keys': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-duplicate-attributes.md
        // 禁止 html 元素中出现重复的属性
        /* 示例
            // bad code
            <div :a="" :a=""></div>

            // good code
            <div :a="" :b=""></div>
        */
        'vue/no-duplicate-attributes': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-multi-spaces.md
        // 删除 html 标签中连续多个不用于缩进的空格
        /* 示例
            // bad code
            <div    :a=""></div>

            // good code
            <div :a=""></div>
        */
        'vue/no-multi-spaces': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-parsing-error.md
        // 禁止语法错误
        /* 示例
            // bad code
            <div : / @click="def(">
                </span>
            </div id="ghi">

            // good code
            <div id="" @click="def()">
                <span></span>
            </div>
        */
        'vue/no-parsing-error': 'error',
        
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-reserved-keys.md
        // 禁止使用保留字，包括Vue
        /* 示例
            // bad code
            props: {
                $nextTick () {}
            }

            // good code
            props: {
                next () {}
            }
        */
        'vue/no-reserved-keys': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-restricted-syntax.md
        // 禁止使用特定的语法，不限制
        'vue/no-restricted-syntax': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-shared-component-data.md
        // data 属性必须是函数
        /* 示例
            // bad code
            data: {
            }

            // good code
            data() {
                return {}
            }
        */
        'vue/no-shared-component-data': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-side-effects-in-computed-properties.md
        // 禁止在计算属性对属性进行修改，不限制
        'vue/no-side-effects-in-computed-properties': 'off',

        // 不允许在属性中的等号周围有空格
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-spaces-around-equal-signs-in-attribute.md
        /* 示例
            // bad code
            <div class = "item"></div>
            
            // good code
            <div></div>
        */
        'vue/no-spaces-around-equal-signs-in-attribute': 'error',


        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-template-key.md
        // 禁止在 <template> 中使用 key 属性，不限制
        'vue/no-template-key': 'off',

        // 禁止再textarea中使用模板语言
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-textarea-mustache.md
        /* 示例
            // bad code
            <textarea>{{ message }}</textarea>

            // good code
            <textarea v-model="message" />
        */
        'vue/no-textarea-mustache': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-unused-components.md
        // 禁止 components 中声明的组件在 template 中没有使用
        /* 示例
            // bad code
            <template>
                <div>
                    <h2>Lorem ipsum</h2>
                </div>
            </template>

            <script>
                import TheButton from 'components/TheButton.vue'

                export default {
                    components: {
                        TheButton // Unused component
                    }
                }
            </script>

            // good code
            <template>
                <div>
                    <TheButton>CTA</TheButton>
                </div>
            </template>

            <script>
                import TheButton from 'components/TheButton.vue'

                export default {
                    components: {
                        TheButton
                    }
                }
            </script>
        */
        'vue/no-unused-components': 'error',

        // 禁止在v-for或作用域内使用未使用过的变量
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-unused-vars.md
        /* 示例
            <template>
                // bad code
                <ol v-for="i in 5">
                    <li>item</li>
                </ol>

                // good code
                <ol v-for="i in 5">
                    <li>{{ i }}</li>
                </ol>
            </template>
        */
        'vue/no-unused-vars': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-use-v-if-with-v-for.md
        // 禁止 v-for 和 v-if 在同一元素上使用，不限制
        'vue/no-use-v-if-with-v-for': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-v-html.md
        // 禁止使用 v-html，防止 xss，不限制
        'vue/no-v-html': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/object-curly-spacing.md
        // 对象写在一行时，大括号里需要空格
        /* 示例
            // bad code
            var obj = {'foo': 'bar'};

            // good code
            var obj = { 'foo': 'bar' };
        */
        'vue/object-curly-spacing': ['error', 'always'],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/order-in-components.md
        // 官方推荐顺序
        'vue/order-in-components': ['error', {
            'order': [
                'el',
                'name',
                'parent',
                'functional',
                ['delimiters', 'comments'],
                ['components', 'directives', 'filters'],
                'extends',
                'mixins',
                'inheritAttrs',
                'model',
                ['props', 'propsData'],
                'data',
                'computed',
                'watch',
                // LIFECYCLE_HOOKS: ['beforeCreate', 'created', 'beforeMount', 'mounted', 'beforeUpdate', 'updated', 'activated', 'deactivated', 'beforeDestroy', 'destroyed']
                'LIFECYCLE_HOOKS',
                'methods',
                ['template', 'render'],
                'renderError'
            ]
        }],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/prop-name-casing.md
        // 组件 props 属性名驼峰命名
        /* 示例
            <script>
                export default {
                    props: {
                        // bad code 
                        'greeting-text': String,
                        greeting_text: String

                        // good code
                        greetingText: String,
                    }
                }
            </script>
        */
        'vue/prop-name-casing': ['error', 'camelCase'],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-component-is.md
        // <component> 元素必须要有 :is 属性
        /* 示例
            <template>
                // bad code
                <component/>
                <component is="type"/>

                // good code
                <component :is="type"/>
                <component v-bind:is="type"/>
            </template>
        */
        'vue/require-component-is': 'error',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-default-prop.md
        // props 必须要有默认值，不限制
        'vue/require-default-prop': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-direct-export.md
        // 组件必须要直接被 export。不限制
        'vue/require-direct-export': 'off',

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-prop-type-constructor.md
        // props 的 type 必须为构造函数，不能为字符串
        /* 示例
            <script>
                export default {
                    props: {
                        // bad code
                        myProp: "Number",
                        anotherProp: ["Number", "String"],
                        myFieldWithBadType: {
                            type: "Object",
                            default: function() {
                                return {}
                            },
                        },
                        myOtherFieldWithBadType: {
                            type: "Number",
                            default: 1,
                        },

                        // good code
                        myProp: Number,
                        anotherProp: [Number, String],
                        myFieldWithBadType: {
                            type: Object,
                            default: function() {
                                return {}
                            },
                        },
                        myOtherFieldWithBadType: {
                            type: Number,
                            default: 1,
                        }
                    }
                }
            </script>
        */
        "vue/require-prop-type-constructor": "error",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-prop-types.md
        // props 必须要有 type。
        /* 示例
            // bad code
            Vue.component('bar', {
                props: ['foo']
            })
            
            Vue.component('baz', {
                props: {
                foo: {},
                }
            })
            
            // good code
            Vue.component('foo', {
                props: {
                    // Without options, just type reference
                    foo: String,
                    // With options with type field
                    bar: {
                        type: String,
                        required: true,
                    },
                    // With options without type field but with validator field
                    baz: {
                        required: true,
                        validator: function (value) {
                        return (
                            value === null ||
                            Array.isArray(value) && value.length > 0
                        )
                        }
                    }
                }
            })
        */
        "vue/require-prop-types": "error",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-render-return.md
        // render 函数必须要有返回值
        /* 示例
            // bad code
            export default {
                render (h) {
                    if (foo) {
                        return h('div', 'hello')
                    }
                }
            }

            // good code
            export default {
                render (h) {
                    return h('div', 'hello')
                }
            }
        */
        "vue/require-render-return": "error",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-v-for-key.md
        // v-for 指令必须要有 key 属性
        /* 示例
            // bad code
            <div v-for="todo in todos"/>

            // good code
            <div
                v-for="todo in todos"
                :key="todo.id"
            />
        */
        "vue/require-v-for-key": "error",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-valid-default-prop.md
        // props 默认值必须有效。不限制
        "vue/require-valid-default-prop": "off",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/return-in-computed-property.md
        // 计算属性必须要有返回值
        /* 示例
            computed: {
                // bad code
                baz () {
                    if (this.baf) {
                        return this.baf
                    }
                },
                baf: function () {}

                // good code
                foo () {
                    if (this.bar) {
                        return this.baz
                    } else {
                        return this.baf
                    }
                },
                bar: function () {
                    return false
                },
            }
        */
        "vue/return-in-computed-property": "error",

        // script缩进
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/script-indent.md
        /* 示例
            // bad code
            let a = {
              foo: 1,
              bar: 2
            }

            // good code
            let a = {
                foo: 1,
                bar: 2
            }
        */
        "vue/script-indent": [
            "error",
            4,
            {
                baseIndent: 1,
                switchCase: 1,
            }
        ],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/singleline-html-element-content-newline.md
        // 单行 html 元素后面必须换行。不限制
        "vue/singleline-html-element-content-newline": "off",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/space-infix-ops.md
        // 二元操作符两边要有空格
        /* 示例
            // bad code
            a+b
            a?b:c

            // good code
            a + b
            a ? b : c
        */
        "vue/space-infix-ops": "error",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/space-unary-ops.md
        // new, delete, typeof, void, yield 等后面必须有空格，一元操作符 -, +, --, ++, !, !! 禁止有空格
        /* 示例
            // bad code
            typeof!foo
            void{foo:0}
            new[foo][0]
            delete(foo.bar)
            ++ foo


            // good code
            typeof !foo
            void {foo:0}
            foo--
        */
        "vue/space-unary-ops": ["error", { words: true, nonwords: false }],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/this-in-template.md
        // 不允许在 template 中使用 this
        /* 示例
            // bad code
            <a :href="this.url">
                {{ this.text }}
            </a>

            // good code
            <a :href="url">
                {{ text }}
            </a>
        */
        "vue/this-in-template": ["error", "never"],

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/use-v-on-exact.md
        // 强制使用精确修饰词。不限制
        "vue/use-v-on-exact": "off",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/v-bind-style.md
        // v-bind 指令的写法。不限制
        "vue/v-bind-style": "off",

        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/v-on-function-call.md
        // 强制或禁止在 v-on 指令中不带参数的方法调用后使用括号。不限制
        "vue/v-on-function-call": "off",

        // v-on 指令的写法，限制简写
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/v-on-style.md
        /* 示例
            // bad code
            <div v-on:click="foo"/>

            // good code
            <div @click="foo"/>
        */
        'vue/v-on-style': ['error', 'shorthand'],

        // 根节点必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-template-root.md
        /* 示例
            // bad code
            < template ></ template >

            // good code
            <template src="foo.html"><div></div></template>
        */
        'vue/valid-template-root': 'error',

        // v-bind 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-bind.md
        /* 示例
            // bad code
            <div v-bind/>
            <div :aaa/>

            // good code
            <div v-bind="foo"/>
            <div :aaa="foo"/>
        */
        'vue/valid-v-bind': 'error',

        // v-cloak 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-cloak.md
        /* 示例
            // bad code
            <div v-cloak:aaa/>
            <div v-cloak.bbb/>
            <div v-cloak="ccc"/>

            // good code
             <div v-cloak/>
        */
        'vue/valid-v-cloak': 'error',

        // v-else-if 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-else-if.md
        /* 示例
            // bad code
            <div v-else-if/>
            <div v-else-if:aaa="foo"/>
            <div v-else-if.bbb="foo"/>

            // good code
            <div v-if="foo"/>
            <div v-else-if="bar"/>
        */
        'vue/valid-v-else-if': 'error',

        // v-else 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-else.md
        /* 示例
            // bad code
            <div v-else="foo"/>
            <div v-else:aaa/>
            <div v-else.bbb/>

            // good code
            <div v-if="foo"/>
            <div v-else/>
        */
        'vue/valid-v-else': 'error',

        // valid-v-for 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-for.md
        /* 示例
            // bad code
            <div v-for/>
            <div v-for:aaa="todo in todos"/>
            <div v-for.bbb="todo in todos"/>
            <div
                v-for="todo in todos"
                is="MyComponent"
                />
                <MyComponent v-for="todo in todos"/>
                <MyComponent
                    v-for="todo in todos"
                    :key="foo"
                />

            // good code
            <div v-for="todo in todos"/>
            <MyComponent
                v-for="todo in todos"
                :key="todo.id"
            />
            <div
                v-for="todo in todos"
                :is="MyComponent"
                :key="todo.id"
            />
        */
        'vue/valid-v-for': 'error',

        // v-html 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-html.md
        /* 示例
            // bad code
            <div v-html/>
            <div v-html:aaa="foo"/>
            <div v-html.bbb="foo"/>

            // good code
            <div v-html="foo"/>
        */
        'vue/valid-v-html': 'error',

        // v-if 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-if.md
        /* 示例
            // bad code
            <div v-if/>
            <div v-if:aaa="foo"/>
            <div v-if.bbb="foo"/>
            <div
                v-if="foo"
                v-else
            />
            <div
                v-if="foo"
                v-else-if="bar"
            />

            // good code
            <div v-if="foo"/>
            <div v-else-if="bar"/>
            <div v-else/>
        */
        'vue/valid-v-if': 'error',

        // v-model 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-model.md
        /* 示例
            // bad code
            <input v-model>
            <input v-model:aaa="foo">
            <input v-model.bbb="foo">
            <input v-model="foo + bar">
            <input v-model="a?.b.c">
            <input v-model="(a?.b).c">
            <div v-model="foo"/>
            <div v-for="todo in todos">
                <input v-model="todo">
            </div>

            // good code
            <input v-model="foo">
            <input v-model.lazy="foo">
            <textarea v-model="foo"/>
            <MyComponent v-model="foo"/>
            <MyComponent v-model:propName="foo"/>
            <MyComponent v-model.modifier="foo"/>
            <MyComponent v-model:propName.modifier="foo"/>
            <div v-for="todo in todos">
                <input v-model="todo.name">
            </div>
        */
        'vue/valid-v-model': 'error',

        // v-on 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-on.md
        /* 示例
            // bad code
             <div v-on/>
             <div v-on:click/>
             <div v-on:click.aaa="foo"/>
             <div @click/>

            // good code
             <div @click="foo"/>
             <div @click.left="foo"/>
             <div @click.prevent/>
             <div @click.stop/>
        */
        'vue/valid-v-on': 'error',

        // v-once 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-once.md
        /* 示例
            // bad code
            <div v-once:aaa/>
            <div v-once.bbb/>
            <div v-once="ccc"/>

            // good code
            <div v-once/>
        */
        'vue/valid-v-once': 'error',

        // v-pre 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-pre.md
        /* 示例
            // bad code
            <div v-pre:aaa/>
            <div v-pre.bbb/>
            <div v-pre="ccc"/>

            // good code
            <div v-pre/>
        */
        'vue/valid-v-pre': 'error',

        // v-show 指令必须合法
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-show.md
        /* 示例
            // bad code
            <div v-show/>
            <div v-show:aaa="foo"/>
            <div v-show.bbb="foo"/>
            <template v-show="condition" />

            // good code
            <div v-show="foo"/>
        */
        'vue/valid-v-show': 'error',
    
        // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-text.md
        // v-text 指令必须合法
        /* 示例
            // bad code
            <div v-text/>
            <div v-text:aaa="foo"/>
            <div v-text.bbb="foo"/>

            // good code
            <div v-text="foo"/>
        */
        'vue/valid-v-text': 'error'
    },
    overrides: [
        {
            files: ['*.vue'],
            rules: {
                indent: 'off'
            }
        }
    ]
}
