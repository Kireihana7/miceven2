(function (exports) {
    'use strict';

    function filterOutModifiersFromData(dataList) {
        dataList = dataList.slice();
        const modifiers = [];
        let elm;
        while ((elm = dataList[0]) && typeof elm === "string") {
            modifiers.push(dataList.shift());
        }
        return { modifiers, data: dataList };
    }
<<<<<<< HEAD
    const config = {
        // whether or not blockdom should normalize DOM whenever a block is created.
        // Normalizing dom mean removing empty text nodes (or containing only spaces)
        shouldNormalizeDom: true,
        // this is the main event handler. Every event handler registered with blockdom
        // will go through this function, giving it the data registered in the block
        // and the event
        mainEventHandler: (data, ev, currentTarget) => {
            if (typeof data === "function") {
                data(ev);
            }
            else if (Array.isArray(data)) {
                data = filterOutModifiersFromData(data).data;
                data[0](data[1], ev);
=======

    /**
     * Owl Observer
     *
     * This code contains the logic that allows Owl to observe and react to state
     * changes.
     *
     * This is a Observer class that can observe any JS values.  The way it works
     * can be summarized thusly:
     * - primitive values are not observed at all
     * - Objects and arrays are observed by replacing them with a Proxy
     * - each object/array metadata are tracked in a weakmap, and keep a revision
     *   number
     *
     * Note that this code is loosely inspired by Vue.
     */
    //------------------------------------------------------------------------------
    // Observer
    //------------------------------------------------------------------------------
    class Observer {
        constructor() {
            this.rev = 1;
            this.allowMutations = true;
            this.weakMap = new WeakMap();
        }
        notifyCB() { }
        observe(value, parent) {
            if (value === null ||
                typeof value !== "object" ||
                value instanceof Date ||
                value instanceof Promise) {
                // fun fact: typeof null === 'object'
                return value;
            }
            let metadata = this.weakMap.get(value) || this._observe(value, parent);
            return metadata.proxy;
        }
        revNumber(value) {
            const metadata = this.weakMap.get(value);
            return metadata ? metadata.rev : 0;
        }
        _observe(value, parent) {
            var self = this;
            const proxy = new Proxy(value, {
                get(target, k) {
                    const targetValue = target[k];
                    return self.observe(targetValue, value);
                },
                set(target, key, newVal) {
                    const value = target[key];
                    if (newVal !== value) {
                        if (!self.allowMutations) {
                            throw new Error(`Observed state cannot be changed here! (key: "${key}", val: "${newVal}")`);
                        }
                        self._updateRevNumber(target);
                        target[key] = newVal;
                        self.notifyCB();
                    }
                    return true;
                },
                deleteProperty(target, key) {
                    if (key in target) {
                        delete target[key];
                        self._updateRevNumber(target);
                        self.notifyCB();
                    }
                    return true;
                },
            });
            const metadata = {
                value,
                proxy,
                rev: this.rev,
                parent,
            };
            this.weakMap.set(value, metadata);
            this.weakMap.set(metadata.proxy, metadata);
            return metadata;
        }
        _updateRevNumber(target) {
            this.rev++;
            let metadata = this.weakMap.get(target);
            let parent = target;
            do {
                metadata = this.weakMap.get(parent);
                metadata.rev++;
            } while ((parent = metadata.parent) && parent !== target);
        }
    }

    /**
     * Owl QWeb Expression Parser
     *
     * Owl needs in various contexts to be able to understand the structure of a
     * string representing a javascript expression.  The usual goal is to be able
     * to rewrite some variables.  For example, if a template has
     *
     *  ```xml
     *  <t t-if="computeSomething({val: state.val})">...</t>
     * ```
     *
     * this needs to be translated in something like this:
     *
     * ```js
     *   if (context["computeSomething"]({val: context["state"].val})) { ... }
     * ```
     *
     * This file contains the implementation of an extremely naive tokenizer/parser
     * and evaluator for javascript expressions.  The supported grammar is basically
     * only expressive enough to understand the shape of objects, of arrays, and
     * various operators.
     */
    //------------------------------------------------------------------------------
    // Misc types, constants and helpers
    //------------------------------------------------------------------------------
    const RESERVED_WORDS = "true,false,NaN,null,undefined,debugger,console,window,in,instanceof,new,function,return,this,eval,void,Math,RegExp,Array,Object,Date".split(",");
    const WORD_REPLACEMENT = Object.assign(Object.create(null), {
        and: "&&",
        or: "||",
        gt: ">",
        gte: ">=",
        lt: "<",
        lte: "<=",
    });
    const STATIC_TOKEN_MAP = Object.assign(Object.create(null), {
        "{": "LEFT_BRACE",
        "}": "RIGHT_BRACE",
        "[": "LEFT_BRACKET",
        "]": "RIGHT_BRACKET",
        ":": "COLON",
        ",": "COMMA",
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
    });
    // note that the space after typeof is relevant. It makes sure that the formatted
    // expression has a space after typeof
    const OPERATORS = "...,.,===,==,+,!==,!=,!,||,&&,>=,>,<=,<,?,-,*,/,%,typeof ,=>,=,;,in ".split(",");
    let tokenizeString = function (expr) {
        let s = expr[0];
        let start = s;
        if (s !== "'" && s !== '"' && s !== "`") {
            return false;
        }
        let i = 1;
        let cur;
        while (expr[i] && expr[i] !== start) {
            cur = expr[i];
            s += cur;
            if (cur === "\\") {
                i++;
                cur = expr[i];
                if (!cur) {
                    throw new Error("Invalid expression");
                }
                s += cur;
            }
            i++;
        }
        if (expr[i] !== start) {
            throw new Error("Invalid expression");
        }
        s += start;
        if (start === "`") {
            return {
                type: "TEMPLATE_STRING",
                value: s,
                replace(replacer) {
                    return s.replace(/\$\{(.*?)\}/g, (match, group) => {
                        return "${" + replacer(group) + "}";
                    });
                },
            };
        }
        return { type: "VALUE", value: s };
    };
    let tokenizeNumber = function (expr) {
        let s = expr[0];
        if (s && s.match(/[0-9]/)) {
            let i = 1;
            while (expr[i] && expr[i].match(/[0-9]|\./)) {
                s += expr[i];
                i++;
            }
            return { type: "VALUE", value: s };
        }
        else {
            return false;
        }
    };
    let tokenizeSymbol = function (expr) {
        let s = expr[0];
        if (s && s.match(/[a-zA-Z_\$]/)) {
            let i = 1;
            while (expr[i] && expr[i].match(/\w/)) {
                s += expr[i];
                i++;
            }
            if (s in WORD_REPLACEMENT) {
                return { type: "OPERATOR", value: WORD_REPLACEMENT[s], size: s.length };
            }
            return { type: "SYMBOL", value: s };
        }
        else {
            return false;
        }
    };
    const tokenizeStatic = function (expr) {
        const char = expr[0];
        if (char && char in STATIC_TOKEN_MAP) {
            return { type: STATIC_TOKEN_MAP[char], value: char };
        }
        return false;
    };
    const tokenizeOperator = function (expr) {
        for (let op of OPERATORS) {
            if (expr.startsWith(op)) {
                return { type: "OPERATOR", value: op };
            }
        }
        return false;
    };
    const TOKENIZERS = [
        tokenizeString,
        tokenizeNumber,
        tokenizeOperator,
        tokenizeSymbol,
        tokenizeStatic,
    ];
    /**
     * Convert a javascript expression (as a string) into a list of tokens. For
     * example: `tokenize("1 + b")` will return:
     * ```js
     *  [
     *   {type: "VALUE", value: "1"},
     *   {type: "OPERATOR", value: "+"},
     *   {type: "SYMBOL", value: "b"}
     * ]
     * ```
     */
    function tokenize(expr) {
        const result = [];
        let token = true;
        while (token) {
            expr = expr.trim();
            if (expr) {
                for (let tokenizer of TOKENIZERS) {
                    token = tokenizer(expr);
                    if (token) {
                        result.push(token);
                        expr = expr.slice(token.size || token.value.length);
                        break;
                    }
                }
            }
            else {
                token = false;
            }
        }
        if (expr.length) {
            throw new Error(`Tokenizer error: could not tokenize "${expr}"`);
        }
        return result;
    }
    //------------------------------------------------------------------------------
    // Expression "evaluator"
    //------------------------------------------------------------------------------
    const isLeftSeparator = (token) => token && (token.type === "LEFT_BRACE" || token.type === "COMMA");
    const isRightSeparator = (token) => token && (token.type === "RIGHT_BRACE" || token.type === "COMMA");
    /**
     * This is the main function exported by this file. This is the code that will
     * process an expression (given as a string) and returns another expression with
     * proper lookups in the context.
     *
     * Usually, this kind of code would be very simple to do if we had an AST (so,
     * if we had a javascript parser), since then, we would only need to find the
     * variables and replace them.  However, a parser is more complicated, and there
     * are no standard builtin parser API.
     *
     * Since this method is applied to simple javasript expressions, and the work to
     * be done is actually quite simple, we actually can get away with not using a
     * parser, which helps with the code size.
     *
     * Here is the heuristic used by this method to determine if a token is a
     * variable:
     * - by default, all symbols are considered a variable
     * - unless the previous token is a dot (in that case, this is a property: `a.b`)
     * - or if the previous token is a left brace or a comma, and the next token is
     *   a colon (in that case, this is an object key: `{a: b}`)
     *
     * Some specific code is also required to support arrow functions. If we detect
     * the arrow operator, then we add the current (or some previous tokens) token to
     * the list of variables so it does not get replaced by a lookup in the context
     */
    function compileExprToArray(expr, scope) {
        const localVars = new Set();
        scope = Object.create(scope);
        const tokens = tokenize(expr);
        let i = 0;
        let stack = []; // to track last opening [ or {
        while (i < tokens.length) {
            let token = tokens[i];
            let prevToken = tokens[i - 1];
            let nextToken = tokens[i + 1];
            let groupType = stack[stack.length - 1];
            switch (token.type) {
                case "LEFT_BRACE":
                case "LEFT_BRACKET":
                    stack.push(token.type);
                    break;
                case "RIGHT_BRACE":
                case "RIGHT_BRACKET":
                    stack.pop();
            }
            let isVar = token.type === "SYMBOL" && !RESERVED_WORDS.includes(token.value);
            if (token.type === "SYMBOL" && !RESERVED_WORDS.includes(token.value)) {
                if (prevToken) {
                    // normalize missing tokens: {a} should be equivalent to {a:a}
                    if (groupType === "LEFT_BRACE" &&
                        isLeftSeparator(prevToken) &&
                        isRightSeparator(nextToken)) {
                        tokens.splice(i + 1, 0, { type: "COLON", value: ":" }, Object.assign({}, token));
                        nextToken = tokens[i + 1];
                    }
                    if (prevToken.type === "OPERATOR" && prevToken.value === ".") {
                        isVar = false;
                    }
                    else if (prevToken.type === "LEFT_BRACE" || prevToken.type === "COMMA") {
                        if (nextToken && nextToken.type === "COLON") {
                            isVar = false;
                        }
                    }
                }
            }
            if (token.type === "TEMPLATE_STRING") {
                token.value = token.replace((expr) => compileExpr(expr, scope));
            }
            if (nextToken && nextToken.type === "OPERATOR" && nextToken.value === "=>") {
                if (token.type === "RIGHT_PAREN") {
                    let j = i - 1;
                    while (j > 0 && tokens[j].type !== "LEFT_PAREN") {
                        if (tokens[j].type === "SYMBOL" && tokens[j].originalValue) {
                            tokens[j].value = tokens[j].originalValue;
                            scope[tokens[j].value] = { id: tokens[j].value, expr: tokens[j].value };
                            localVars.add(tokens[j].value);
                        }
                        j--;
                    }
                }
                else {
                    scope[token.value] = { id: token.value, expr: token.value };
                    localVars.add(token.value);
                }
            }
            if (isVar) {
                token.varName = token.value;
                if (token.value in scope && "id" in scope[token.value]) {
                    token.value = scope[token.value].expr;
                }
                else {
                    token.originalValue = token.value;
                    token.value = `scope['${token.value}']`;
                }
            }
            i++;
        }
        // Mark all variables that have been used locally.
        // This assumes the expression has only one scope (incorrect but "good enough for now")
        for (const token of tokens) {
            if (token.type === "SYMBOL" && localVars.has(token.value)) {
                token.isLocal = true;
            }
        }
        return tokens;
    }
    function compileExpr(expr, scope) {
        return compileExprToArray(expr, scope)
            .map((t) => t.value)
            .join("");
    }

    const INTERP_REGEXP = /\{\{.*?\}\}/g;
    //------------------------------------------------------------------------------
    // Compilation Context
    //------------------------------------------------------------------------------
    class CompilationContext {
        constructor(name) {
            this.code = [];
            this.variables = {};
            this.escaping = false;
            this.parentNode = null;
            this.parentTextNode = null;
            this.rootNode = null;
            this.indentLevel = 0;
            this.shouldDefineParent = false;
            this.shouldDefineScope = false;
            this.protectedScopeNumber = 0;
            this.shouldDefineQWeb = false;
            this.shouldDefineUtils = false;
            this.shouldDefineRefs = false;
            this.shouldDefineResult = true;
            this.loopNumber = 0;
            this.inPreTag = false;
            this.allowMultipleRoots = false;
            this.hasParentWidget = false;
            this.hasKey0 = false;
            this.keyStack = [];
            this.rootContext = this;
            this.templateName = name || "noname";
            this.addLine("let h = this.h;");
        }
        generateID() {
            return CompilationContext.nextID++;
        }
        /**
         * This method generates a "template key", which is basically a unique key
         * which depends on the currently set keys, and on the iteration numbers (if
         * we are in a loop).
         *
         * Such a key is necessary when we need to associate an id to some element
         * generated by a template (for example, a component)
         */
        generateTemplateKey(prefix = "") {
            const id = this.generateID();
            if (this.loopNumber === 0 && !this.hasKey0) {
                return `'${prefix}__${id}__'`;
            }
            let key = `\`${prefix}__${id}__`;
            let start = this.hasKey0 ? 0 : 1;
            for (let i = start; i < this.loopNumber + 1; i++) {
                key += `\${key${i}}__`;
            }
            this.addLine(`let k${id} = ${key}\`;`);
            return `k${id}`;
        }
        generateCode() {
            if (this.shouldDefineResult) {
                this.code.unshift("    let result;");
            }
            if (this.shouldDefineScope) {
                this.code.unshift("    let scope = Object.create(context);");
            }
            if (this.shouldDefineRefs) {
                this.code.unshift("    context.__owl__.refs = context.__owl__.refs || {};");
            }
            if (this.shouldDefineParent) {
                if (this.hasParentWidget) {
                    this.code.unshift("    let parent = extra.parent;");
                }
                else {
                    this.code.unshift("    let parent = context;");
                }
            }
            if (this.shouldDefineQWeb) {
                this.code.unshift("    let QWeb = this.constructor;");
            }
            if (this.shouldDefineUtils) {
                this.code.unshift("    let utils = this.constructor.utils;");
            }
            return this.code;
        }
        withParent(node) {
            if (!this.allowMultipleRoots &&
                this === this.rootContext &&
                (this.parentNode || this.parentTextNode)) {
                throw new Error("A template should not have more than one root node");
            }
            if (!this.rootContext.rootNode) {
                this.rootContext.rootNode = node;
            }
            if (!this.parentNode && this.rootContext.shouldDefineResult) {
                this.addLine(`result = vn${node};`);
            }
            return this.subContext("parentNode", node);
        }
        subContext(key, value) {
            const newContext = Object.create(this);
            newContext[key] = value;
            return newContext;
        }
        indent() {
            this.rootContext.indentLevel++;
        }
        dedent() {
            this.rootContext.indentLevel--;
        }
        addLine(line) {
            const prefix = new Array(this.indentLevel + 2).join("    ");
            this.code.push(prefix + line);
            return this.code.length - 1;
        }
        addIf(condition) {
            this.addLine(`if (${condition}) {`);
            this.indent();
        }
        addElse() {
            this.dedent();
            this.addLine("} else {");
            this.indent();
        }
        closeIf() {
            this.dedent();
            this.addLine("}");
        }
        getValue(val) {
            return val in this.variables ? this.getValue(this.variables[val]) : val;
        }
        /**
         * Prepare an expression for being consumed at render time.  Its main job
         * is to
         * - replace unknown variables by a lookup in the context
         * - replace already defined variables by their internal name
         */
        formatExpression(expr) {
            this.rootContext.shouldDefineScope = true;
            return compileExpr(expr, this.variables);
        }
        captureExpression(expr) {
            this.rootContext.shouldDefineScope = true;
            const argId = this.generateID();
            const tokens = compileExprToArray(expr, this.variables);
            const done = new Set();
            return tokens
                .map((tok, i) => {
                // "this" in captured expressions should be the current component
                if (tok.value === "this") {
                    if (!done.has("this")) {
                        done.add("this");
                        this.addLine(`const this_${argId} = utils.getComponent(context);`);
                    }
                    tok.value = `this_${argId}`;
                }
                // Variables that should be looked up in the scope. isLocal is for arrow
                // function arguments that should stay untouched (eg "ev => ev" should
                // not become "const ev_1 = scope['ev']; ev_1 => ev_1")
                if (tok.varName &&
                    !tok.isLocal &&
                    // HACK: for backwards compatibility, we don't capture bare methods
                    // this allows them to be called with the rendering context/scope
                    // as their this value.
                    (!tokens[i + 1] || tokens[i + 1].type !== "LEFT_PAREN")) {
                    if (!done.has(tok.varName)) {
                        done.add(tok.varName);
                        this.addLine(`const ${tok.varName}_${argId} = ${tok.value};`);
                    }
                    tok.value = `${tok.varName}_${argId}`;
                }
                return tok.value;
            })
                .join("");
        }
        /**
         * Perform string interpolation on the given string. Note that if the whole
         * string is an expression, it simply returns it (formatted and enclosed in
         * parentheses).
         * For instance:
         *   'Hello {{x}}!' -> `Hello ${x}`
         *   '{{x ? 'a': 'b'}}' -> (x ? 'a' : 'b')
         */
        interpolate(s) {
            let matches = s.match(INTERP_REGEXP);
            if (matches && matches[0].length === s.length) {
                return `(${this.formatExpression(s.slice(2, -2))})`;
            }
            let r = s.replace(/\{\{.*?\}\}/g, (s) => "${" + this.formatExpression(s.slice(2, -2)) + "}");
            return "`" + r + "`";
        }
        startProtectScope(codeBlock) {
            const protectID = this.generateID();
            this.rootContext.protectedScopeNumber++;
            this.rootContext.shouldDefineScope = true;
            const scopeExpr = `Object.create(scope);`;
            this.addLine(`let _origScope${protectID} = scope;`);
            this.addLine(`scope = ${scopeExpr}`);
            if (!codeBlock) {
                this.addLine(`scope.__access_mode__ = 'ro';`);
            }
            return protectID;
        }
        stopProtectScope(protectID) {
            this.rootContext.protectedScopeNumber--;
            this.addLine(`scope = _origScope${protectID};`);
        }
    }
    CompilationContext.nextID = 1;

    //------------------------------------------------------------------------------
    // module/props.ts
    //------------------------------------------------------------------------------
    function updateProps(oldVnode, vnode) {
        var key, cur, old, elm = vnode.elm, oldProps = oldVnode.data.props, props = vnode.data.props;
        if (!oldProps && !props)
            return;
        if (oldProps === props)
            return;
        oldProps = oldProps || {};
        props = props || {};
        for (key in oldProps) {
            if (!props[key]) {
                delete elm[key];
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
            return false;
        },
    };
<<<<<<< HEAD
=======
    //------------------------------------------------------------------------------
    // module/eventlisteners.ts
    //------------------------------------------------------------------------------
    function invokeHandler(handler, vnode, event) {
        if (typeof handler === "function") {
            // call function handler
            handler.call(vnode, event, vnode);
        }
        else if (typeof handler === "object") {
            // call handler with arguments
            if (typeof handler[0] === "function") {
                // special case for single argument for performance
                if (handler.length === 2) {
                    handler[0].call(vnode, handler[1], event, vnode);
                }
                else {
                    var args = handler.slice(1);
                    args.push(event);
                    args.push(vnode);
                    handler[0].apply(vnode, args);
                }
            }
            else {
                // call multiple handlers
                for (let i = 0, iLen = handler.length; i < iLen; i++) {
                    invokeHandler(handler[i], vnode, event);
                }
            }
        }
    }
    function handleEvent(event, vnode) {
        var name = event.type, on = vnode.data.on;
        // call event handler(s) if exists
        if (on) {
            if (on[name]) {
                invokeHandler(on[name], vnode, event);
            }
            else if (on["!" + name]) {
                invokeHandler(on["!" + name], vnode, event);
            }
        }
    }
    function createListener() {
        return function handler(event) {
            handleEvent(event, handler.vnode);
        };
    }
    function updateEventListeners(oldVnode, vnode) {
        var oldOn = oldVnode.data.on, oldListener = oldVnode.listener, oldElm = oldVnode.elm, on = vnode && vnode.data.on, elm = (vnode && vnode.elm), name;
        // optimization for reused immutable handlers
        if (oldOn === on) {
            return;
        }
        // remove existing listeners which no longer used
        if (oldOn && oldListener) {
            // if element changed or deleted we remove all existing listeners unconditionally
            if (!on) {
                for (name in oldOn) {
                    // remove listener if element was changed or existing listeners removed
                    const capture = name.charAt(0) === "!";
                    name = capture ? name.slice(1) : name;
                    oldElm.removeEventListener(name, oldListener, capture);
                }
            }
            else {
                for (name in oldOn) {
                    // remove listener if existing listener removed
                    if (!on[name]) {
                        const capture = name.charAt(0) === "!";
                        name = capture ? name.slice(1) : name;
                        oldElm.removeEventListener(name, oldListener, capture);
                    }
                }
            }
        }
        // add new listeners which has not already attached
        if (on) {
            // reuse existing listener or create new
            var listener = (vnode.listener = oldVnode.listener || createListener());
            // update vnode for listener
            listener.vnode = vnode;
            // if element changed or added we add all needed listeners unconditionally
            if (!oldOn) {
                for (name in on) {
                    // add listener if element was changed or new listeners added
                    const capture = name.charAt(0) === "!";
                    name = capture ? name.slice(1) : name;
                    elm.addEventListener(name, listener, capture);
                }
            }
            else {
                for (name in on) {
                    // add listener if new listener added
                    if (!oldOn[name]) {
                        const capture = name.charAt(0) === "!";
                        name = capture ? name.slice(1) : name;
                        elm.addEventListener(name, listener, capture);
                    }
                }
            }
        }
    }
    const eventListenersModule = {
        create: updateEventListeners,
        update: updateEventListeners,
        destroy: updateEventListeners,
    };
    //------------------------------------------------------------------------------
    // attributes.ts
    //------------------------------------------------------------------------------
    const xlinkNS = "http://www.w3.org/1999/xlink";
    const xmlNS = "http://www.w3.org/XML/1998/namespace";
    const colonChar = 58;
    const xChar = 120;
    function updateAttrs(oldVnode, vnode) {
        var key, elm = vnode.elm, oldAttrs = oldVnode.data.attrs, attrs = vnode.data.attrs;
        if (!oldAttrs && !attrs)
            return;
        if (oldAttrs === attrs)
            return;
        oldAttrs = oldAttrs || {};
        attrs = attrs || {};
        // update modified attributes, add new attributes
        for (key in attrs) {
            const cur = attrs[key];
            const old = oldAttrs[key];
            if (old !== cur) {
                if (cur === true) {
                    elm.setAttribute(key, "");
                }
                else if (cur === false) {
                    elm.removeAttribute(key);
                }
                else {
                    if (key.charCodeAt(0) !== xChar) {
                        elm.setAttribute(key, cur);
                    }
                    else if (key.charCodeAt(3) === colonChar) {
                        // Assume xml namespace
                        elm.setAttributeNS(xmlNS, key, cur);
                    }
                    else if (key.charCodeAt(5) === colonChar) {
                        // Assume xlink namespace
                        elm.setAttributeNS(xlinkNS, key, cur);
                    }
                    else {
                        elm.setAttribute(key, cur);
                    }
                }
            }
        }
        // remove removed attributes
        // use `in` operator since the previous `for` iteration uses it (.i.e. add even attributes with undefined value)
        // the other option is to remove all attributes with value == undefined
        for (key in oldAttrs) {
            if (!(key in attrs)) {
                elm.removeAttribute(key);
            }
        }
    }
    const attrsModule = {
        create: updateAttrs,
        update: updateAttrs,
    };
    //------------------------------------------------------------------------------
    // class.ts
    //------------------------------------------------------------------------------
    function updateClass(oldVnode, vnode) {
        var cur, name, elm, oldClass = oldVnode.data.class, klass = vnode.data.class;
        if (!oldClass && !klass)
            return;
        if (oldClass === klass)
            return;
        oldClass = oldClass || {};
        klass = klass || {};
        elm = vnode.elm;
        for (name in oldClass) {
            if (name && !klass[name] && !Object.prototype.hasOwnProperty.call(klass, name)) {
                // was `true` and now not provided
                elm.classList.remove(name);
            }
        }
        for (name in klass) {
            cur = klass[name];
            if (cur !== oldClass[name]) {
                elm.classList[cur ? "add" : "remove"](name);
            }
        }
    }
    const classModule = { create: updateClass, update: updateClass };
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    // -----------------------------------------------------------------------------
    // Toggler node
    // -----------------------------------------------------------------------------
    class VToggler {
        constructor(key, child) {
            this.key = key;
            this.child = child;
        }
<<<<<<< HEAD
        mount(parent, afterNode) {
            this.parentEl = parent;
            this.child.mount(parent, afterNode);
=======
        return map;
    }
    const hooks$1 = ["create", "update", "remove", "destroy", "pre", "post"];
    function init(modules, domApi) {
        let i, j, cbs = {};
        const api = domApi !== undefined ? domApi : htmlDomApi;
        for (i = 0; i < hooks$1.length; ++i) {
            cbs[hooks$1[i]] = [];
            for (j = 0; j < modules.length; ++j) {
                const hook = modules[j][hooks$1[i]];
                if (hook !== undefined) {
                    cbs[hooks$1[i]].push(hook);
                }
            }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        moveBeforeDOMNode(node, parent) {
            this.child.moveBeforeDOMNode(node, parent);
        }
        moveBeforeVNode(other, afterNode) {
            this.moveBeforeDOMNode((other && other.firstNode()) || afterNode);
        }
        patch(other, withBeforeRemove) {
            if (this === other) {
                return;
            }
            let child1 = this.child;
            let child2 = other.child;
            if (this.key === other.key) {
                child1.patch(child2, withBeforeRemove);
            }
            else {
                child2.mount(this.parentEl, child1.firstNode());
                if (withBeforeRemove) {
                    child1.beforeRemove();
                }
                child1.remove();
                this.child = child2;
                this.key = other.key;
            }
        }
        beforeRemove() {
            this.child.beforeRemove();
        }
        remove() {
            this.child.remove();
        }
        firstNode() {
            return this.child.firstNode();
        }
        toString() {
            return this.child.toString();
        }
    }
    function toggler(key, child) {
        return new VToggler(key, child);
    }

    // Custom error class that wraps error that happen in the owl lifecycle
    class OwlError extends Error {
    }

    const { setAttribute: elemSetAttribute, removeAttribute } = Element.prototype;
    const tokenList = DOMTokenList.prototype;
    const tokenListAdd = tokenList.add;
    const tokenListRemove = tokenList.remove;
    const isArray = Array.isArray;
    const { split, trim } = String.prototype;
    const wordRegexp = /\s+/;
    /**
     * We regroup here all code related to updating attributes in a very loose sense:
     * attributes, properties and classs are all managed by the functions in this
     * file.
     */
    function setAttribute(key, value) {
        switch (value) {
            case false:
            case undefined:
                removeAttribute.call(this, key);
                break;
            case true:
                elemSetAttribute.call(this, key, "");
                break;
            default:
                elemSetAttribute.call(this, key, value);
        }
    }
    function createAttrUpdater(attr) {
        return function (value) {
            setAttribute.call(this, attr, value);
        };
    }
    function attrsSetter(attrs) {
        if (isArray(attrs)) {
            if (attrs[0] === "class") {
                setClass.call(this, attrs[1]);
            }
            else {
                setAttribute.call(this, attrs[0], attrs[1]);
            }
        }
        else {
            for (let k in attrs) {
                if (k === "class") {
                    setClass.call(this, attrs[k]);
                }
                else {
                    setAttribute.call(this, k, attrs[k]);
                }
            }
        }
    }
    function attrsUpdater(attrs, oldAttrs) {
        if (isArray(attrs)) {
            const name = attrs[0];
            const val = attrs[1];
            if (name === oldAttrs[0]) {
                if (val === oldAttrs[1]) {
                    return;
                }
                if (name === "class") {
                    updateClass.call(this, val, oldAttrs[1]);
                }
                else {
                    setAttribute.call(this, name, val);
                }
            }
            else {
                removeAttribute.call(this, oldAttrs[0]);
                setAttribute.call(this, name, val);
            }
        }
        else {
            for (let k in oldAttrs) {
                if (!(k in attrs)) {
                    if (k === "class") {
                        updateClass.call(this, "", oldAttrs[k]);
                    }
                    else {
                        removeAttribute.call(this, k);
                    }
                }
            }
            for (let k in attrs) {
                const val = attrs[k];
                if (val !== oldAttrs[k]) {
                    if (k === "class") {
                        updateClass.call(this, val, oldAttrs[k]);
                    }
                    else {
                        setAttribute.call(this, k, val);
                    }
                }
            }
        }
    }
    function toClassObj(expr) {
        const result = {};
        switch (typeof expr) {
            case "string":
                // we transform here a list of classes into an object:
                //  'hey you' becomes {hey: true, you: true}
                const str = trim.call(expr);
                if (!str) {
                    return {};
                }
                let words = split.call(str, wordRegexp);
                for (let i = 0, l = words.length; i < l; i++) {
                    result[words[i]] = true;
                }
                return result;
            case "object":
                // this is already an object but we may need to split keys:
                // {'a': true, 'b c': true} should become {a: true, b: true, c: true}
                for (let key in expr) {
                    const value = expr[key];
                    if (value) {
                        key = trim.call(key);
                        if (!key) {
                            continue;
                        }
                        const words = split.call(key, wordRegexp);
                        for (let word of words) {
                            result[word] = value;
                        }
                    }
                }
                return result;
            case "undefined":
                return {};
            case "number":
                return { [expr]: true };
            default:
                return { [expr]: true };
        }
    }
    function setClass(val) {
        val = val === "" ? {} : toClassObj(val);
        // add classes
        const cl = this.classList;
        for (let c in val) {
            tokenListAdd.call(cl, c);
        }
    }
    function updateClass(val, oldVal) {
        oldVal = oldVal === "" ? {} : toClassObj(oldVal);
        val = val === "" ? {} : toClassObj(val);
        const cl = this.classList;
        // remove classes
        for (let c in oldVal) {
            if (!(c in val)) {
                tokenListRemove.call(cl, c);
            }
        }
        // add classes
        for (let c in val) {
            if (!(c in oldVal)) {
                tokenListAdd.call(cl, c);
            }
        }
    }

    /**
     * Creates a batched version of a callback so that all calls to it in the same
     * microtick will only call the original callback once.
     *
     * @param callback the callback to batch
     * @returns a batched version of the original callback
     */
    function batched(callback) {
        let scheduled = false;
        return async (...args) => {
            if (!scheduled) {
                scheduled = true;
                await Promise.resolve();
                scheduled = false;
                callback(...args);
            }
        };
    }
    /**
     * Determine whether the given element is contained in its ownerDocument:
     * either directly or with a shadow root in between.
     */
    function inOwnerDocument(el) {
        if (!el) {
            return false;
        }
        if (el.ownerDocument.contains(el)) {
            return true;
        }
        const rootNode = el.getRootNode();
        return rootNode instanceof ShadowRoot && el.ownerDocument.contains(rootNode.host);
    }
    function validateTarget(target) {
        // Get the document and HTMLElement corresponding to the target to allow mounting in iframes
        const document = target && target.ownerDocument;
        if (document) {
            const HTMLElement = document.defaultView.HTMLElement;
            if (target instanceof HTMLElement || target instanceof ShadowRoot) {
                if (!document.body.contains(target instanceof HTMLElement ? target : target.host)) {
                    throw new OwlError("Cannot mount a component on a detached dom node");
                }
                return;
            }
        }
        throw new OwlError("Cannot mount component: the target is not a valid DOM element");
    }
    class EventBus extends EventTarget {
        trigger(name, payload) {
            this.dispatchEvent(new CustomEvent(name, { detail: payload }));
        }
    }
    function whenReady(fn) {
        return new Promise(function (resolve) {
            if (document.readyState !== "loading") {
                resolve(true);
            }
            else {
                document.addEventListener("DOMContentLoaded", resolve, false);
            }
        }).then(fn || function () { });
    }
    async function loadFile(url) {
        const result = await fetch(url);
        if (!result.ok) {
            throw new OwlError("Error while fetching xml templates");
        }
        return await result.text();
    }
    /*
     * This class just transports the fact that a string is safe
     * to be injected as HTML. Overriding a JS primitive is quite painful though
     * so we need to redfine toString and valueOf.
     */
    class Markup extends String {
    }
    /*
     * Marks a value as safe, that is, a value that can be injected as HTML directly.
     * It should be used to wrap the value passed to a t-out directive to allow a raw rendering.
     */
    function markup(value) {
        return new Markup(value);
    }

    function createEventHandler(rawEvent) {
        const eventName = rawEvent.split(".")[0];
        const capture = rawEvent.includes(".capture");
        if (rawEvent.includes(".synthetic")) {
            return createSyntheticHandler(eventName, capture);
        }
        else {
            return createElementHandler(eventName, capture);
        }
    }
    // Native listener
    let nextNativeEventId = 1;
    function createElementHandler(evName, capture = false) {
        let eventKey = `__event__${evName}_${nextNativeEventId++}`;
        if (capture) {
            eventKey = `${eventKey}_capture`;
        }
        function listener(ev) {
            const currentTarget = ev.currentTarget;
            if (!currentTarget || !inOwnerDocument(currentTarget))
                return;
            const data = currentTarget[eventKey];
            if (!data)
                return;
            config.mainEventHandler(data, ev, currentTarget);
        }
        function setup(data) {
            this[eventKey] = data;
            this.addEventListener(evName, listener, { capture });
        }
        function remove() {
            delete this[eventKey];
            this.removeEventListener(evName, listener, { capture });
        }
        function update(data) {
            this[eventKey] = data;
        }
        return { setup, update, remove };
    }
    // Synthetic handler: a form of event delegation that allows placing only one
    // listener per event type.
    let nextSyntheticEventId = 1;
    function createSyntheticHandler(evName, capture = false) {
        let eventKey = `__event__synthetic_${evName}`;
        if (capture) {
            eventKey = `${eventKey}_capture`;
        }
        setupSyntheticEvent(evName, eventKey, capture);
        const currentId = nextSyntheticEventId++;
        function setup(data) {
            const _data = this[eventKey] || {};
            _data[currentId] = data;
            this[eventKey] = _data;
        }
        function remove() {
            delete this[eventKey];
        }
        return { setup, update: setup, remove };
    }
    function nativeToSyntheticEvent(eventKey, event) {
        let dom = event.target;
        while (dom !== null) {
            const _data = dom[eventKey];
            if (_data) {
                for (const data of Object.values(_data)) {
                    const stopped = config.mainEventHandler(data, event, dom);
                    if (stopped)
                        return;
                }
            }
            dom = dom.parentNode;
        }
    }
    const CONFIGURED_SYNTHETIC_EVENTS = {};
    function setupSyntheticEvent(evName, eventKey, capture = false) {
        if (CONFIGURED_SYNTHETIC_EVENTS[eventKey]) {
            return;
        }
        document.addEventListener(evName, (event) => nativeToSyntheticEvent(eventKey, event), {
            capture,
        });
        CONFIGURED_SYNTHETIC_EVENTS[eventKey] = true;
    }

    const getDescriptor$3 = (o, p) => Object.getOwnPropertyDescriptor(o, p);
    const nodeProto$4 = Node.prototype;
    const nodeInsertBefore$3 = nodeProto$4.insertBefore;
    const nodeSetTextContent$1 = getDescriptor$3(nodeProto$4, "textContent").set;
    const nodeRemoveChild$3 = nodeProto$4.removeChild;
    // -----------------------------------------------------------------------------
    // Multi NODE
    // -----------------------------------------------------------------------------
    class VMulti {
        constructor(children) {
            this.children = children;
        }
        mount(parent, afterNode) {
            const children = this.children;
            const l = children.length;
            const anchors = new Array(l);
            for (let i = 0; i < l; i++) {
                let child = children[i];
                if (child) {
                    child.mount(parent, afterNode);
                }
                else {
                    const childAnchor = document.createTextNode("");
                    anchors[i] = childAnchor;
                    nodeInsertBefore$3.call(parent, childAnchor, afterNode);
                }
            }
            this.anchors = anchors;
            this.parentEl = parent;
        }
        moveBeforeDOMNode(node, parent = this.parentEl) {
            this.parentEl = parent;
            const children = this.children;
            const anchors = this.anchors;
            for (let i = 0, l = children.length; i < l; i++) {
                let child = children[i];
                if (child) {
                    child.moveBeforeDOMNode(node, parent);
                }
                else {
                    const anchor = anchors[i];
                    nodeInsertBefore$3.call(parent, anchor, node);
                }
            }
        }
        moveBeforeVNode(other, afterNode) {
            if (other) {
                const next = other.children[0];
                afterNode = (next ? next.firstNode() : other.anchors[0]) || null;
            }
            const children = this.children;
            const parent = this.parentEl;
            const anchors = this.anchors;
            for (let i = 0, l = children.length; i < l; i++) {
                let child = children[i];
                if (child) {
                    child.moveBeforeVNode(null, afterNode);
                }
                else {
                    const anchor = anchors[i];
                    nodeInsertBefore$3.call(parent, anchor, afterNode);
                }
            }
        }
        patch(other, withBeforeRemove) {
            if (this === other) {
                return;
            }
            const children1 = this.children;
            const children2 = other.children;
            const anchors = this.anchors;
            const parentEl = this.parentEl;
            for (let i = 0, l = children1.length; i < l; i++) {
                const vn1 = children1[i];
                const vn2 = children2[i];
                if (vn1) {
                    if (vn2) {
                        vn1.patch(vn2, withBeforeRemove);
                    }
                    else {
                        const afterNode = vn1.firstNode();
                        const anchor = document.createTextNode("");
                        anchors[i] = anchor;
                        nodeInsertBefore$3.call(parentEl, anchor, afterNode);
                        if (withBeforeRemove) {
                            vn1.beforeRemove();
                        }
                        vn1.remove();
                        children1[i] = undefined;
                    }
                }
                else if (vn2) {
                    children1[i] = vn2;
                    const anchor = anchors[i];
                    vn2.mount(parentEl, anchor);
                    nodeRemoveChild$3.call(parentEl, anchor);
                }
            }
        }
        beforeRemove() {
            const children = this.children;
            for (let i = 0, l = children.length; i < l; i++) {
                const child = children[i];
                if (child) {
                    child.beforeRemove();
                }
            }
        }
        remove() {
            const parentEl = this.parentEl;
            if (this.isOnlyChild) {
                nodeSetTextContent$1.call(parentEl, "");
            }
            else {
                const children = this.children;
                const anchors = this.anchors;
                for (let i = 0, l = children.length; i < l; i++) {
                    const child = children[i];
                    if (child) {
                        child.remove();
                    }
                    else {
                        nodeRemoveChild$3.call(parentEl, anchors[i]);
                    }
                }
            }
        }
        firstNode() {
            const child = this.children[0];
            return child ? child.firstNode() : this.anchors[0];
        }
        toString() {
            return this.children.map((c) => (c ? c.toString() : "")).join("");
        }
    }
    function multi(children) {
        return new VMulti(children);
    }

    const getDescriptor$2 = (o, p) => Object.getOwnPropertyDescriptor(o, p);
    const nodeProto$3 = Node.prototype;
    const characterDataProto$1 = CharacterData.prototype;
    const nodeInsertBefore$2 = nodeProto$3.insertBefore;
    const characterDataSetData$1 = getDescriptor$2(characterDataProto$1, "data").set;
    const nodeRemoveChild$2 = nodeProto$3.removeChild;
    class VSimpleNode {
        constructor(text) {
            this.text = text;
        }
        mountNode(node, parent, afterNode) {
            this.parentEl = parent;
            nodeInsertBefore$2.call(parent, node, afterNode);
            this.el = node;
        }
        moveBeforeDOMNode(node, parent = this.parentEl) {
            this.parentEl = parent;
            nodeInsertBefore$2.call(parent, this.el, node);
        }
        moveBeforeVNode(other, afterNode) {
            nodeInsertBefore$2.call(this.parentEl, this.el, other ? other.el : afterNode);
        }
        beforeRemove() { }
        remove() {
            nodeRemoveChild$2.call(this.parentEl, this.el);
        }
        firstNode() {
            return this.el;
        }
        toString() {
            return this.text;
        }
    }
    class VText$1 extends VSimpleNode {
        mount(parent, afterNode) {
            this.mountNode(document.createTextNode(toText(this.text)), parent, afterNode);
        }
        patch(other) {
            const text2 = other.text;
            if (this.text !== text2) {
                characterDataSetData$1.call(this.el, toText(text2));
                this.text = text2;
            }
        }
    }
    class VComment extends VSimpleNode {
        mount(parent, afterNode) {
            this.mountNode(document.createComment(toText(this.text)), parent, afterNode);
        }
        patch() { }
    }
    function text(str) {
        return new VText$1(str);
    }
    function comment(str) {
        return new VComment(str);
    }
    function toText(value) {
        switch (typeof value) {
            case "string":
                return value;
            case "number":
                return String(value);
            case "boolean":
                return value ? "true" : "false";
            default:
                return value || "";
        }
    }

    const getDescriptor$1 = (o, p) => Object.getOwnPropertyDescriptor(o, p);
    const nodeProto$2 = Node.prototype;
    const elementProto = Element.prototype;
    const characterDataProto = CharacterData.prototype;
    const characterDataSetData = getDescriptor$1(characterDataProto, "data").set;
    const nodeGetFirstChild = getDescriptor$1(nodeProto$2, "firstChild").get;
    const nodeGetNextSibling = getDescriptor$1(nodeProto$2, "nextSibling").get;
    const NO_OP = () => { };
    function makePropSetter(name) {
        return function setProp(value) {
            // support 0, fallback to empty string for other falsy values
            this[name] = value === 0 ? 0 : value ? value.valueOf() : "";
        };
    }
    const cache$1 = {};
    /**
     * Compiling blocks is a multi-step process:
     *
     * 1. build an IntermediateTree from the HTML element. This intermediate tree
     *    is a binary tree structure that encode dynamic info sub nodes, and the
     *    path required to reach them
     * 2. process the tree to build a block context, which is an object that aggregate
     *    all dynamic info in a list, and also, all ref indexes.
     * 3. process the context to build appropriate builder/setter functions
     * 4. make a dynamic block class, which will efficiently collect references and
     *    create/update dynamic locations/children
     *
     * @param str
     * @returns a new block type, that can build concrete blocks
     */
    function createBlock(str) {
        if (str in cache$1) {
            return cache$1[str];
        }
        // step 0: prepare html base element
        const doc = new DOMParser().parseFromString(`<t>${str}</t>`, "text/xml");
        const node = doc.firstChild.firstChild;
        if (config.shouldNormalizeDom) {
            normalizeNode(node);
        }
        // step 1: prepare intermediate tree
        const tree = buildTree(node);
        // step 2: prepare block context
        const context = buildContext(tree);
        // step 3: build the final block class
        const template = tree.el;
        const Block = buildBlock(template, context);
        cache$1[str] = Block;
        return Block;
    }
    // -----------------------------------------------------------------------------
    // Helper
    // -----------------------------------------------------------------------------
    function normalizeNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            if (!/\S/.test(node.textContent)) {
                node.remove();
                return;
            }
        }
        if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.tagName === "pre") {
                return;
            }
        }
        for (let i = node.childNodes.length - 1; i >= 0; --i) {
            normalizeNode(node.childNodes.item(i));
        }
    }
    function buildTree(node, parent = null, domParentTree = null) {
        switch (node.nodeType) {
            case Node.ELEMENT_NODE: {
                // HTMLElement
                let currentNS = domParentTree && domParentTree.currentNS;
                const tagName = node.tagName;
                let el = undefined;
                const info = [];
                if (tagName.startsWith("block-text-")) {
                    const index = parseInt(tagName.slice(11), 10);
                    info.push({ type: "text", idx: index });
                    el = document.createTextNode("");
                }
                if (tagName.startsWith("block-child-")) {
                    if (!domParentTree.isRef) {
                        addRef(domParentTree);
                    }
                    const index = parseInt(tagName.slice(12), 10);
                    info.push({ type: "child", idx: index });
                    el = document.createTextNode("");
                }
                currentNS || (currentNS = node.namespaceURI);
                if (!el) {
                    el = currentNS
                        ? document.createElementNS(currentNS, tagName)
                        : document.createElement(tagName);
                }
                if (el instanceof Element) {
                    if (!domParentTree) {
                        // some html elements may have side effects when setting their attributes.
                        // For example, setting the src attribute of an <img/> will trigger a
                        // request to get the corresponding image. This is something that we
                        // don't want at compile time. We avoid that by putting the content of
                        // the block in a <template/> element
                        const fragment = document.createElement("template").content;
                        fragment.appendChild(el);
                    }
                    const attrs = node.attributes;
                    for (let i = 0; i < attrs.length; i++) {
                        const attrName = attrs[i].name;
                        const attrValue = attrs[i].value;
                        if (attrName.startsWith("block-handler-")) {
                            const idx = parseInt(attrName.slice(14), 10);
                            info.push({
                                type: "handler",
                                idx,
                                event: attrValue,
                            });
                        }
                        else if (attrName.startsWith("block-attribute-")) {
                            const idx = parseInt(attrName.slice(16), 10);
                            info.push({
                                type: "attribute",
                                idx,
                                name: attrValue,
                                tag: tagName,
                            });
                        }
                        else if (attrName.startsWith("block-property-")) {
                            const idx = parseInt(attrName.slice(15), 10);
                            info.push({
                                type: "property",
                                idx,
                                name: attrValue,
                                tag: tagName,
                            });
                        }
                        else if (attrName === "block-attributes") {
                            info.push({
                                type: "attributes",
                                idx: parseInt(attrValue, 10),
                            });
                        }
                        else if (attrName === "block-ref") {
                            info.push({
                                type: "ref",
                                idx: parseInt(attrValue, 10),
                            });
                        }
                        else {
                            el.setAttribute(attrs[i].name, attrValue);
                        }
                    }
                }
                const tree = {
                    parent,
                    firstChild: null,
                    nextSibling: null,
                    el,
                    info,
                    refN: 0,
                    currentNS,
                };
                if (node.firstChild) {
                    const childNode = node.childNodes[0];
                    if (node.childNodes.length === 1 &&
                        childNode.nodeType === Node.ELEMENT_NODE &&
                        childNode.tagName.startsWith("block-child-")) {
                        const tagName = childNode.tagName;
                        const index = parseInt(tagName.slice(12), 10);
                        info.push({ idx: index, type: "child", isOnlyChild: true });
                    }
                    else {
                        tree.firstChild = buildTree(node.firstChild, tree, tree);
                        el.appendChild(tree.firstChild.el);
                        let curNode = node.firstChild;
                        let curTree = tree.firstChild;
                        while ((curNode = curNode.nextSibling)) {
                            curTree.nextSibling = buildTree(curNode, curTree, tree);
                            el.appendChild(curTree.nextSibling.el);
                            curTree = curTree.nextSibling;
                        }
                    }
                }
                if (tree.info.length) {
                    addRef(tree);
                }
                return tree;
            }
            case Node.TEXT_NODE:
            case Node.COMMENT_NODE: {
                // text node or comment node
                const el = node.nodeType === Node.TEXT_NODE
                    ? document.createTextNode(node.textContent)
                    : document.createComment(node.textContent);
                return {
                    parent: parent,
                    firstChild: null,
                    nextSibling: null,
                    el,
                    info: [],
                    refN: 0,
                    currentNS: null,
                };
            }
        }
        throw new OwlError("boom");
    }
    function addRef(tree) {
        tree.isRef = true;
        do {
            tree.refN++;
        } while ((tree = tree.parent));
    }
    function parentTree(tree) {
        let parent = tree.parent;
        while (parent && parent.nextSibling === tree) {
            tree = parent;
            parent = parent.parent;
        }
        return parent;
    }
    function buildContext(tree, ctx, fromIdx) {
        if (!ctx) {
            const children = new Array(tree.info.filter((v) => v.type === "child").length);
            ctx = { collectors: [], locations: [], children, cbRefs: [], refN: tree.refN, refList: [] };
            fromIdx = 0;
        }
        if (tree.refN) {
            const initialIdx = fromIdx;
            const isRef = tree.isRef;
            const firstChild = tree.firstChild ? tree.firstChild.refN : 0;
            const nextSibling = tree.nextSibling ? tree.nextSibling.refN : 0;
            //node
            if (isRef) {
                for (let info of tree.info) {
                    info.refIdx = initialIdx;
                }
                tree.refIdx = initialIdx;
                updateCtx(ctx, tree);
                fromIdx++;
            }
            // right
            if (nextSibling) {
                const idx = fromIdx + firstChild;
                ctx.collectors.push({ idx, prevIdx: initialIdx, getVal: nodeGetNextSibling });
                buildContext(tree.nextSibling, ctx, idx);
            }
            // left
            if (firstChild) {
                ctx.collectors.push({ idx: fromIdx, prevIdx: initialIdx, getVal: nodeGetFirstChild });
                buildContext(tree.firstChild, ctx, fromIdx);
            }
        }
        return ctx;
    }
    function updateCtx(ctx, tree) {
        for (let info of tree.info) {
            switch (info.type) {
                case "text":
                    ctx.locations.push({
                        idx: info.idx,
                        refIdx: info.refIdx,
                        setData: setText,
                        updateData: setText,
                    });
                    break;
                case "child":
                    if (info.isOnlyChild) {
                        // tree is the parentnode here
                        ctx.children[info.idx] = {
                            parentRefIdx: info.refIdx,
                            isOnlyChild: true,
                        };
                    }
                    else {
                        // tree is the anchor text node
                        ctx.children[info.idx] = {
                            parentRefIdx: parentTree(tree).refIdx,
                            afterRefIdx: info.refIdx,
                        };
                    }
                    break;
                case "property": {
                    const refIdx = info.refIdx;
                    const setProp = makePropSetter(info.name);
                    ctx.locations.push({
                        idx: info.idx,
                        refIdx,
                        setData: setProp,
                        updateData: setProp,
                    });
                    break;
                }
                case "attribute": {
                    const refIdx = info.refIdx;
                    let updater;
                    let setter;
                    if (info.name === "class") {
                        setter = setClass;
                        updater = updateClass;
                    }
                    else {
                        setter = createAttrUpdater(info.name);
                        updater = setter;
                    }
                    ctx.locations.push({
                        idx: info.idx,
                        refIdx,
                        setData: setter,
                        updateData: updater,
                    });
                    break;
                }
                case "attributes":
                    ctx.locations.push({
                        idx: info.idx,
                        refIdx: info.refIdx,
                        setData: attrsSetter,
                        updateData: attrsUpdater,
                    });
                    break;
                case "handler": {
                    const { setup, update } = createEventHandler(info.event);
                    ctx.locations.push({
                        idx: info.idx,
                        refIdx: info.refIdx,
                        setData: setup,
                        updateData: update,
                    });
                    break;
                }
                case "ref":
                    const index = ctx.cbRefs.push(info.idx) - 1;
                    ctx.locations.push({
                        idx: info.idx,
                        refIdx: info.refIdx,
                        setData: makeRefSetter(index, ctx.refList),
                        updateData: NO_OP,
                    });
            }
        }
    }
    // -----------------------------------------------------------------------------
    // building the concrete block class
    // -----------------------------------------------------------------------------
    function buildBlock(template, ctx) {
        let B = createBlockClass(template, ctx);
        if (ctx.cbRefs.length) {
            const cbRefs = ctx.cbRefs;
            const refList = ctx.refList;
            let cbRefsNumber = cbRefs.length;
            B = class extends B {
                mount(parent, afterNode) {
                    refList.push(new Array(cbRefsNumber));
                    super.mount(parent, afterNode);
                    for (let cbRef of refList.pop()) {
                        cbRef();
                    }
                }
                remove() {
                    super.remove();
                    for (let cbRef of cbRefs) {
                        let fn = this.data[cbRef];
                        fn(null);
                    }
                }
            };
        }
        if (ctx.children.length) {
            B = class extends B {
                constructor(data, children) {
                    super(data);
                    this.children = children;
                }
            };
            B.prototype.beforeRemove = VMulti.prototype.beforeRemove;
            return (data, children = []) => new B(data, children);
        }
        return (data) => new B(data);
    }
    function createBlockClass(template, ctx) {
        const { refN, collectors, children } = ctx;
        const colN = collectors.length;
        ctx.locations.sort((a, b) => a.idx - b.idx);
        const locations = ctx.locations.map((loc) => ({
            refIdx: loc.refIdx,
            setData: loc.setData,
            updateData: loc.updateData,
        }));
        const locN = locations.length;
        const childN = children.length;
        const childrenLocs = children;
        const isDynamic = refN > 0;
        // these values are defined here to make them faster to lookup in the class
        // block scope
        const nodeCloneNode = nodeProto$2.cloneNode;
        const nodeInsertBefore = nodeProto$2.insertBefore;
        const elementRemove = elementProto.remove;
        class Block {
            constructor(data) {
                this.data = data;
            }
            beforeRemove() { }
            remove() {
                elementRemove.call(this.el);
            }
            firstNode() {
                return this.el;
            }
            moveBeforeDOMNode(node, parent = this.parentEl) {
                this.parentEl = parent;
                nodeInsertBefore.call(parent, this.el, node);
            }
            moveBeforeVNode(other, afterNode) {
                nodeInsertBefore.call(this.parentEl, this.el, other ? other.el : afterNode);
            }
            toString() {
                const div = document.createElement("div");
                this.mount(div, null);
                return div.innerHTML;
            }
            mount(parent, afterNode) {
                const el = nodeCloneNode.call(template, true);
                nodeInsertBefore.call(parent, el, afterNode);
                this.el = el;
                this.parentEl = parent;
            }
            patch(other, withBeforeRemove) { }
        }
        if (isDynamic) {
            Block.prototype.mount = function mount(parent, afterNode) {
                const el = nodeCloneNode.call(template, true);
                // collecting references
                const refs = new Array(refN);
                this.refs = refs;
                refs[0] = el;
                for (let i = 0; i < colN; i++) {
                    const w = collectors[i];
                    refs[w.idx] = w.getVal.call(refs[w.prevIdx]);
                }
                // applying data to all update points
                if (locN) {
                    const data = this.data;
                    for (let i = 0; i < locN; i++) {
                        const loc = locations[i];
                        loc.setData.call(refs[loc.refIdx], data[i]);
                    }
                }
                nodeInsertBefore.call(parent, el, afterNode);
                // preparing all children
                if (childN) {
                    const children = this.children;
                    for (let i = 0; i < childN; i++) {
                        const child = children[i];
                        if (child) {
                            const loc = childrenLocs[i];
                            const afterNode = loc.afterRefIdx ? refs[loc.afterRefIdx] : null;
                            child.isOnlyChild = loc.isOnlyChild;
                            child.mount(refs[loc.parentRefIdx], afterNode);
                        }
                    }
                }
                this.el = el;
                this.parentEl = parent;
            };
            Block.prototype.patch = function patch(other, withBeforeRemove) {
                if (this === other) {
                    return;
                }
                const refs = this.refs;
                // update texts/attributes/
                if (locN) {
                    const data1 = this.data;
                    const data2 = other.data;
                    for (let i = 0; i < locN; i++) {
                        const val1 = data1[i];
                        const val2 = data2[i];
                        if (val1 !== val2) {
                            const loc = locations[i];
                            loc.updateData.call(refs[loc.refIdx], val2, val1);
                        }
                    }
                    this.data = data2;
                }
                // update children
                if (childN) {
                    let children1 = this.children;
                    const children2 = other.children;
                    for (let i = 0; i < childN; i++) {
                        const child1 = children1[i];
                        const child2 = children2[i];
                        if (child1) {
                            if (child2) {
                                child1.patch(child2, withBeforeRemove);
                            }
                            else {
                                if (withBeforeRemove) {
                                    child1.beforeRemove();
                                }
                                child1.remove();
                                children1[i] = undefined;
                            }
                        }
                        else if (child2) {
                            const loc = childrenLocs[i];
                            const afterNode = loc.afterRefIdx ? refs[loc.afterRefIdx] : null;
                            child2.mount(refs[loc.parentRefIdx], afterNode);
                            children1[i] = child2;
                        }
                    }
                }
            };
        }
        return Block;
    }
    function setText(value) {
        characterDataSetData.call(this, toText(value));
    }
    function makeRefSetter(index, refs) {
        return function setRef(fn) {
            refs[refs.length - 1][index] = () => fn(this);
        };
    }

    const getDescriptor = (o, p) => Object.getOwnPropertyDescriptor(o, p);
    const nodeProto$1 = Node.prototype;
    const nodeInsertBefore$1 = nodeProto$1.insertBefore;
    const nodeAppendChild = nodeProto$1.appendChild;
    const nodeRemoveChild$1 = nodeProto$1.removeChild;
    const nodeSetTextContent = getDescriptor(nodeProto$1, "textContent").set;
    // -----------------------------------------------------------------------------
    // List Node
    // -----------------------------------------------------------------------------
    class VList {
        constructor(children) {
            this.children = children;
        }
        mount(parent, afterNode) {
            const children = this.children;
            const _anchor = document.createTextNode("");
            this.anchor = _anchor;
            nodeInsertBefore$1.call(parent, _anchor, afterNode);
            const l = children.length;
            if (l) {
                const mount = children[0].mount;
                for (let i = 0; i < l; i++) {
                    mount.call(children[i], parent, _anchor);
                }
            }
            this.parentEl = parent;
        }
        moveBeforeDOMNode(node, parent = this.parentEl) {
            this.parentEl = parent;
            const children = this.children;
            for (let i = 0, l = children.length; i < l; i++) {
                children[i].moveBeforeDOMNode(node, parent);
            }
            parent.insertBefore(this.anchor, node);
        }
        moveBeforeVNode(other, afterNode) {
            if (other) {
                const next = other.children[0];
                afterNode = (next ? next.firstNode() : other.anchor) || null;
            }
            const children = this.children;
            for (let i = 0, l = children.length; i < l; i++) {
                children[i].moveBeforeVNode(null, afterNode);
            }
            this.parentEl.insertBefore(this.anchor, afterNode);
        }
        patch(other, withBeforeRemove) {
            if (this === other) {
                return;
            }
            const ch1 = this.children;
            const ch2 = other.children;
            if (ch2.length === 0 && ch1.length === 0) {
                return;
            }
            this.children = ch2;
            const proto = ch2[0] || ch1[0];
            const { mount: cMount, patch: cPatch, remove: cRemove, beforeRemove, moveBeforeVNode: cMoveBefore, firstNode: cFirstNode, } = proto;
            const _anchor = this.anchor;
            const isOnlyChild = this.isOnlyChild;
            const parent = this.parentEl;
            // fast path: no new child => only remove
            if (ch2.length === 0 && isOnlyChild) {
                if (withBeforeRemove) {
                    for (let i = 0, l = ch1.length; i < l; i++) {
                        beforeRemove.call(ch1[i]);
                    }
                }
                nodeSetTextContent.call(parent, "");
                nodeAppendChild.call(parent, _anchor);
                return;
            }
            let startIdx1 = 0;
            let startIdx2 = 0;
            let startVn1 = ch1[0];
            let startVn2 = ch2[0];
            let endIdx1 = ch1.length - 1;
            let endIdx2 = ch2.length - 1;
            let endVn1 = ch1[endIdx1];
            let endVn2 = ch2[endIdx2];
            let mapping = undefined;
            while (startIdx1 <= endIdx1 && startIdx2 <= endIdx2) {
                // -------------------------------------------------------------------
                if (startVn1 === null) {
                    startVn1 = ch1[++startIdx1];
                    continue;
                }
                // -------------------------------------------------------------------
                if (endVn1 === null) {
                    endVn1 = ch1[--endIdx1];
                    continue;
                }
                // -------------------------------------------------------------------
                let startKey1 = startVn1.key;
                let startKey2 = startVn2.key;
                if (startKey1 === startKey2) {
                    cPatch.call(startVn1, startVn2, withBeforeRemove);
                    ch2[startIdx2] = startVn1;
                    startVn1 = ch1[++startIdx1];
                    startVn2 = ch2[++startIdx2];
                    continue;
                }
                // -------------------------------------------------------------------
                let endKey1 = endVn1.key;
                let endKey2 = endVn2.key;
                if (endKey1 === endKey2) {
                    cPatch.call(endVn1, endVn2, withBeforeRemove);
                    ch2[endIdx2] = endVn1;
                    endVn1 = ch1[--endIdx1];
                    endVn2 = ch2[--endIdx2];
                    continue;
                }
                // -------------------------------------------------------------------
                if (startKey1 === endKey2) {
                    // bnode moved right
                    cPatch.call(startVn1, endVn2, withBeforeRemove);
                    ch2[endIdx2] = startVn1;
                    const nextChild = ch2[endIdx2 + 1];
                    cMoveBefore.call(startVn1, nextChild, _anchor);
                    startVn1 = ch1[++startIdx1];
                    endVn2 = ch2[--endIdx2];
                    continue;
                }
                // -------------------------------------------------------------------
                if (endKey1 === startKey2) {
                    // bnode moved left
                    cPatch.call(endVn1, startVn2, withBeforeRemove);
                    ch2[startIdx2] = endVn1;
                    const nextChild = ch1[startIdx1];
                    cMoveBefore.call(endVn1, nextChild, _anchor);
                    endVn1 = ch1[--endIdx1];
                    startVn2 = ch2[++startIdx2];
                    continue;
                }
                // -------------------------------------------------------------------
                mapping = mapping || createMapping(ch1, startIdx1, endIdx1);
                let idxInOld = mapping[startKey2];
                if (idxInOld === undefined) {
                    cMount.call(startVn2, parent, cFirstNode.call(startVn1) || null);
                }
                else {
                    const elmToMove = ch1[idxInOld];
                    cMoveBefore.call(elmToMove, startVn1, null);
                    cPatch.call(elmToMove, startVn2, withBeforeRemove);
                    ch2[startIdx2] = elmToMove;
                    ch1[idxInOld] = null;
                }
                startVn2 = ch2[++startIdx2];
            }
            // ---------------------------------------------------------------------
            if (startIdx1 <= endIdx1 || startIdx2 <= endIdx2) {
                if (startIdx1 > endIdx1) {
                    const nextChild = ch2[endIdx2 + 1];
                    const anchor = nextChild ? cFirstNode.call(nextChild) || null : _anchor;
                    for (let i = startIdx2; i <= endIdx2; i++) {
                        cMount.call(ch2[i], parent, anchor);
                    }
                }
                else {
                    for (let i = startIdx1; i <= endIdx1; i++) {
                        let ch = ch1[i];
                        if (ch) {
                            if (withBeforeRemove) {
                                beforeRemove.call(ch);
                            }
                            cRemove.call(ch);
                        }
                    }
                }
            }
        }
        beforeRemove() {
            const children = this.children;
            const l = children.length;
            if (l) {
                const beforeRemove = children[0].beforeRemove;
                for (let i = 0; i < l; i++) {
                    beforeRemove.call(children[i]);
                }
            }
        }
        remove() {
            const { parentEl, anchor } = this;
            if (this.isOnlyChild) {
                nodeSetTextContent.call(parentEl, "");
            }
            else {
                const children = this.children;
                const l = children.length;
                if (l) {
                    const remove = children[0].remove;
                    for (let i = 0; i < l; i++) {
                        remove.call(children[i]);
                    }
                }
                nodeRemoveChild$1.call(parentEl, anchor);
            }
        }
        firstNode() {
            const child = this.children[0];
            return child ? child.firstNode() : undefined;
        }
        toString() {
            return this.children.map((c) => c.toString()).join("");
        }
    }
    function list(children) {
        return new VList(children);
    }
    function createMapping(ch1, startIdx1, endIdx2) {
        let mapping = {};
        for (let i = startIdx1; i <= endIdx2; i++) {
            mapping[ch1[i].key] = i;
        }
        return mapping;
    }

    const nodeProto = Node.prototype;
    const nodeInsertBefore = nodeProto.insertBefore;
    const nodeRemoveChild = nodeProto.removeChild;
    class VHtml {
        constructor(html) {
            this.content = [];
            this.html = html;
        }
        mount(parent, afterNode) {
            this.parentEl = parent;
            const template = document.createElement("template");
            template.innerHTML = this.html;
            this.content = [...template.content.childNodes];
            for (let elem of this.content) {
                nodeInsertBefore.call(parent, elem, afterNode);
            }
            if (!this.content.length) {
                const textNode = document.createTextNode("");
                this.content.push(textNode);
                nodeInsertBefore.call(parent, textNode, afterNode);
            }
        }
        moveBeforeDOMNode(node, parent = this.parentEl) {
            this.parentEl = parent;
            for (let elem of this.content) {
                nodeInsertBefore.call(parent, elem, node);
            }
        }
        moveBeforeVNode(other, afterNode) {
            const target = other ? other.content[0] : afterNode;
            this.moveBeforeDOMNode(target);
        }
        patch(other) {
            if (this === other) {
                return;
            }
            const html2 = other.html;
            if (this.html !== html2) {
                const parent = this.parentEl;
                // insert new html in front of current
                const afterNode = this.content[0];
                const template = document.createElement("template");
                template.innerHTML = html2;
                const content = [...template.content.childNodes];
                for (let elem of content) {
                    nodeInsertBefore.call(parent, elem, afterNode);
                }
                if (!content.length) {
                    const textNode = document.createTextNode("");
                    content.push(textNode);
                    nodeInsertBefore.call(parent, textNode, afterNode);
                }
                // remove current content
                this.remove();
                this.content = content;
                this.html = other.html;
            }
        }
        beforeRemove() { }
        remove() {
            const parent = this.parentEl;
            for (let elem of this.content) {
                nodeRemoveChild.call(parent, elem);
            }
        }
        firstNode() {
            return this.content[0];
        }
        toString() {
            return this.html;
        }
    }
    function html(str) {
        return new VHtml(str);
    }

    function createCatcher(eventsSpec) {
        const n = Object.keys(eventsSpec).length;
        class VCatcher {
            constructor(child, handlers) {
                this.handlerFns = [];
                this.afterNode = null;
                this.child = child;
                this.handlerData = handlers;
            }
            mount(parent, afterNode) {
                this.parentEl = parent;
                this.child.mount(parent, afterNode);
                this.afterNode = document.createTextNode("");
                parent.insertBefore(this.afterNode, afterNode);
                this.wrapHandlerData();
                for (let name in eventsSpec) {
                    const index = eventsSpec[name];
                    const handler = createEventHandler(name);
                    this.handlerFns[index] = handler;
                    handler.setup.call(parent, this.handlerData[index]);
                }
            }
            wrapHandlerData() {
                for (let i = 0; i < n; i++) {
                    let handler = this.handlerData[i];
                    // handler = [...mods, fn, comp], so we need to replace second to last elem
                    let idx = handler.length - 2;
                    let origFn = handler[idx];
                    const self = this;
                    handler[idx] = function (ev) {
                        const target = ev.target;
                        let currentNode = self.child.firstNode();
                        const afterNode = self.afterNode;
                        while (currentNode && currentNode !== afterNode) {
                            if (currentNode.contains(target)) {
                                return origFn.call(this, ev);
                            }
                            currentNode = currentNode.nextSibling;
                        }
                    };
                }
            }
            moveBeforeDOMNode(node, parent = this.parentEl) {
                this.parentEl = parent;
                this.child.moveBeforeDOMNode(node, parent);
                parent.insertBefore(this.afterNode, node);
            }
            moveBeforeVNode(other, afterNode) {
                if (other) {
                    // check this with @ged-odoo for use in foreach
                    afterNode = other.firstNode() || afterNode;
                }
                this.child.moveBeforeVNode(other ? other.child : null, afterNode);
                this.parentEl.insertBefore(this.afterNode, afterNode);
            }
            patch(other, withBeforeRemove) {
                if (this === other) {
                    return;
                }
                this.handlerData = other.handlerData;
                this.wrapHandlerData();
                for (let i = 0; i < n; i++) {
                    this.handlerFns[i].update.call(this.parentEl, this.handlerData[i]);
                }
                this.child.patch(other.child, withBeforeRemove);
            }
            beforeRemove() {
                this.child.beforeRemove();
            }
            remove() {
                for (let i = 0; i < n; i++) {
                    this.handlerFns[i].remove.call(this.parentEl);
                }
                this.child.remove();
                this.afterNode.remove();
            }
            firstNode() {
                return this.child.firstNode();
            }
            toString() {
                return this.child.toString();
            }
        }
        return function (child, handlers) {
            return new VCatcher(child, handlers);
        };
    }

    function mount$1(vnode, fixture, afterNode = null) {
        vnode.mount(fixture, afterNode);
    }
    function patch(vnode1, vnode2, withBeforeRemove = false) {
        vnode1.patch(vnode2, withBeforeRemove);
    }
    function remove(vnode, withBeforeRemove = false) {
        if (withBeforeRemove) {
            vnode.beforeRemove();
        }
        vnode.remove();
    }

    // Maps fibers to thrown errors
    const fibersInError = new WeakMap();
    const nodeErrorHandlers = new WeakMap();
    function _handleError(node, error) {
        if (!node) {
            return false;
        }
        const fiber = node.fiber;
        if (fiber) {
            fibersInError.set(fiber, error);
        }
        const errorHandlers = nodeErrorHandlers.get(node);
        if (errorHandlers) {
            let handled = false;
            // execute in the opposite order
            for (let i = errorHandlers.length - 1; i >= 0; i--) {
                try {
                    errorHandlers[i](error);
                    handled = true;
                    break;
                }
                catch (e) {
                    error = e;
                }
            }
            if (handled) {
                return true;
            }
        }
        return _handleError(node.parent, error);
    }
    function handleError(params) {
        let { error } = params;
        // Wrap error if it wasn't wrapped by wrapError (ie when not in dev mode)
        if (!(error instanceof OwlError)) {
            error = Object.assign(new OwlError(`An error occured in the owl lifecycle (see this Error's "cause" property)`), { cause: error });
        }
        const node = "node" in params ? params.node : params.fiber.node;
        const fiber = "fiber" in params ? params.fiber : node.fiber;
        if (fiber) {
            // resets the fibers on components if possible. This is important so that
            // new renderings can be properly included in the initial one, if any.
            let current = fiber;
            do {
                current.node.fiber = current;
                current = current.parent;
            } while (current);
            fibersInError.set(fiber.root, error);
        }
        const handled = _handleError(node, error);
        if (!handled) {
            console.warn(`[Owl] Unhandled error. Destroying the root component`);
            try {
                node.app.destroy();
            }
            catch (e) {
                console.error(e);
            }
            throw error;
        }
    }

    function makeChildFiber(node, parent) {
        let current = node.fiber;
        if (current) {
            cancelFibers(current.children);
            current.root = null;
        }
        return new Fiber(node, parent);
    }
    function makeRootFiber(node) {
        let current = node.fiber;
        if (current) {
            let root = current.root;
            // lock root fiber because canceling children fibers may destroy components,
            // which means any arbitrary code can be run in onWillDestroy, which may
            // trigger new renderings
            root.locked = true;
            root.setCounter(root.counter + 1 - cancelFibers(current.children));
            root.locked = false;
            current.children = [];
            current.childrenMap = {};
            current.bdom = null;
            if (fibersInError.has(current)) {
                fibersInError.delete(current);
                fibersInError.delete(root);
                current.appliedToDom = false;
            }
            return current;
        }
        const fiber = new RootFiber(node, null);
        if (node.willPatch.length) {
            fiber.willPatch.push(fiber);
        }
        if (node.patched.length) {
            fiber.patched.push(fiber);
        }
        return fiber;
    }
    function throwOnRender() {
        throw new OwlError("Attempted to render cancelled fiber");
    }
    /**
     * @returns number of not-yet rendered fibers cancelled
     */
    function cancelFibers(fibers) {
        let result = 0;
        for (let fiber of fibers) {
            let node = fiber.node;
            fiber.render = throwOnRender;
            if (node.status === 0 /* NEW */) {
                node.cancel();
            }
            node.fiber = null;
            if (fiber.bdom) {
                // if fiber has been rendered, this means that the component props have
                // been updated. however, this fiber will not be patched to the dom, so
                // it could happen that the next render compare the current props with
                // the same props, and skip the render completely. With the next line,
                // we kindly request the component code to force a render, so it works as
                // expected.
                node.forceNextRender = true;
            }
            else {
                result++;
            }
            result += cancelFibers(fiber.children);
        }
        return result;
    }
    class Fiber {
        constructor(node, parent) {
            this.bdom = null;
            this.children = [];
            this.appliedToDom = false;
            this.deep = false;
            this.childrenMap = {};
            this.node = node;
            this.parent = parent;
            if (parent) {
                this.deep = parent.deep;
                const root = parent.root;
                root.setCounter(root.counter + 1);
                this.root = root;
                parent.children.push(this);
            }
            else {
                this.root = this;
            }
        }
        render() {
            // if some parent has a fiber => register in followup
            let prev = this.root.node;
            let scheduler = prev.app.scheduler;
            let current = prev.parent;
            while (current) {
                if (current.fiber) {
                    let root = current.fiber.root;
                    if (root.counter === 0 && prev.parentKey in current.fiber.childrenMap) {
                        current = root.node;
                    }
                    else {
                        scheduler.delayedRenders.push(this);
                        return;
                    }
                }
                prev = current;
                current = current.parent;
            }
            // there are no current rendering from above => we can render
            this._render();
        }
        _render() {
            const node = this.node;
            const root = this.root;
            if (root) {
                try {
                    this.bdom = true;
                    this.bdom = node.renderFn();
                }
                catch (e) {
                    node.app.handleError({ node, error: e });
                }
                root.setCounter(root.counter - 1);
            }
        }
    }
    class RootFiber extends Fiber {
        constructor() {
            super(...arguments);
            this.counter = 1;
            // only add stuff in this if they have registered some hooks
            this.willPatch = [];
            this.patched = [];
            this.mounted = [];
            // A fiber is typically locked when it is completing and the patch has not, or is being applied.
            // i.e.: render triggered in onWillUnmount or in willPatch will be delayed
            this.locked = false;
        }
        complete() {
            const node = this.node;
            this.locked = true;
            let current = undefined;
            try {
                // Step 1: calling all willPatch lifecycle hooks
                for (current of this.willPatch) {
                    // because of the asynchronous nature of the rendering, some parts of the
                    // UI may have been rendered, then deleted in a followup rendering, and we
                    // do not want to call onWillPatch in that case.
                    let node = current.node;
                    if (node.fiber === current) {
                        const component = node.component;
                        for (let cb of node.willPatch) {
                            cb.call(component);
                        }
                    }
                }
                current = undefined;
                // Step 2: patching the dom
                node._patch();
                this.locked = false;
                // Step 4: calling all mounted lifecycle hooks
                let mountedFibers = this.mounted;
                while ((current = mountedFibers.pop())) {
                    current = current;
                    if (current.appliedToDom) {
                        for (let cb of current.node.mounted) {
                            cb();
                        }
                    }
                }
                // Step 5: calling all patched hooks
                let patchedFibers = this.patched;
                while ((current = patchedFibers.pop())) {
                    current = current;
                    if (current.appliedToDom) {
                        for (let cb of current.node.patched) {
                            cb();
                        }
                    }
                }
            }
            catch (e) {
                this.locked = false;
                node.app.handleError({ fiber: current || this, error: e });
            }
        }
        setCounter(newValue) {
            this.counter = newValue;
            if (newValue === 0) {
                this.node.app.scheduler.flush();
            }
        }
    }
    class MountFiber extends RootFiber {
        constructor(node, target, options = {}) {
            super(node, null);
            this.target = target;
            this.position = options.position || "last-child";
        }
        complete() {
            let current = this;
            try {
                const node = this.node;
                node.children = this.childrenMap;
                node.app.constructor.validateTarget(this.target);
                if (node.bdom) {
                    // this is a complicated situation: if we mount a fiber with an existing
                    // bdom, this means that this same fiber was already completed, mounted,
                    // but a crash occurred in some mounted hook. Then, it was handled and
                    // the new rendering is being applied.
                    node.updateDom();
                }
                else {
                    node.bdom = this.bdom;
                    if (this.position === "last-child" || this.target.childNodes.length === 0) {
                        mount$1(node.bdom, this.target);
                    }
                    else {
                        const firstChild = this.target.childNodes[0];
                        mount$1(node.bdom, this.target, firstChild);
                    }
                }
                // unregistering the fiber before mounted since it can do another render
                // and that the current rendering is obviously completed
                node.fiber = null;
                node.status = 1 /* MOUNTED */;
                this.appliedToDom = true;
                let mountedFibers = this.mounted;
                while ((current = mountedFibers.pop())) {
                    if (current.appliedToDom) {
                        for (let cb of current.node.mounted) {
                            cb();
                        }
                    }
                }
            }
            catch (e) {
                this.node.app.handleError({ fiber: current, error: e });
            }
        }
    }

    // Special key to subscribe to, to be notified of key creation/deletion
    const KEYCHANGES = Symbol("Key changes");
    // Used to specify the absence of a callback, can be used as WeakMap key but
    // should only be used as a sentinel value and never called.
    const NO_CALLBACK = () => {
        throw new Error("Called NO_CALLBACK. Owl is broken, please report this to the maintainers.");
    };
    const objectToString = Object.prototype.toString;
    const objectHasOwnProperty = Object.prototype.hasOwnProperty;
    const SUPPORTED_RAW_TYPES = new Set(["Object", "Array", "Set", "Map", "WeakMap"]);
    const COLLECTION_RAWTYPES = new Set(["Set", "Map", "WeakMap"]);
    /**
     * extract "RawType" from strings like "[object RawType]" => this lets us ignore
     * many native objects such as Promise (whose toString is [object Promise])
     * or Date ([object Date]), while also supporting collections without using
     * instanceof in a loop
     *
     * @param obj the object to check
     * @returns the raw type of the object
     */
    function rawType(obj) {
        return objectToString.call(toRaw(obj)).slice(8, -1);
    }
    /**
     * Checks whether a given value can be made into a reactive object.
     *
     * @param value the value to check
     * @returns whether the value can be made reactive
     */
    function canBeMadeReactive(value) {
        if (typeof value !== "object") {
            return false;
        }
        return SUPPORTED_RAW_TYPES.has(rawType(value));
    }
    /**
     * Creates a reactive from the given object/callback if possible and returns it,
     * returns the original object otherwise.
     *
     * @param value the value make reactive
     * @returns a reactive for the given object when possible, the original otherwise
     */
    function possiblyReactive(val, cb) {
        return canBeMadeReactive(val) ? reactive(val, cb) : val;
    }
    const skipped = new WeakSet();
    /**
     * Mark an object or array so that it is ignored by the reactivity system
     *
     * @param value the value to mark
     * @returns the object itself
     */
    function markRaw(value) {
        skipped.add(value);
        return value;
    }
    /**
     * Given a reactive objet, return the raw (non reactive) underlying object
     *
     * @param value a reactive value
     * @returns the underlying value
     */
    function toRaw(value) {
        return targets.has(value) ? targets.get(value) : value;
    }
    const targetToKeysToCallbacks = new WeakMap();
    /**
     * Observes a given key on a target with an callback. The callback will be
     * called when the given key changes on the target.
     *
     * @param target the target whose key should be observed
     * @param key the key to observe (or Symbol(KEYCHANGES) for key creation
     *  or deletion)
     * @param callback the function to call when the key changes
     */
    function observeTargetKey(target, key, callback) {
        if (callback === NO_CALLBACK) {
            return;
        }
        if (!targetToKeysToCallbacks.get(target)) {
            targetToKeysToCallbacks.set(target, new Map());
        }
        const keyToCallbacks = targetToKeysToCallbacks.get(target);
        if (!keyToCallbacks.get(key)) {
            keyToCallbacks.set(key, new Set());
        }
        keyToCallbacks.get(key).add(callback);
        if (!callbacksToTargets.has(callback)) {
            callbacksToTargets.set(callback, new Set());
        }
        callbacksToTargets.get(callback).add(target);
    }
    /**
     * Notify Reactives that are observing a given target that a key has changed on
     * the target.
     *
     * @param target target whose Reactives should be notified that the target was
     *  changed.
     * @param key the key that changed (or Symbol `KEYCHANGES` if a key was created
     *   or deleted)
     */
    function notifyReactives(target, key) {
        const keyToCallbacks = targetToKeysToCallbacks.get(target);
        if (!keyToCallbacks) {
            return;
        }
        const callbacks = keyToCallbacks.get(key);
        if (!callbacks) {
            return;
        }
        // Loop on copy because clearReactivesForCallback will modify the set in place
        for (const callback of [...callbacks]) {
            clearReactivesForCallback(callback);
            callback();
        }
    }
    const callbacksToTargets = new WeakMap();
    /**
     * Clears all subscriptions of the Reactives associated with a given callback.
     *
     * @param callback the callback for which the reactives need to be cleared
     */
    function clearReactivesForCallback(callback) {
        const targetsToClear = callbacksToTargets.get(callback);
        if (!targetsToClear) {
            return;
        }
        for (const target of targetsToClear) {
            const observedKeys = targetToKeysToCallbacks.get(target);
            if (!observedKeys) {
                continue;
            }
            for (const [key, callbacks] of observedKeys.entries()) {
                callbacks.delete(callback);
                if (!callbacks.size) {
                    observedKeys.delete(key);
                }
            }
        }
        targetsToClear.clear();
    }
    function getSubscriptions(callback) {
        const targets = callbacksToTargets.get(callback) || [];
        return [...targets].map((target) => {
            const keysToCallbacks = targetToKeysToCallbacks.get(target);
            let keys = [];
            if (keysToCallbacks) {
                for (const [key, cbs] of keysToCallbacks) {
                    if (cbs.has(callback)) {
                        keys.push(key);
                    }
                }
            }
            return { target, keys };
        });
    }
    // Maps reactive objects to the underlying target
    const targets = new WeakMap();
    const reactiveCache = new WeakMap();
    /**
     * Creates a reactive proxy for an object. Reading data on the reactive object
     * subscribes to changes to the data. Writing data on the object will cause the
     * notify callback to be called if there are suscriptions to that data. Nested
     * objects and arrays are automatically made reactive as well.
     *
     * Whenever you are notified of a change, all subscriptions are cleared, and if
     * you would like to be notified of any further changes, you should go read
     * the underlying data again. We assume that if you don't go read it again after
     * being notified, it means that you are no longer interested in that data.
     *
     * Subscriptions:
     * + Reading a property on an object will subscribe you to changes in the value
     *    of that property.
     * + Accessing an object's keys (eg with Object.keys or with `for..in`) will
     *    subscribe you to the creation/deletion of keys. Checking the presence of a
     *    key on the object with 'in' has the same effect.
     * - getOwnPropertyDescriptor does not currently subscribe you to the property.
     *    This is a choice that was made because changing a key's value will trigger
     *    this trap and we do not want to subscribe by writes. This also means that
     *    Object.hasOwnProperty doesn't subscribe as it goes through this trap.
     *
     * @param target the object for which to create a reactive proxy
     * @param callback the function to call when an observed property of the
     *  reactive has changed
     * @returns a proxy that tracks changes to it
     */
    function reactive(target, callback = NO_CALLBACK) {
        if (!canBeMadeReactive(target)) {
            throw new OwlError(`Cannot make the given value reactive`);
        }
        if (skipped.has(target)) {
            return target;
        }
        if (targets.has(target)) {
            // target is reactive, create a reactive on the underlying object instead
            return reactive(targets.get(target), callback);
        }
        if (!reactiveCache.has(target)) {
            reactiveCache.set(target, new WeakMap());
        }
        const reactivesForTarget = reactiveCache.get(target);
        if (!reactivesForTarget.has(callback)) {
            const targetRawType = rawType(target);
            const handler = COLLECTION_RAWTYPES.has(targetRawType)
                ? collectionsProxyHandler(target, callback, targetRawType)
                : basicProxyHandler(callback);
            const proxy = new Proxy(target, handler);
            reactivesForTarget.set(callback, proxy);
            targets.set(proxy, target);
        }
        return reactivesForTarget.get(callback);
    }
    /**
     * Creates a basic proxy handler for regular objects and arrays.
     *
     * @param callback @see reactive
     * @returns a proxy handler object
     */
    function basicProxyHandler(callback) {
        return {
            get(target, key, receiver) {
                // non-writable non-configurable properties cannot be made reactive
                const desc = Object.getOwnPropertyDescriptor(target, key);
                if (desc && !desc.writable && !desc.configurable) {
                    return Reflect.get(target, key, receiver);
                }
                observeTargetKey(target, key, callback);
                return possiblyReactive(Reflect.get(target, key, receiver), callback);
            },
            set(target, key, value, receiver) {
                const hadKey = objectHasOwnProperty.call(target, key);
                const originalValue = Reflect.get(target, key, receiver);
                const ret = Reflect.set(target, key, value, receiver);
                if (!hadKey && objectHasOwnProperty.call(target, key)) {
                    notifyReactives(target, KEYCHANGES);
                }
                // While Array length may trigger the set trap, it's not actually set by this
                // method but is updated behind the scenes, and the trap is not called with the
                // new value. We disable the "same-value-optimization" for it because of that.
                if (originalValue !== Reflect.get(target, key, receiver) ||
                    (key === "length" && Array.isArray(target))) {
                    notifyReactives(target, key);
                }
                return ret;
            },
            deleteProperty(target, key) {
                const ret = Reflect.deleteProperty(target, key);
                // TODO: only notify when something was actually deleted
                notifyReactives(target, KEYCHANGES);
                notifyReactives(target, key);
                return ret;
            },
            ownKeys(target) {
                observeTargetKey(target, KEYCHANGES, callback);
                return Reflect.ownKeys(target);
            },
            has(target, key) {
                // TODO: this observes all key changes instead of only the presence of the argument key
                // observing the key itself would observe value changes instead of presence changes
                // so we may need a finer grained system to distinguish observing value vs presence.
                observeTargetKey(target, KEYCHANGES, callback);
                return Reflect.has(target, key);
            },
        };
    }
    /**
     * Creates a function that will observe the key that is passed to it when called
     * and delegates to the underlying method.
     *
     * @param methodName name of the method to delegate to
     * @param target @see reactive
     * @param callback @see reactive
     */
    function makeKeyObserver(methodName, target, callback) {
        return (key) => {
            key = toRaw(key);
            observeTargetKey(target, key, callback);
            return possiblyReactive(target[methodName](key), callback);
        };
    }
    /**
     * Creates an iterable that will delegate to the underlying iteration method and
     * observe keys as necessary.
     *
     * @param methodName name of the method to delegate to
     * @param target @see reactive
     * @param callback @see reactive
     */
    function makeIteratorObserver(methodName, target, callback) {
        return function* () {
            observeTargetKey(target, KEYCHANGES, callback);
            const keys = target.keys();
            for (const item of target[methodName]()) {
                const key = keys.next().value;
                observeTargetKey(target, key, callback);
                yield possiblyReactive(item, callback);
            }
        };
    }
    /**
     * Creates a forEach function that will delegate to forEach on the underlying
     * collection while observing key changes, and keys as they're iterated over,
     * and making the passed keys/values reactive.
     *
     * @param target @see reactive
     * @param callback @see reactive
     */
    function makeForEachObserver(target, callback) {
        return function forEach(forEachCb, thisArg) {
            observeTargetKey(target, KEYCHANGES, callback);
            target.forEach(function (val, key, targetObj) {
                observeTargetKey(target, key, callback);
                forEachCb.call(thisArg, possiblyReactive(val, callback), possiblyReactive(key, callback), possiblyReactive(targetObj, callback));
            }, thisArg);
        };
    }
    /**
     * Creates a function that will delegate to an underlying method, and check if
     * that method has modified the presence or value of a key, and notify the
     * reactives appropriately.
     *
     * @param setterName name of the method to delegate to
     * @param getterName name of the method which should be used to retrieve the
     *  value before calling the delegate method for comparison purposes
     * @param target @see reactive
     */
    function delegateAndNotify(setterName, getterName, target) {
        return (key, value) => {
            key = toRaw(key);
            const hadKey = target.has(key);
            const originalValue = target[getterName](key);
            const ret = target[setterName](key, value);
            const hasKey = target.has(key);
            if (hadKey !== hasKey) {
                notifyReactives(target, KEYCHANGES);
            }
            if (originalValue !== target[getterName](key)) {
                notifyReactives(target, key);
            }
            return ret;
        };
    }
    /**
     * Creates a function that will clear the underlying collection and notify that
     * the keys of the collection have changed.
     *
     * @param target @see reactive
     */
    function makeClearNotifier(target) {
        return () => {
            const allKeys = [...target.keys()];
            target.clear();
            notifyReactives(target, KEYCHANGES);
            for (const key of allKeys) {
                notifyReactives(target, key);
            }
        };
    }
    /**
     * Maps raw type of an object to an object containing functions that can be used
     * to build an appropritate proxy handler for that raw type. Eg: when making a
     * reactive set, calling the has method should mark the key that is being
     * retrieved as observed, and calling the add or delete method should notify the
     * reactives that the key which is being added or deleted has been modified.
     */
    const rawTypeToFuncHandlers = {
        Set: (target, callback) => ({
            has: makeKeyObserver("has", target, callback),
            add: delegateAndNotify("add", "has", target),
            delete: delegateAndNotify("delete", "has", target),
            keys: makeIteratorObserver("keys", target, callback),
            values: makeIteratorObserver("values", target, callback),
            entries: makeIteratorObserver("entries", target, callback),
            [Symbol.iterator]: makeIteratorObserver(Symbol.iterator, target, callback),
            forEach: makeForEachObserver(target, callback),
            clear: makeClearNotifier(target),
            get size() {
                observeTargetKey(target, KEYCHANGES, callback);
                return target.size;
            },
        }),
        Map: (target, callback) => ({
            has: makeKeyObserver("has", target, callback),
            get: makeKeyObserver("get", target, callback),
            set: delegateAndNotify("set", "get", target),
            delete: delegateAndNotify("delete", "has", target),
            keys: makeIteratorObserver("keys", target, callback),
            values: makeIteratorObserver("values", target, callback),
            entries: makeIteratorObserver("entries", target, callback),
            [Symbol.iterator]: makeIteratorObserver(Symbol.iterator, target, callback),
            forEach: makeForEachObserver(target, callback),
            clear: makeClearNotifier(target),
            get size() {
                observeTargetKey(target, KEYCHANGES, callback);
                return target.size;
            },
        }),
        WeakMap: (target, callback) => ({
            has: makeKeyObserver("has", target, callback),
            get: makeKeyObserver("get", target, callback),
            set: delegateAndNotify("set", "get", target),
            delete: delegateAndNotify("delete", "has", target),
        }),
    };
    /**
     * Creates a proxy handler for collections (Set/Map/WeakMap)
     *
     * @param callback @see reactive
     * @param target @see reactive
     * @returns a proxy handler object
     */
    function collectionsProxyHandler(target, callback, targetRawType) {
        // TODO: if performance is an issue we can create the special handlers lazily when each
        // property is read.
        const specialHandlers = rawTypeToFuncHandlers[targetRawType](target, callback);
        return Object.assign(basicProxyHandler(callback), {
            // FIXME: probably broken when part of prototype chain since we ignore the receiver
            get(target, key) {
                if (objectHasOwnProperty.call(specialHandlers, key)) {
                    return specialHandlers[key];
                }
                observeTargetKey(target, key, callback);
                return possiblyReactive(target[key], callback);
            },
        });
    }

    let currentNode = null;
    function getCurrent() {
        if (!currentNode) {
            throw new OwlError("No active component (a hook function should only be called in 'setup')");
        }
        return currentNode;
    }
    function useComponent() {
        return currentNode.component;
    }
    /**
     * Apply default props (only top level).
     */
    function applyDefaultProps(props, defaultProps) {
        for (let propName in defaultProps) {
            if (props[propName] === undefined) {
                props[propName] = defaultProps[propName];
            }
        }
    }
    // -----------------------------------------------------------------------------
    // Integration with reactivity system (useState)
    // -----------------------------------------------------------------------------
    const batchedRenderFunctions = new WeakMap();
    /**
     * Creates a reactive object that will be observed by the current component.
     * Reading data from the returned object (eg during rendering) will cause the
     * component to subscribe to that data and be rerendered when it changes.
     *
     * @param state the state to observe
     * @returns a reactive object that will cause the component to re-render on
     *  relevant changes
     * @see reactive
     */
    function useState(state) {
        const node = getCurrent();
        let render = batchedRenderFunctions.get(node);
        if (!render) {
            render = batched(node.render.bind(node, false));
            batchedRenderFunctions.set(node, render);
            // manual implementation of onWillDestroy to break cyclic dependency
            node.willDestroy.push(clearReactivesForCallback.bind(null, render));
        }
        return reactive(state, render);
    }
    class ComponentNode {
        constructor(C, props, app, parent, parentKey) {
            this.fiber = null;
            this.bdom = null;
            this.status = 0 /* NEW */;
            this.forceNextRender = false;
            this.nextProps = null;
            this.children = Object.create(null);
            this.refs = {};
            this.willStart = [];
            this.willUpdateProps = [];
            this.willUnmount = [];
            this.mounted = [];
            this.willPatch = [];
            this.patched = [];
            this.willDestroy = [];
            currentNode = this;
            this.app = app;
            this.parent = parent;
            this.props = props;
            this.parentKey = parentKey;
            const defaultProps = C.defaultProps;
            props = Object.assign({}, props);
            if (defaultProps) {
                applyDefaultProps(props, defaultProps);
            }
            const env = (parent && parent.childEnv) || app.env;
            this.childEnv = env;
            for (const key in props) {
                const prop = props[key];
                if (prop && typeof prop === "object" && targets.has(prop)) {
                    props[key] = useState(prop);
                }
            }
            this.component = new C(props, env, this);
            const ctx = Object.assign(Object.create(this.component), { this: this.component });
            this.renderFn = app.getTemplate(C.template).bind(this.component, ctx, this);
            this.component.setup();
            currentNode = null;
        }
        mountComponent(target, options) {
            const fiber = new MountFiber(this, target, options);
            this.app.scheduler.addFiber(fiber);
            this.initiateRender(fiber);
        }
        async initiateRender(fiber) {
            this.fiber = fiber;
            if (this.mounted.length) {
                fiber.root.mounted.push(fiber);
            }
            const component = this.component;
            try {
                await Promise.all(this.willStart.map((f) => f.call(component)));
            }
            catch (e) {
                this.app.handleError({ node: this, error: e });
                return;
            }
            if (this.status === 0 /* NEW */ && this.fiber === fiber) {
                fiber.render();
            }
        }
        async render(deep) {
            if (this.status >= 2 /* CANCELLED */) {
                return;
            }
            let current = this.fiber;
            if (current && (current.root.locked || current.bdom === true)) {
                await Promise.resolve();
                // situation may have changed after the microtask tick
                current = this.fiber;
            }
            if (current) {
                if (!current.bdom && !fibersInError.has(current)) {
                    if (deep) {
                        // we want the render from this point on to be with deep=true
                        current.deep = deep;
                    }
                    return;
                }
                // if current rendering was with deep=true, we want this one to be the same
                deep = deep || current.deep;
            }
            else if (!this.bdom) {
                return;
            }
            const fiber = makeRootFiber(this);
            fiber.deep = deep;
            this.fiber = fiber;
            this.app.scheduler.addFiber(fiber);
            await Promise.resolve();
            if (this.status >= 2 /* CANCELLED */) {
                return;
            }
            // We only want to actually render the component if the following two
            // conditions are true:
            // * this.fiber: it could be null, in which case the render has been cancelled
            // * (current || !fiber.parent): if current is not null, this means that the
            //   render function was called when a render was already occurring. In this
            //   case, the pending rendering was cancelled, and the fiber needs to be
            //   rendered to complete the work.  If current is null, we check that the
            //   fiber has no parent.  If that is the case, the fiber was downgraded from
            //   a root fiber to a child fiber in the previous microtick, because it was
            //   embedded in a rendering coming from above, so the fiber will be rendered
            //   in the next microtick anyway, so we should not render it again.
            if (this.fiber === fiber && (current || !fiber.parent)) {
                fiber.render();
            }
        }
        cancel() {
            this._cancel();
            delete this.parent.children[this.parentKey];
            this.app.scheduler.scheduleDestroy(this);
        }
        _cancel() {
            this.status = 2 /* CANCELLED */;
            const children = this.children;
            for (let childKey in children) {
                children[childKey]._cancel();
            }
        }
        destroy() {
            let shouldRemove = this.status === 1 /* MOUNTED */;
            this._destroy();
            if (shouldRemove) {
                this.bdom.remove();
            }
        }
        _destroy() {
            const component = this.component;
            if (this.status === 1 /* MOUNTED */) {
                for (let cb of this.willUnmount) {
                    cb.call(component);
                }
            }
            for (let child of Object.values(this.children)) {
                child._destroy();
            }
            if (this.willDestroy.length) {
                try {
                    for (let cb of this.willDestroy) {
                        cb.call(component);
                    }
                }
                catch (e) {
                    this.app.handleError({ error: e, node: this });
                }
            }
            this.status = 3 /* DESTROYED */;
        }
        async updateAndRender(props, parentFiber) {
            this.nextProps = props;
            props = Object.assign({}, props);
            // update
            const fiber = makeChildFiber(this, parentFiber);
            this.fiber = fiber;
            const component = this.component;
            const defaultProps = component.constructor.defaultProps;
            if (defaultProps) {
                applyDefaultProps(props, defaultProps);
            }
            currentNode = this;
            for (const key in props) {
                const prop = props[key];
                if (prop && typeof prop === "object" && targets.has(prop)) {
                    props[key] = useState(prop);
                }
            }
            currentNode = null;
            const prom = Promise.all(this.willUpdateProps.map((f) => f.call(component, props)));
            await prom;
            if (fiber !== this.fiber) {
                return;
            }
            component.props = props;
            fiber.render();
            const parentRoot = parentFiber.root;
            if (this.willPatch.length) {
                parentRoot.willPatch.push(fiber);
            }
            if (this.patched.length) {
                parentRoot.patched.push(fiber);
            }
        }
        /**
         * Finds a child that has dom that is not yet updated, and update it. This
         * method is meant to be used only in the context of repatching the dom after
         * a mounted hook failed and was handled.
         */
        updateDom() {
            if (!this.fiber) {
                return;
            }
            if (this.bdom === this.fiber.bdom) {
                // If the error was handled by some child component, we need to find it to
                // apply its change
                for (let k in this.children) {
                    const child = this.children[k];
                    child.updateDom();
                }
            }
            else {
                // if we get here, this is the component that handled the error and rerendered
                // itself, so we can simply patch the dom
                this.bdom.patch(this.fiber.bdom, false);
                this.fiber.appliedToDom = true;
                this.fiber = null;
            }
        }
        /**
         * Sets a ref to a given HTMLElement.
         *
         * @param name the name of the ref to set
         * @param el the HTMLElement to set the ref to. The ref is not set if the el
         *  is null, but useRef will not return elements that are not in the DOM
         */
        setRef(name, el) {
            if (el) {
                this.refs[name] = el;
            }
        }
        // ---------------------------------------------------------------------------
        // Block DOM methods
        // ---------------------------------------------------------------------------
        firstNode() {
            const bdom = this.bdom;
            return bdom ? bdom.firstNode() : undefined;
        }
        mount(parent, anchor) {
            const bdom = this.fiber.bdom;
            this.bdom = bdom;
            bdom.mount(parent, anchor);
            this.status = 1 /* MOUNTED */;
            this.fiber.appliedToDom = true;
            this.children = this.fiber.childrenMap;
            this.fiber = null;
        }
        moveBeforeDOMNode(node, parent) {
            this.bdom.moveBeforeDOMNode(node, parent);
        }
        moveBeforeVNode(other, afterNode) {
            this.bdom.moveBeforeVNode(other ? other.bdom : null, afterNode);
        }
        patch() {
            if (this.fiber && this.fiber.parent) {
                // we only patch here renderings coming from above. renderings initiated
                // by the component will be patched independently in the appropriate
                // fiber.complete
                this._patch();
                this.props = this.nextProps;
            }
        }
        _patch() {
            let hasChildren = false;
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            for (let _k in this.children) {
                hasChildren = true;
                break;
            }
            const fiber = this.fiber;
            this.children = fiber.childrenMap;
            this.bdom.patch(fiber.bdom, hasChildren);
            fiber.appliedToDom = true;
            this.fiber = null;
        }
        beforeRemove() {
            this._destroy();
        }
        remove() {
            this.bdom.remove();
        }
        // ---------------------------------------------------------------------------
        // Some debug helpers
        // ---------------------------------------------------------------------------
        get name() {
            return this.component.constructor.name;
        }
        get subscriptions() {
            const render = batchedRenderFunctions.get(this);
            return render ? getSubscriptions(render) : [];
        }
    }

    const TIMEOUT = Symbol("timeout");
    function wrapError(fn, hookName) {
        const error = new OwlError(`The following error occurred in ${hookName}: `);
        const timeoutError = new OwlError(`${hookName}'s promise hasn't resolved after 3 seconds`);
        const node = getCurrent();
        return (...args) => {
            const onError = (cause) => {
                error.cause = cause;
                if (cause instanceof Error) {
                    error.message += `"${cause.message}"`;
                }
                else {
                    error.message = `Something that is not an Error was thrown in ${hookName} (see this Error's "cause" property)`;
                }
                throw error;
            };
            try {
                const result = fn(...args);
                if (result instanceof Promise) {
                    if (hookName === "onWillStart" || hookName === "onWillUpdateProps") {
                        const fiber = node.fiber;
                        Promise.race([
                            result.catch(() => { }),
                            new Promise((resolve) => setTimeout(() => resolve(TIMEOUT), 3000)),
                        ]).then((res) => {
                            if (res === TIMEOUT && node.fiber === fiber) {
                                console.warn(timeoutError);
                            }
                        });
                    }
                    return result.catch(onError);
                }
                return result;
            }
            catch (cause) {
                onError(cause);
            }
        };
    }
    // -----------------------------------------------------------------------------
    //  hooks
    // -----------------------------------------------------------------------------
    function onWillStart(fn) {
        const node = getCurrent();
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        node.willStart.push(decorate(fn.bind(node.component), "onWillStart"));
    }
    function onWillUpdateProps(fn) {
        const node = getCurrent();
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        node.willUpdateProps.push(decorate(fn.bind(node.component), "onWillUpdateProps"));
    }
    function onMounted(fn) {
        const node = getCurrent();
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        node.mounted.push(decorate(fn.bind(node.component), "onMounted"));
    }
    function onWillPatch(fn) {
        const node = getCurrent();
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        node.willPatch.unshift(decorate(fn.bind(node.component), "onWillPatch"));
    }
    function onPatched(fn) {
        const node = getCurrent();
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        node.patched.push(decorate(fn.bind(node.component), "onPatched"));
    }
    function onWillUnmount(fn) {
        const node = getCurrent();
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        node.willUnmount.unshift(decorate(fn.bind(node.component), "onWillUnmount"));
    }
    function onWillDestroy(fn) {
        const node = getCurrent();
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        node.willDestroy.push(decorate(fn.bind(node.component), "onWillDestroy"));
    }
    function onWillRender(fn) {
        const node = getCurrent();
        const renderFn = node.renderFn;
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        fn = decorate(fn.bind(node.component), "onWillRender");
        node.renderFn = () => {
            fn();
            return renderFn();
        };
    }
    function onRendered(fn) {
        const node = getCurrent();
        const renderFn = node.renderFn;
        const decorate = node.app.dev ? wrapError : (fn) => fn;
        fn = decorate(fn.bind(node.component), "onRendered");
        node.renderFn = () => {
            const result = renderFn();
            fn();
            return result;
        };
    }
    function onError(callback) {
        const node = getCurrent();
        let handlers = nodeErrorHandlers.get(node);
        if (!handlers) {
            handlers = [];
            nodeErrorHandlers.set(node, handlers);
        }
        handlers.push(callback.bind(node.component));
    }

    class Component {
        constructor(props, env, node) {
            this.props = props;
            this.env = env;
            this.__owl__ = node;
        }
        setup() { }
        render(deep = false) {
            this.__owl__.render(deep === true);
        }
    }
    Component.template = "";

    const VText = text("").constructor;
    class VPortal extends VText {
        constructor(selector, content) {
            super("");
            this.target = null;
            this.selector = selector;
            this.content = content;
        }
        mount(parent, anchor) {
            super.mount(parent, anchor);
            this.target = document.querySelector(this.selector);
            if (this.target) {
                this.content.mount(this.target, null);
            }
            else {
                this.content.mount(parent, anchor);
            }
        }
        beforeRemove() {
            this.content.beforeRemove();
        }
        remove() {
            if (this.content) {
                super.remove();
                this.content.remove();
                this.content = null;
            }
        }
        patch(other) {
            super.patch(other);
            if (this.content) {
                this.content.patch(other.content, true);
            }
            else {
                this.content = other.content;
                this.content.mount(this.target, null);
            }
        }
    }
    /**
     * kind of similar to <t t-slot="default"/>, but it wraps it around a VPortal
     */
    function portalTemplate(app, bdom, helpers) {
        let { callSlot } = helpers;
        return function template(ctx, node, key = "") {
            return new VPortal(ctx.props.target, callSlot(ctx, node, key, "default", false, null));
        };
    }
    class Portal extends Component {
        setup() {
            const node = this.__owl__;
            onMounted(() => {
                const portal = node.bdom;
                if (!portal.target) {
                    const target = document.querySelector(this.props.target);
                    if (target) {
                        portal.content.moveBeforeDOMNode(target.firstChild, target);
                    }
                    else {
                        throw new OwlError("invalid portal target");
                    }
                }
            });
            onWillUnmount(() => {
                const portal = node.bdom;
                portal.remove();
            });
        }
    }
    Portal.template = "__portal__";
    Portal.props = {
        target: {
            type: String,
        },
        slots: true,
    };

    // -----------------------------------------------------------------------------
    // helpers
    // -----------------------------------------------------------------------------
    const isUnionType = (t) => Array.isArray(t);
    const isBaseType = (t) => typeof t !== "object";
    const isValueType = (t) => typeof t === "object" && t && "value" in t;
    function isOptional(t) {
        return typeof t === "object" && "optional" in t ? t.optional || false : false;
    }
    function describeType(type) {
        return type === "*" || type === true ? "value" : type.name.toLowerCase();
    }
    function describe(info) {
        if (isBaseType(info)) {
            return describeType(info);
        }
        else if (isUnionType(info)) {
            return info.map(describe).join(" or ");
        }
        else if (isValueType(info)) {
            return String(info.value);
        }
        if ("element" in info) {
            return `list of ${describe({ type: info.element, optional: false })}s`;
        }
        if ("shape" in info) {
            return `object`;
        }
        return describe(info.type || "*");
    }
    function toSchema(spec) {
        return Object.fromEntries(spec.map((e) => e.endsWith("?") ? [e.slice(0, -1), { optional: true }] : [e, { type: "*", optional: false }]));
    }
    /**
     * Main validate function
     */
    function validate(obj, spec) {
        let errors = validateSchema(obj, spec);
        if (errors.length) {
            throw new OwlError("Invalid object: " + errors.join(", "));
        }
    }
    /**
     * Helper validate function, to get the list of errors. useful if one want to
     * manipulate the errors without parsing an error object
     */
    function validateSchema(obj, schema) {
        if (Array.isArray(schema)) {
            schema = toSchema(schema);
        }
        obj = toRaw(obj);
        let errors = [];
        // check if each value in obj has correct shape
        for (let key in obj) {
            if (key in schema) {
                let result = validateType(key, obj[key], schema[key]);
                if (result) {
                    errors.push(result);
                }
            }
            else if (!("*" in schema)) {
                errors.push(`unknown key '${key}'`);
            }
        }
        // check that all specified keys are defined in obj
        for (let key in schema) {
            const spec = schema[key];
            if (key !== "*" && !isOptional(spec) && !(key in obj)) {
                const isObj = typeof spec === "object" && !Array.isArray(spec);
                const isAny = spec === "*" || (isObj && "type" in spec ? spec.type === "*" : isObj);
                let detail = isAny ? "" : ` (should be a ${describe(spec)})`;
                errors.push(`'${key}' is missing${detail}`);
            }
        }
        return errors;
    }
    function validateBaseType(key, value, type) {
        if (typeof type === "function") {
            if (typeof value === "object") {
                if (!(value instanceof type)) {
                    return `'${key}' is not a ${describeType(type)}`;
                }
            }
            else if (typeof value !== type.name.toLowerCase()) {
                return `'${key}' is not a ${describeType(type)}`;
            }
        }
        return null;
    }
    function validateArrayType(key, value, descr) {
        if (!Array.isArray(value)) {
            return `'${key}' is not a list of ${describe(descr)}s`;
        }
        for (let i = 0; i < value.length; i++) {
            const error = validateType(`${key}[${i}]`, value[i], descr);
            if (error) {
                return error;
            }
        }
        return null;
    }
    function validateType(key, value, descr) {
        if (value === undefined) {
            return isOptional(descr) ? null : `'${key}' is undefined (should be a ${describe(descr)})`;
        }
        else if (isBaseType(descr)) {
            return validateBaseType(key, value, descr);
        }
        else if (isValueType(descr)) {
            return value === descr.value ? null : `'${key}' is not equal to '${descr.value}'`;
        }
        else if (isUnionType(descr)) {
            let validDescr = descr.find((p) => !validateType(key, value, p));
            return validDescr ? null : `'${key}' is not a ${describe(descr)}`;
        }
        let result = null;
        if ("element" in descr) {
            result = validateArrayType(key, value, descr.element);
        }
        else if ("shape" in descr) {
            if (typeof value !== "object" || Array.isArray(value)) {
                result = `'${key}' is not an object`;
            }
            else {
                const errors = validateSchema(value, descr.shape);
                if (errors.length) {
                    result = `'${key}' doesn't have the correct shape (${errors.join(", ")})`;
                }
            }
        }
        else if ("values" in descr) {
            if (typeof value !== "object" || Array.isArray(value)) {
                result = `'${key}' is not an object`;
            }
            else {
                const errors = Object.entries(value)
                    .map(([key, value]) => validateType(key, value, descr.values))
                    .filter(Boolean);
                if (errors.length) {
                    result = `some of the values in '${key}' are invalid (${errors.join(", ")})`;
                }
            }
        }
        if ("type" in descr && !result) {
            result = validateType(key, value, descr.type);
        }
        if ("validate" in descr && !result) {
            result = !descr.validate(value) ? `'${key}' is not valid` : null;
        }
        return result;
    }

    const ObjectCreate = Object.create;
    /**
     * This file contains utility functions that will be injected in each template,
     * to perform various useful tasks in the compiled code.
     */
    function withDefault(value, defaultValue) {
        return value === undefined || value === null || value === false ? defaultValue : value;
    }
    function callSlot(ctx, parent, key, name, dynamic, extra, defaultContent) {
        key = key + "__slot_" + name;
        const slots = ctx.props.slots || {};
        const { __render, __ctx, __scope } = slots[name] || {};
        const slotScope = ObjectCreate(__ctx || {});
        if (__scope) {
            slotScope[__scope] = extra;
        }
        const slotBDom = __render ? __render(slotScope, parent, key) : null;
        if (defaultContent) {
            let child1 = undefined;
            let child2 = undefined;
            if (slotBDom) {
                child1 = dynamic ? toggler(name, slotBDom) : slotBDom;
            }
            else {
                child2 = defaultContent(ctx, parent, key);
            }
            return multi([child1, child2]);
        }
        return slotBDom || text("");
    }
    function capture(ctx) {
        const result = ObjectCreate(ctx);
        for (let k in ctx) {
            result[k] = ctx[k];
        }
        return result;
    }
    function withKey(elem, k) {
        elem.key = k;
        return elem;
    }
    function prepareList(collection) {
        let keys;
        let values;
        if (Array.isArray(collection)) {
            keys = collection;
            values = collection;
        }
        else if (collection instanceof Map) {
            keys = [...collection.keys()];
            values = [...collection.values()];
        }
        else if (Symbol.iterator in Object(collection)) {
            keys = [...collection];
            values = keys;
        }
        else if (collection && typeof collection === "object") {
            values = Object.values(collection);
            keys = Object.keys(collection);
        }
        else {
            throw new OwlError(`Invalid loop expression: "${collection}" is not iterable`);
        }
        const n = values.length;
        return [keys, values, n, new Array(n)];
    }
    const isBoundary = Symbol("isBoundary");
    function setContextValue(ctx, key, value) {
        const ctx0 = ctx;
        while (!ctx.hasOwnProperty(key) && !ctx.hasOwnProperty(isBoundary)) {
            const newCtx = ctx.__proto__;
            if (!newCtx) {
                ctx = ctx0;
                break;
            }
            ctx = newCtx;
        }
        ctx[key] = value;
    }
    function toNumber(val) {
        const n = parseFloat(val);
        return isNaN(n) ? val : n;
    }
    function shallowEqual(l1, l2) {
        for (let i = 0, l = l1.length; i < l; i++) {
            if (l1[i] !== l2[i]) {
                return false;
            }
        }
        return true;
    }
    class LazyValue {
        constructor(fn, ctx, component, node, key) {
            this.fn = fn;
            this.ctx = capture(ctx);
            this.component = component;
            this.node = node;
            this.key = key;
        }
        evaluate() {
            return this.fn.call(this.component, this.ctx, this.node, this.key);
        }
        toString() {
            return this.evaluate().toString();
        }
    }
    /*
     * Safely outputs `value` as a block depending on the nature of `value`
     */
    function safeOutput(value, defaultValue) {
        if (value === undefined || value === null) {
            return defaultValue ? toggler("default", defaultValue) : toggler("undefined", text(""));
        }
        let safeKey;
        let block;
        switch (typeof value) {
            case "object":
                if (value instanceof Markup) {
                    safeKey = `string_safe`;
                    block = html(value);
                }
                else if (value instanceof LazyValue) {
                    safeKey = `lazy_value`;
                    block = value.evaluate();
                }
                else if (value instanceof String) {
                    safeKey = "string_unsafe";
                    block = text(value);
                }
                else {
                    // Assuming it is a block
                    safeKey = "block_safe";
                    block = value;
                }
                break;
            case "string":
                safeKey = "string_unsafe";
                block = text(value);
                break;
            default:
                safeKey = "string_unsafe";
                block = text(String(value));
        }
        return toggler(safeKey, block);
    }
    /**
     * Validate the component props (or next props) against the (static) props
     * description.  This is potentially an expensive operation: it may needs to
     * visit recursively the props and all the children to check if they are valid.
     * This is why it is only done in 'dev' mode.
     */
    function validateProps(name, props, comp) {
        const ComponentClass = typeof name !== "string"
            ? name
            : comp.constructor.components[name];
        if (!ComponentClass) {
            // this is an error, wrong component. We silently return here instead so the
            // error is triggered by the usual path ('component' function)
            return;
        }
        const schema = ComponentClass.props;
        if (!schema) {
            if (comp.__owl__.app.warnIfNoStaticProps) {
                console.warn(`Component '${ComponentClass.name}' does not have a static props description`);
            }
            return;
        }
        const defaultProps = ComponentClass.defaultProps;
        if (defaultProps) {
            let isMandatory = (name) => Array.isArray(schema)
                ? schema.includes(name)
                : name in schema && !("*" in schema) && !isOptional(schema[name]);
            for (let p in defaultProps) {
                if (isMandatory(p)) {
                    throw new OwlError(`A default value cannot be defined for a mandatory prop (name: '${p}', component: ${ComponentClass.name})`);
                }
            }
        }
        const errors = validateSchema(props, schema);
        if (errors.length) {
            throw new OwlError(`Invalid props for component '${ComponentClass.name}': ` + errors.join(", "));
        }
    }
    function makeRefWrapper(node) {
        let refNames = new Set();
        return (name, fn) => {
            if (refNames.has(name)) {
                throw new OwlError(`Cannot set the same ref more than once in the same component, ref "${name}" was set multiple times in ${node.name}`);
            }
            refNames.add(name);
            return fn;
        };
    }
    const helpers = {
        withDefault,
        zero: Symbol("zero"),
        isBoundary,
        callSlot,
        capture,
        withKey,
        prepareList,
        setContextValue,
        shallowEqual,
        toNumber,
        validateProps,
        LazyValue,
        safeOutput,
        createCatcher,
        markRaw,
        OwlError,
        makeRefWrapper,
    };

    const bdom = { text, createBlock, list, multi, html, toggler, comment };
    function parseXML$1(xml) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(xml, "text/xml");
        if (doc.getElementsByTagName("parsererror").length) {
            let msg = "Invalid XML in template.";
            const parsererrorText = doc.getElementsByTagName("parsererror")[0].textContent;
            if (parsererrorText) {
                msg += "\nThe parser has produced the following error message:\n" + parsererrorText;
                const re = /\d+/g;
                const firstMatch = re.exec(parsererrorText);
                if (firstMatch) {
                    const lineNumber = Number(firstMatch[0]);
                    const line = xml.split("\n")[lineNumber - 1];
                    const secondMatch = re.exec(parsererrorText);
                    if (line && secondMatch) {
                        const columnIndex = Number(secondMatch[0]) - 1;
                        if (line[columnIndex]) {
                            msg +=
                                `\nThe error might be located at xml line ${lineNumber} column ${columnIndex}\n` +
                                    `${line}\n${"-".repeat(columnIndex - 1)}^`;
                        }
                    }
                }
            }
            throw new OwlError(msg);
        }
        return doc;
    }
    class TemplateSet {
        constructor(config = {}) {
            this.rawTemplates = Object.create(globalTemplates);
            this.templates = {};
            this.Portal = Portal;
            this.dev = config.dev || false;
            this.translateFn = config.translateFn;
            this.translatableAttributes = config.translatableAttributes;
            if (config.templates) {
                this.addTemplates(config.templates);
            }
        }
        static registerTemplate(name, fn) {
            globalTemplates[name] = fn;
        }
        addTemplate(name, template) {
            if (name in this.rawTemplates) {
                // this check can be expensive, just silently ignore double definitions outside dev mode
                if (!this.dev) {
                    return;
                }
                const rawTemplate = this.rawTemplates[name];
                const currentAsString = typeof rawTemplate === "string"
                    ? rawTemplate
                    : rawTemplate instanceof Element
                        ? rawTemplate.outerHTML
                        : rawTemplate.toString();
                const newAsString = typeof template === "string" ? template : template.outerHTML;
                if (currentAsString === newAsString) {
                    return;
                }
                throw new OwlError(`Template ${name} already defined with different content`);
            }
            this.rawTemplates[name] = template;
        }
        addTemplates(xml) {
            if (!xml) {
                // empty string
                return;
            }
            xml = xml instanceof Document ? xml : parseXML$1(xml);
            for (const template of xml.querySelectorAll("[t-name]")) {
                const name = template.getAttribute("t-name");
                this.addTemplate(name, template);
            }
        }
        getTemplate(name) {
            if (!(name in this.templates)) {
                const rawTemplate = this.rawTemplates[name];
                if (rawTemplate === undefined) {
                    let extraInfo = "";
                    try {
                        const componentName = getCurrent().component.constructor.name;
                        extraInfo = ` (for component "${componentName}")`;
                    }
                    catch { }
                    throw new OwlError(`Missing template: "${name}"${extraInfo}`);
                }
                const isFn = typeof rawTemplate === "function" && !(rawTemplate instanceof Element);
                const templateFn = isFn ? rawTemplate : this._compileTemplate(name, rawTemplate);
                // first add a function to lazily get the template, in case there is a
                // recursive call to the template name
                const templates = this.templates;
                this.templates[name] = function (context, parent) {
                    return templates[name].call(this, context, parent);
                };
                const template = templateFn(this, bdom, helpers);
                this.templates[name] = template;
            }
            return this.templates[name];
        }
        _compileTemplate(name, template) {
            throw new OwlError(`Unable to compile a template. Please use owl full build instead`);
        }
        callTemplate(owner, subTemplate, ctx, parent, key) {
            const template = this.getTemplate(subTemplate);
            return toggler(subTemplate, template.call(owner, ctx, parent, key + subTemplate));
        }
    }
    // -----------------------------------------------------------------------------
    //  xml tag helper
    // -----------------------------------------------------------------------------
    const globalTemplates = {};
    function xml(...args) {
        const name = `__template__${xml.nextId++}`;
        const value = String.raw(...args);
        globalTemplates[name] = value;
        return name;
    }
    xml.nextId = 1;
    TemplateSet.registerTemplate("__portal__", portalTemplate);

<<<<<<< HEAD
    /**
     * Owl QWeb Expression Parser
     *
     * Owl needs in various contexts to be able to understand the structure of a
     * string representing a javascript expression.  The usual goal is to be able
     * to rewrite some variables.  For example, if a template has
     *
     *  ```xml
     *  <t t-if="computeSomething({val: state.val})">...</t>
     * ```
     *
     * this needs to be translated in something like this:
     *
     * ```js
     *   if (context["computeSomething"]({val: context["state"].val})) { ... }
     * ```
     *
     * This file contains the implementation of an extremely naive tokenizer/parser
     * and evaluator for javascript expressions.  The supported grammar is basically
     * only expressive enough to understand the shape of objects, of arrays, and
     * various operators.
     */
    //------------------------------------------------------------------------------
    // Misc types, constants and helpers
    //------------------------------------------------------------------------------
    const RESERVED_WORDS = "true,false,NaN,null,undefined,debugger,console,window,in,instanceof,new,function,return,eval,void,Math,RegExp,Array,Object,Date".split(",");
    const WORD_REPLACEMENT = Object.assign(Object.create(null), {
        and: "&&",
        or: "||",
        gt: ">",
        gte: ">=",
        lt: "<",
        lte: "<=",
    });
    const STATIC_TOKEN_MAP = Object.assign(Object.create(null), {
        "{": "LEFT_BRACE",
        "}": "RIGHT_BRACE",
        "[": "LEFT_BRACKET",
        "]": "RIGHT_BRACKET",
        ":": "COLON",
        ",": "COMMA",
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
    });
    // note that the space after typeof is relevant. It makes sure that the formatted
    // expression has a space after typeof. Currently we don't support delete and void
    const OPERATORS = "...,.,===,==,+,!==,!=,!,||,&&,>=,>,<=,<,?,-,*,/,%,typeof ,=>,=,;,in ,new ,|,&,^,~".split(",");
    let tokenizeString = function (expr) {
        let s = expr[0];
        let start = s;
        if (s !== "'" && s !== '"' && s !== "`") {
            return false;
        }
        let i = 1;
        let cur;
        while (expr[i] && expr[i] !== start) {
            cur = expr[i];
            s += cur;
            if (cur === "\\") {
                i++;
                cur = expr[i];
                if (!cur) {
                    throw new OwlError("Invalid expression");
                }
                s += cur;
            }
            i++;
        }
        if (expr[i] !== start) {
            throw new OwlError("Invalid expression");
        }
        s += start;
        if (start === "`") {
            return {
                type: "TEMPLATE_STRING",
                value: s,
                replace(replacer) {
                    return s.replace(/\$\{(.*?)\}/g, (match, group) => {
                        return "${" + replacer(group) + "}";
                    });
                },
            };
        }
        return { type: "VALUE", value: s };
    };
    let tokenizeNumber = function (expr) {
        let s = expr[0];
        if (s && s.match(/[0-9]/)) {
            let i = 1;
            while (expr[i] && expr[i].match(/[0-9]|\./)) {
                s += expr[i];
                i++;
            }
            return { type: "VALUE", value: s };
        }
        else {
            return false;
        }
    };
    let tokenizeSymbol = function (expr) {
        let s = expr[0];
        if (s && s.match(/[a-zA-Z_\$]/)) {
            let i = 1;
            while (expr[i] && expr[i].match(/\w/)) {
                s += expr[i];
                i++;
            }
            if (s in WORD_REPLACEMENT) {
                return { type: "OPERATOR", value: WORD_REPLACEMENT[s], size: s.length };
            }
            return { type: "SYMBOL", value: s };
        }
        else {
            return false;
        }
    };
    const tokenizeStatic = function (expr) {
        const char = expr[0];
        if (char && char in STATIC_TOKEN_MAP) {
            return { type: STATIC_TOKEN_MAP[char], value: char };
        }
        return false;
    };
    const tokenizeOperator = function (expr) {
        for (let op of OPERATORS) {
            if (expr.startsWith(op)) {
                return { type: "OPERATOR", value: op };
            }
        }
        return false;
    };
    const TOKENIZERS = [
        tokenizeString,
        tokenizeNumber,
        tokenizeOperator,
        tokenizeSymbol,
        tokenizeStatic,
    ];
    /**
     * Convert a javascript expression (as a string) into a list of tokens. For
     * example: `tokenize("1 + b")` will return:
     * ```js
     *  [
     *   {type: "VALUE", value: "1"},
     *   {type: "OPERATOR", value: "+"},
     *   {type: "SYMBOL", value: "b"}
     * ]
     * ```
     */
    function tokenize(expr) {
        const result = [];
        let token = true;
        let error;
        let current = expr;
        try {
            while (token) {
                current = current.trim();
                if (current) {
                    for (let tokenizer of TOKENIZERS) {
                        token = tokenizer(current);
                        if (token) {
                            result.push(token);
                            current = current.slice(token.size || token.value.length);
                            break;
                        }
                    }
                }
                else {
                    token = false;
                }
            }
        }
        catch (e) {
            error = e; // Silence all errors and throw a generic error below
        }
        if (current.length || error) {
            throw new OwlError(`Tokenizer error: could not tokenize \`${expr}\``);
        }
        return result;
    }
    //------------------------------------------------------------------------------
    // Expression "evaluator"
    //------------------------------------------------------------------------------
    const isLeftSeparator = (token) => token && (token.type === "LEFT_BRACE" || token.type === "COMMA");
    const isRightSeparator = (token) => token && (token.type === "RIGHT_BRACE" || token.type === "COMMA");
    /**
     * This is the main function exported by this file. This is the code that will
     * process an expression (given as a string) and returns another expression with
     * proper lookups in the context.
     *
     * Usually, this kind of code would be very simple to do if we had an AST (so,
     * if we had a javascript parser), since then, we would only need to find the
     * variables and replace them.  However, a parser is more complicated, and there
     * are no standard builtin parser API.
     *
     * Since this method is applied to simple javasript expressions, and the work to
     * be done is actually quite simple, we actually can get away with not using a
     * parser, which helps with the code size.
     *
     * Here is the heuristic used by this method to determine if a token is a
     * variable:
     * - by default, all symbols are considered a variable
     * - unless the previous token is a dot (in that case, this is a property: `a.b`)
     * - or if the previous token is a left brace or a comma, and the next token is
     *   a colon (in that case, this is an object key: `{a: b}`)
     *
     * Some specific code is also required to support arrow functions. If we detect
     * the arrow operator, then we add the current (or some previous tokens) token to
     * the list of variables so it does not get replaced by a lookup in the context
     */
    function compileExprToArray(expr) {
        const localVars = new Set();
        const tokens = tokenize(expr);
        let i = 0;
        let stack = []; // to track last opening [ or {
        while (i < tokens.length) {
            let token = tokens[i];
            let prevToken = tokens[i - 1];
            let nextToken = tokens[i + 1];
            let groupType = stack[stack.length - 1];
            switch (token.type) {
                case "LEFT_BRACE":
                case "LEFT_BRACKET":
                    stack.push(token.type);
                    break;
                case "RIGHT_BRACE":
                case "RIGHT_BRACKET":
                    stack.pop();
            }
            let isVar = token.type === "SYMBOL" && !RESERVED_WORDS.includes(token.value);
            if (token.type === "SYMBOL" && !RESERVED_WORDS.includes(token.value)) {
                if (prevToken) {
                    // normalize missing tokens: {a} should be equivalent to {a:a}
                    if (groupType === "LEFT_BRACE" &&
                        isLeftSeparator(prevToken) &&
                        isRightSeparator(nextToken)) {
                        tokens.splice(i + 1, 0, { type: "COLON", value: ":" }, { ...token });
                        nextToken = tokens[i + 1];
                    }
                    if (prevToken.type === "OPERATOR" && prevToken.value === ".") {
                        isVar = false;
                    }
                    else if (prevToken.type === "LEFT_BRACE" || prevToken.type === "COMMA") {
                        if (nextToken && nextToken.type === "COLON") {
                            isVar = false;
                        }
                    }
                }
            }
            if (token.type === "TEMPLATE_STRING") {
                token.value = token.replace((expr) => compileExpr(expr));
            }
            if (nextToken && nextToken.type === "OPERATOR" && nextToken.value === "=>") {
                if (token.type === "RIGHT_PAREN") {
                    let j = i - 1;
                    while (j > 0 && tokens[j].type !== "LEFT_PAREN") {
                        if (tokens[j].type === "SYMBOL" && tokens[j].originalValue) {
                            tokens[j].value = tokens[j].originalValue;
                            localVars.add(tokens[j].value); //] = { id: tokens[j].value, expr: tokens[j].value };
                        }
                        j--;
                    }
                }
                else {
                    localVars.add(token.value); //] = { id: token.value, expr: token.value };
                }
            }
            if (isVar) {
                token.varName = token.value;
                if (!localVars.has(token.value)) {
                    token.originalValue = token.value;
                    token.value = `ctx['${token.value}']`;
                }
            }
            i++;
        }
        // Mark all variables that have been used locally.
        // This assumes the expression has only one scope (incorrect but "good enough for now")
        for (const token of tokens) {
            if (token.type === "SYMBOL" && token.varName && localVars.has(token.value)) {
                token.originalValue = token.value;
                token.value = `_${token.value}`;
                token.isLocal = true;
            }
        }
        return tokens;
    }
    // Leading spaces are trimmed during tokenization, so they need to be added back for some values
    const paddedValues = new Map([["in ", " in "]]);
    function compileExpr(expr) {
        return compileExprToArray(expr)
            .map((t) => paddedValues.get(t.value) || t.value)
            .join("");
    }
    const INTERP_REGEXP = /\{\{.*?\}\}|\#\{.*?\}/g;
    function replaceDynamicParts(s, replacer) {
        let matches = s.match(INTERP_REGEXP);
        if (matches && matches[0].length === s.length) {
            return `(${replacer(s.slice(2, matches[0][0] === "{" ? -2 : -1))})`;
        }
        let r = s.replace(INTERP_REGEXP, (s) => "${" + replacer(s.slice(2, s[0] === "{" ? -2 : -1)) + "}");
        return "`" + r + "`";
    }
    function interpolate(s) {
        return replaceDynamicParts(s, compileExpr);
    }

    const whitespaceRE = /\s+/g;
    // using a non-html document so that <inner/outer>HTML serializes as XML instead
    // of HTML (as we will parse it as xml later)
    const xmlDoc = document.implementation.createDocument(null, null, null);
    const MODS = new Set(["stop", "capture", "prevent", "self", "synthetic"]);
    let nextDataIds = {};
    function generateId(prefix = "") {
        nextDataIds[prefix] = (nextDataIds[prefix] || 0) + 1;
        return prefix + nextDataIds[prefix];
    }
    function isProp(tag, key) {
        switch (tag) {
            case "input":
                return (key === "checked" ||
                    key === "indeterminate" ||
                    key === "value" ||
                    key === "readonly" ||
                    key === "readOnly" ||
                    key === "disabled");
            case "option":
                return key === "selected" || key === "disabled";
            case "textarea":
                return key === "value" || key === "readonly" || key === "readOnly" || key === "disabled";
            case "select":
                return key === "value" || key === "disabled";
            case "button":
            case "optgroup":
                return key === "disabled";
        }
        return false;
    }
    // -----------------------------------------------------------------------------
    // BlockDescription
    // -----------------------------------------------------------------------------
    class BlockDescription {
        constructor(target, type) {
            this.dynamicTagName = null;
            this.isRoot = false;
            this.hasDynamicChildren = false;
            this.children = [];
            this.data = [];
            this.childNumber = 0;
            this.parentVar = "";
            this.id = BlockDescription.nextBlockId++;
            this.varName = "b" + this.id;
            this.blockName = "block" + this.id;
            this.target = target;
            this.type = type;
        }
        insertData(str, prefix = "d") {
            const id = generateId(prefix);
            this.target.addLine(`let ${id} = ${str};`);
            return this.data.push(id) - 1;
        }
        insert(dom) {
            if (this.currentDom) {
                this.currentDom.appendChild(dom);
            }
            else {
                this.dom = dom;
            }
        }
        generateExpr(expr) {
            if (this.type === "block") {
                const hasChildren = this.children.length;
                let params = this.data.length ? `[${this.data.join(", ")}]` : hasChildren ? "[]" : "";
                if (hasChildren) {
                    params += ", [" + this.children.map((c) => c.varName).join(", ") + "]";
                }
                if (this.dynamicTagName) {
                    return `toggler(${this.dynamicTagName}, ${this.blockName}(${this.dynamicTagName})(${params}))`;
                }
                return `${this.blockName}(${params})`;
            }
            else if (this.type === "list") {
                return `list(c_block${this.id})`;
            }
            return expr;
        }
        asXmlString() {
            // Can't use outerHTML on text/comment nodes
            // append dom to any element and use innerHTML instead
            const t = xmlDoc.createElement("t");
            t.appendChild(this.dom);
            return t.innerHTML;
        }
    }
    BlockDescription.nextBlockId = 1;
    function createContext(parentCtx, params) {
        return Object.assign({
            block: null,
            index: 0,
            forceNewBlock: true,
            translate: parentCtx.translate,
            tKeyExpr: null,
            nameSpace: parentCtx.nameSpace,
            tModelSelectedExpr: parentCtx.tModelSelectedExpr,
        }, params);
    }
    class CodeTarget {
        constructor(name, on) {
            this.indentLevel = 0;
            this.loopLevel = 0;
            this.code = [];
            this.hasRoot = false;
            this.hasCache = false;
            this.shouldProtectScope = false;
            this.hasRefWrapper = false;
            this.name = name;
            this.on = on || null;
        }
        addLine(line, idx) {
            const prefix = new Array(this.indentLevel + 2).join("  ");
            if (idx === undefined) {
                this.code.push(prefix + line);
            }
            else {
                this.code.splice(idx, 0, prefix + line);
            }
        }
        generateCode() {
            let result = [];
            result.push(`function ${this.name}(ctx, node, key = "") {`);
            if (this.shouldProtectScope) {
                result.push(`  ctx = Object.create(ctx);`);
                result.push(`  ctx[isBoundary] = 1`);
            }
            if (this.hasRefWrapper) {
                result.push(`  let refWrapper = makeRefWrapper(this.__owl__);`);
            }
            if (this.hasCache) {
                result.push(`  let cache = ctx.cache || {};`);
                result.push(`  let nextCache = ctx.cache = {};`);
            }
            for (let line of this.code) {
                result.push(line);
            }
            if (!this.hasRoot) {
                result.push(`return text('');`);
            }
            result.push(`}`);
            return result.join("\n  ");
        }
        currentKey(ctx) {
            let key = this.loopLevel ? `key${this.loopLevel}` : "key";
            if (ctx.tKeyExpr) {
                key = `${ctx.tKeyExpr} + ${key}`;
            }
            return key;
        }
    }
    const TRANSLATABLE_ATTRS = ["label", "title", "placeholder", "alt"];
    const translationRE = /^(\s*)([\s\S]+?)(\s*)$/;
    class CodeGenerator {
        constructor(ast, options) {
            this.blocks = [];
            this.nextBlockId = 1;
            this.isDebug = false;
            this.targets = [];
            this.target = new CodeTarget("template");
            this.translatableAttributes = TRANSLATABLE_ATTRS;
            this.staticDefs = [];
            this.slotNames = new Set();
            this.helpers = new Set();
            this.translateFn = options.translateFn || ((s) => s);
            if (options.translatableAttributes) {
                const attrs = new Set(TRANSLATABLE_ATTRS);
                for (let attr of options.translatableAttributes) {
                    if (attr.startsWith("-")) {
                        attrs.delete(attr.slice(1));
                    }
                    else {
                        attrs.add(attr);
                    }
                }
                this.translatableAttributes = [...attrs];
            }
            this.hasSafeContext = options.hasSafeContext || false;
            this.dev = options.dev || false;
            this.ast = ast;
            this.templateName = options.name;
        }
        generateCode() {
            const ast = this.ast;
            this.isDebug = ast.type === 12 /* TDebug */;
            BlockDescription.nextBlockId = 1;
            nextDataIds = {};
            this.compileAST(ast, {
                block: null,
                index: 0,
                forceNewBlock: false,
                isLast: true,
                translate: true,
                tKeyExpr: null,
            });
            // define blocks and utility functions
            let mainCode = [`  let { text, createBlock, list, multi, html, toggler, comment } = bdom;`];
            if (this.helpers.size) {
                mainCode.push(`let { ${[...this.helpers].join(", ")} } = helpers;`);
            }
            if (this.templateName) {
                mainCode.push(`// Template name: "${this.templateName}"`);
            }
            for (let { id, expr } of this.staticDefs) {
                mainCode.push(`const ${id} = ${expr};`);
            }
            // define all blocks
            if (this.blocks.length) {
                mainCode.push(``);
                for (let block of this.blocks) {
                    if (block.dom) {
                        let xmlString = block.asXmlString();
                        xmlString = xmlString.replace(/\\/g, "\\\\").replace(/`/g, "\\`");
                        if (block.dynamicTagName) {
                            xmlString = xmlString.replace(/^<\w+/, `<\${tag || '${block.dom.nodeName}'}`);
                            xmlString = xmlString.replace(/\w+>$/, `\${tag || '${block.dom.nodeName}'}>`);
                            mainCode.push(`let ${block.blockName} = tag => createBlock(\`${xmlString}\`);`);
                        }
                        else {
                            mainCode.push(`let ${block.blockName} = createBlock(\`${xmlString}\`);`);
                        }
                    }
                }
            }
            // define all slots/defaultcontent function
            if (this.targets.length) {
                for (let fn of this.targets) {
                    mainCode.push("");
                    mainCode = mainCode.concat(fn.generateCode());
                }
            }
            // generate main code
            mainCode.push("");
            mainCode = mainCode.concat("return " + this.target.generateCode());
            const code = mainCode.join("\n  ");
            if (this.isDebug) {
                const msg = `[Owl Debug]\n${code}`;
                console.log(msg);
            }
            return code;
        }
        compileInNewTarget(prefix, ast, ctx, on) {
            const name = generateId(prefix);
            const initialTarget = this.target;
            const target = new CodeTarget(name, on);
            this.targets.push(target);
            this.target = target;
            this.compileAST(ast, createContext(ctx));
            this.target = initialTarget;
            return name;
        }
        addLine(line, idx) {
            this.target.addLine(line, idx);
        }
        define(varName, expr) {
            this.addLine(`const ${varName} = ${expr};`);
        }
        insertAnchor(block, index = block.children.length) {
            const tag = `block-child-${index}`;
            const anchor = xmlDoc.createElement(tag);
            block.insert(anchor);
        }
        createBlock(parentBlock, type, ctx) {
            const hasRoot = this.target.hasRoot;
            const block = new BlockDescription(this.target, type);
            if (!hasRoot) {
                this.target.hasRoot = true;
                block.isRoot = true;
            }
            if (parentBlock) {
                parentBlock.children.push(block);
                if (parentBlock.type === "list") {
                    block.parentVar = `c_block${parentBlock.id}`;
                }
            }
            return block;
        }
        insertBlock(expression, block, ctx) {
            let blockExpr = block.generateExpr(expression);
            if (block.parentVar) {
                let key = this.target.currentKey(ctx);
                this.helpers.add("withKey");
                this.addLine(`${block.parentVar}[${ctx.index}] = withKey(${blockExpr}, ${key});`);
                return;
            }
            if (ctx.tKeyExpr) {
                blockExpr = `toggler(${ctx.tKeyExpr}, ${blockExpr})`;
            }
            if (block.isRoot) {
                if (this.target.on) {
                    blockExpr = this.wrapWithEventCatcher(blockExpr, this.target.on);
                }
                this.addLine(`return ${blockExpr};`);
            }
            else {
                this.define(block.varName, blockExpr);
            }
        }
        /**
         * Captures variables that are used inside of an expression. This is useful
         * because in compiled code, almost all variables are accessed through the ctx
         * object. In the case of functions, that lookup in the context can be delayed
         * which can cause issues if the value has changed since the function was
         * defined.
         *
         * @param expr the expression to capture
         * @param forceCapture whether the expression should capture its scope even if
         *  it doesn't contain a function. Useful when the expression will be used as
         *  a function body.
         * @returns a new expression that uses the captured values
         */
        captureExpression(expr, forceCapture = false) {
            if (!forceCapture && !expr.includes("=>")) {
                return compileExpr(expr);
            }
            const tokens = compileExprToArray(expr);
            const mapping = new Map();
            return tokens
                .map((tok) => {
                if (tok.varName && !tok.isLocal) {
                    if (!mapping.has(tok.varName)) {
                        const varId = generateId("v");
                        mapping.set(tok.varName, varId);
                        this.define(varId, tok.value);
                    }
                    tok.value = mapping.get(tok.varName);
                }
                return tok.value;
            })
                .join("");
        }
        translate(str) {
            const match = translationRE.exec(str);
            return match[1] + this.translateFn(match[2]) + match[3];
        }
        /**
         * @returns the newly created block name, if any
         */
        compileAST(ast, ctx) {
            switch (ast.type) {
                case 1 /* Comment */:
                    return this.compileComment(ast, ctx);
                case 0 /* Text */:
                    return this.compileText(ast, ctx);
                case 2 /* DomNode */:
                    return this.compileTDomNode(ast, ctx);
                case 4 /* TEsc */:
                    return this.compileTEsc(ast, ctx);
                case 8 /* TOut */:
                    return this.compileTOut(ast, ctx);
                case 5 /* TIf */:
                    return this.compileTIf(ast, ctx);
                case 9 /* TForEach */:
                    return this.compileTForeach(ast, ctx);
                case 10 /* TKey */:
                    return this.compileTKey(ast, ctx);
                case 3 /* Multi */:
                    return this.compileMulti(ast, ctx);
                case 7 /* TCall */:
                    return this.compileTCall(ast, ctx);
                case 15 /* TCallBlock */:
                    return this.compileTCallBlock(ast, ctx);
                case 6 /* TSet */:
                    return this.compileTSet(ast, ctx);
                case 11 /* TComponent */:
                    return this.compileComponent(ast, ctx);
                case 12 /* TDebug */:
                    return this.compileDebug(ast, ctx);
                case 13 /* TLog */:
                    return this.compileLog(ast, ctx);
                case 14 /* TSlot */:
                    return this.compileTSlot(ast, ctx);
                case 16 /* TTranslation */:
                    return this.compileTTranslation(ast, ctx);
                case 17 /* TPortal */:
                    return this.compileTPortal(ast, ctx);
            }
        }
        compileDebug(ast, ctx) {
            this.addLine(`debugger;`);
            if (ast.content) {
                return this.compileAST(ast.content, ctx);
            }
            return null;
        }
        compileLog(ast, ctx) {
            this.addLine(`console.log(${compileExpr(ast.expr)});`);
            if (ast.content) {
                return this.compileAST(ast.content, ctx);
            }
            return null;
        }
        compileComment(ast, ctx) {
            let { block, forceNewBlock } = ctx;
            const isNewBlock = !block || forceNewBlock;
            if (isNewBlock) {
                block = this.createBlock(block, "comment", ctx);
                this.insertBlock(`comment(\`${ast.value}\`)`, block, {
                    ...ctx,
                    forceNewBlock: forceNewBlock && !block,
                });
=======
    let localStorage = null;
    const browser = {
        setTimeout: window.setTimeout.bind(window),
        clearTimeout: window.clearTimeout.bind(window),
        setInterval: window.setInterval.bind(window),
        clearInterval: window.clearInterval.bind(window),
        requestAnimationFrame: window.requestAnimationFrame.bind(window),
        random: Math.random,
        Date: window.Date,
        fetch: (window.fetch || (() => { })).bind(window),
        get localStorage() {
            return localStorage || window.localStorage;
        },
        set localStorage(newLocalStorage) {
            localStorage = newLocalStorage;
        },
    };

    /**
     * Owl Utils
     *
     * We have here a small collection of utility functions:
     *
     * - whenReady
     * - loadJS
     * - loadFile
     * - escape
     * - debounce
     */
    function whenReady(fn) {
        return new Promise(function (resolve) {
            if (document.readyState !== "loading") {
                resolve();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
            else {
                const text = xmlDoc.createComment(ast.value);
                block.insert(text);
            }
            return block.varName;
        }
        compileText(ast, ctx) {
            let { block, forceNewBlock } = ctx;
            let value = ast.value;
            if (value && ctx.translate !== false) {
                value = this.translate(value);
            }
            if (!ctx.inPreTag) {
                value = value.replace(whitespaceRE, " ");
            }
            if (!block || forceNewBlock) {
                block = this.createBlock(block, "text", ctx);
                this.insertBlock(`text(\`${value}\`)`, block, {
                    ...ctx,
                    forceNewBlock: forceNewBlock && !block,
                });
            }
            else {
                const createFn = ast.type === 0 /* Text */ ? xmlDoc.createTextNode : xmlDoc.createComment;
                block.insert(createFn.call(xmlDoc, value));
            }
            return block.varName;
        }
        generateHandlerCode(rawEvent, handler) {
            const modifiers = rawEvent
                .split(".")
                .slice(1)
                .map((m) => {
                if (!MODS.has(m)) {
                    throw new OwlError(`Unknown event modifier: '${m}'`);
                }
                return `"${m}"`;
            });
            let modifiersCode = "";
            if (modifiers.length) {
                modifiersCode = `${modifiers.join(",")}, `;
            }
            return `[${modifiersCode}${this.captureExpression(handler)}, ctx]`;
        }
        compileTDomNode(ast, ctx) {
            let { block, forceNewBlock } = ctx;
            const isNewBlock = !block || forceNewBlock || ast.dynamicTag !== null || ast.ns;
            let codeIdx = this.target.code.length;
            if (isNewBlock) {
                if ((ast.dynamicTag || ctx.tKeyExpr || ast.ns) && ctx.block) {
                    this.insertAnchor(ctx.block);
                }
                block = this.createBlock(block, "block", ctx);
                this.blocks.push(block);
                if (ast.dynamicTag) {
                    const tagExpr = generateId("tag");
                    this.define(tagExpr, compileExpr(ast.dynamicTag));
                    block.dynamicTagName = tagExpr;
                }
            }
<<<<<<< HEAD
            // attributes
            const attrs = {};
            for (let key in ast.attrs) {
                let expr, attrName;
                if (key.startsWith("t-attf")) {
                    expr = interpolate(ast.attrs[key]);
                    const idx = block.insertData(expr, "attr");
                    attrName = key.slice(7);
                    attrs["block-attribute-" + idx] = attrName;
                }
                else if (key.startsWith("t-att")) {
                    attrName = key === "t-att" ? null : key.slice(6);
                    expr = compileExpr(ast.attrs[key]);
                    if (attrName && isProp(ast.tag, attrName)) {
                        if (attrName === "readonly") {
                            // the property has a different name than the attribute
                            attrName = "readOnly";
                        }
                        // we force a new string or new boolean to bypass the equality check in blockdom when patching same value
                        if (attrName === "value") {
                            // When the expression is falsy (except 0), fall back to an empty string
                            expr = `new String((${expr}) === 0 ? 0 : ((${expr}) || ""))`;
                        }
                        else {
                            expr = `new Boolean(${expr})`;
                        }
                        const idx = block.insertData(expr, "prop");
                        attrs[`block-property-${idx}`] = attrName;
                    }
                    else {
                        const idx = block.insertData(expr, "attr");
                        if (key === "t-att") {
                            attrs[`block-attributes`] = String(idx);
                        }
                        else {
                            attrs[`block-attribute-${idx}`] = attrName;
                        }
                    }
                }
                else if (this.translatableAttributes.includes(key)) {
                    attrs[key] = this.translateFn(ast.attrs[key]);
                }
                else {
                    expr = `"${ast.attrs[key]}"`;
                    attrName = key;
                    attrs[key] = ast.attrs[key];
                }
                if (attrName === "value" && ctx.tModelSelectedExpr) {
                    let selectedId = block.insertData(`${ctx.tModelSelectedExpr} === ${expr}`, "attr");
                    attrs[`block-attribute-${selectedId}`] = "selected";
=======
            const callNow = immediate && !timeout;
            browser.clearTimeout(timeout);
            timeout = browser.setTimeout(later, wait);
            if (callNow) {
                func.apply(context, args);
            }
        };
    }
    function shallowEqual(p1, p2) {
        for (let k in p1) {
            if (p1[k] !== p2[k]) {
                return false;
            }
        }
        return true;
    }

    var _utils = /*#__PURE__*/Object.freeze({
        __proto__: null,
        whenReady: whenReady,
        loadJS: loadJS,
        loadFile: loadFile,
        escape: escape,
        debounce: debounce,
        shallowEqual: shallowEqual
    });

    //------------------------------------------------------------------------------
    // Const/global stuff/helpers
    //------------------------------------------------------------------------------
    const TRANSLATABLE_ATTRS = ["label", "title", "placeholder", "alt"];
    const lineBreakRE = /[\r\n]/;
    const whitespaceRE = /\s+/g;
    const translationRE = /^(\s*)([\s\S]+?)(\s*)$/;
    const NODE_HOOKS_PARAMS = {
        create: "(_, n)",
        insert: "vn",
        remove: "(vn, rm)",
        destroy: "()",
    };
    function isComponent(obj) {
        return obj && obj.hasOwnProperty("__owl__");
    }
    class VDomArray extends Array {
        toString() {
            return vDomToString(this);
        }
    }
    function vDomToString(vdom) {
        return vdom
            .map((vnode) => {
            if (vnode.sel) {
                const node = document.createElement(vnode.sel);
                const result = patch(node, vnode);
                return result.elm.outerHTML;
            }
            else {
                return vnode.text;
            }
        })
            .join("");
    }
    const UTILS = {
        zero: Symbol("zero"),
        toClassObj(expr) {
            const result = {};
            if (typeof expr === "string") {
                // we transform here a list of classes into an object:
                //  'hey you' becomes {hey: true, you: true}
                expr = expr.trim();
                if (!expr) {
                    return {};
                }
                let words = expr.split(/\s+/);
                for (let i = 0; i < words.length; i++) {
                    result[words[i]] = true;
                }
                return result;
            }
            // this is already an object, but we may need to split keys:
            // {'a b': true, 'a c': false} should become {a: true, b: true, c: false}
            for (let key in expr) {
                const value = expr[key];
                const words = key.split(/\s+/);
                for (let word of words) {
                    result[word] = result[word] || value;
                }
            }
            return result;
        },
        /**
         * This method combines the current context with the variables defined in a
         * scope for use in a slot.
         *
         * The implementation is kind of tricky because we want to preserve the
         * prototype chain structure of the cloned result. So we need to traverse the
         * prototype chain, cloning each level respectively.
         */
        combine(context, scope) {
            let clone = context;
            const scopeStack = [];
            while (!isComponent(scope)) {
                scopeStack.push(scope);
                scope = scope.__proto__;
            }
            while (scopeStack.length) {
                let scope = scopeStack.pop();
                clone = Object.create(clone);
                Object.assign(clone, scope);
            }
            return clone;
        },
        shallowEqual,
        addNameSpace(vnode) {
            addNS(vnode.data, vnode.children, vnode.sel);
        },
        VDomArray,
        vDomToString,
        getComponent(obj) {
            while (obj && !isComponent(obj)) {
                obj = obj.__proto__;
            }
            return obj;
        },
        getScope(obj, property) {
            const obj0 = obj;
            while (obj &&
                !obj.hasOwnProperty(property) &&
                !(obj.hasOwnProperty("__access_mode__") && obj.__access_mode__ === "ro")) {
                const newObj = obj.__proto__;
                if (!newObj || isComponent(newObj)) {
                    return obj0;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                }
            }
            // t-model
            let tModelSelectedExpr;
            if (ast.model) {
                const { hasDynamicChildren, baseExpr, expr, eventType, shouldNumberize, shouldTrim, targetAttr, specialInitTargetAttr, } = ast.model;
                const baseExpression = compileExpr(baseExpr);
                const bExprId = generateId("bExpr");
                this.define(bExprId, baseExpression);
                const expression = compileExpr(expr);
                const exprId = generateId("expr");
                this.define(exprId, expression);
                const fullExpression = `${bExprId}[${exprId}]`;
                let idx;
                if (specialInitTargetAttr) {
                    let targetExpr = targetAttr in attrs && `'${attrs[targetAttr]}'`;
                    if (!targetExpr && ast.attrs) {
                        // look at the dynamic attribute counterpart
                        const dynamicTgExpr = ast.attrs[`t-att-${targetAttr}`];
                        if (dynamicTgExpr) {
                            targetExpr = compileExpr(dynamicTgExpr);
                        }
                    }
                    idx = block.insertData(`${fullExpression} === ${targetExpr}`, "prop");
                    attrs[`block-property-${idx}`] = specialInitTargetAttr;
                }
                else if (hasDynamicChildren) {
                    const bValueId = generateId("bValue");
                    tModelSelectedExpr = `${bValueId}`;
                    this.define(tModelSelectedExpr, fullExpression);
                }
                else {
                    idx = block.insertData(`${fullExpression}`, "prop");
                    attrs[`block-property-${idx}`] = targetAttr;
                }
                this.helpers.add("toNumber");
                let valueCode = `ev.target.${targetAttr}`;
                valueCode = shouldTrim ? `${valueCode}.trim()` : valueCode;
                valueCode = shouldNumberize ? `toNumber(${valueCode})` : valueCode;
                const handler = `[(ev) => { ${fullExpression} = ${valueCode}; }]`;
                idx = block.insertData(handler, "hdlr");
                attrs[`block-handler-${idx}`] = eventType;
            }
            // event handlers
            for (let ev in ast.on) {
                const name = this.generateHandlerCode(ev, ast.on[ev]);
                const idx = block.insertData(name, "hdlr");
                attrs[`block-handler-${idx}`] = ev;
            }
            // t-ref
            if (ast.ref) {
                if (this.dev) {
                    this.helpers.add("makeRefWrapper");
                    this.target.hasRefWrapper = true;
                }
                const isDynamic = INTERP_REGEXP.test(ast.ref);
                let name = `\`${ast.ref}\``;
                if (isDynamic) {
                    name = replaceDynamicParts(ast.ref, (expr) => this.captureExpression(expr, true));
                }
                let setRefStr = `(el) => this.__owl__.setRef((${name}), el)`;
                if (this.dev) {
                    setRefStr = `refWrapper(${name}, ${setRefStr})`;
                }
                const idx = block.insertData(setRefStr, "ref");
                attrs["block-ref"] = String(idx);
            }
            const nameSpace = ast.ns || ctx.nameSpace;
            const dom = nameSpace
                ? xmlDoc.createElementNS(nameSpace, ast.tag)
                : xmlDoc.createElement(ast.tag);
            for (const [attr, val] of Object.entries(attrs)) {
                if (!(attr === "class" && val === "")) {
                    dom.setAttribute(attr, val);
                }
            }
            block.insert(dom);
            if (ast.content.length) {
                const initialDom = block.currentDom;
                block.currentDom = dom;
                const children = ast.content;
                for (let i = 0; i < children.length; i++) {
                    const child = ast.content[i];
                    const subCtx = createContext(ctx, {
                        block,
                        index: block.childNumber,
                        forceNewBlock: false,
                        isLast: ctx.isLast && i === children.length - 1,
                        tKeyExpr: ctx.tKeyExpr,
                        nameSpace,
                        tModelSelectedExpr,
                        inPreTag: ctx.inPreTag || ast.tag === "pre",
                    });
                    this.compileAST(child, subCtx);
                }
                block.currentDom = initialDom;
            }
            if (isNewBlock) {
                this.insertBlock(`${block.blockName}(ddd)`, block, ctx);
                // may need to rewrite code!
                if (block.children.length && block.hasDynamicChildren) {
                    const code = this.target.code;
                    const children = block.children.slice();
                    let current = children.shift();
                    for (let i = codeIdx; i < code.length; i++) {
                        if (code[i].trimStart().startsWith(`const ${current.varName} `)) {
                            code[i] = code[i].replace(`const ${current.varName}`, current.varName);
                            current = children.shift();
                            if (!current)
                                break;
                        }
                    }
                    this.addLine(`let ${block.children.map((c) => c.varName).join(", ")};`, codeIdx);
                }
            }
            return block.varName;
        }
        compileTEsc(ast, ctx) {
            let { block, forceNewBlock } = ctx;
            let expr;
            if (ast.expr === "0") {
                this.helpers.add("zero");
                expr = `ctx[zero]`;
            }
            else {
                expr = compileExpr(ast.expr);
                if (ast.defaultValue) {
                    this.helpers.add("withDefault");
                    expr = `withDefault(${expr}, \`${ast.defaultValue}\`)`;
                }
            }
            if (!block || forceNewBlock) {
                block = this.createBlock(block, "text", ctx);
                this.insertBlock(`text(${expr})`, block, { ...ctx, forceNewBlock: forceNewBlock && !block });
            }
            else {
                const idx = block.insertData(expr, "txt");
                const text = xmlDoc.createElement(`block-text-${idx}`);
                block.insert(text);
            }
            return block.varName;
        }
        compileTOut(ast, ctx) {
            let { block } = ctx;
            if (block) {
                this.insertAnchor(block);
            }
            block = this.createBlock(block, "html", ctx);
            let blockStr;
            if (ast.expr === "0") {
                this.helpers.add("zero");
                blockStr = `ctx[zero]`;
            }
            else if (ast.body) {
                let bodyValue = null;
                bodyValue = BlockDescription.nextBlockId;
                const subCtx = createContext(ctx);
                this.compileAST({ type: 3 /* Multi */, content: ast.body }, subCtx);
                this.helpers.add("safeOutput");
                blockStr = `safeOutput(${compileExpr(ast.expr)}, b${bodyValue})`;
            }
            else {
                this.helpers.add("safeOutput");
                blockStr = `safeOutput(${compileExpr(ast.expr)})`;
            }
            this.insertBlock(blockStr, block, ctx);
            return block.varName;
        }
        compileTIfBranch(content, block, ctx) {
            this.target.indentLevel++;
            let childN = block.children.length;
            this.compileAST(content, createContext(ctx, { block, index: ctx.index }));
            if (block.children.length > childN) {
                // we have some content => need to insert an anchor at correct index
                this.insertAnchor(block, childN);
            }
            this.target.indentLevel--;
        }
        compileTIf(ast, ctx, nextNode) {
            let { block, forceNewBlock } = ctx;
            const codeIdx = this.target.code.length;
            const isNewBlock = !block || (block.type !== "multi" && forceNewBlock);
            if (block) {
                block.hasDynamicChildren = true;
            }
            if (!block || (block.type !== "multi" && forceNewBlock)) {
                block = this.createBlock(block, "multi", ctx);
            }
            this.addLine(`if (${compileExpr(ast.condition)}) {`);
            this.compileTIfBranch(ast.content, block, ctx);
            if (ast.tElif) {
                for (let clause of ast.tElif) {
                    this.addLine(`} else if (${compileExpr(clause.condition)}) {`);
                    this.compileTIfBranch(clause.content, block, ctx);
                }
            }
            if (ast.tElse) {
                this.addLine(`} else {`);
                this.compileTIfBranch(ast.tElse, block, ctx);
            }
            this.addLine("}");
            if (isNewBlock) {
                // note: this part is duplicated from end of compiledomnode:
                if (block.children.length) {
                    const code = this.target.code;
                    const children = block.children.slice();
                    let current = children.shift();
                    for (let i = codeIdx; i < code.length; i++) {
                        if (code[i].trimStart().startsWith(`const ${current.varName} `)) {
                            code[i] = code[i].replace(`const ${current.varName}`, current.varName);
                            current = children.shift();
                            if (!current)
                                break;
                        }
                    }
                    this.addLine(`let ${block.children.map((c) => c.varName).join(", ")};`, codeIdx);
                }
                // note: this part is duplicated from end of compilemulti:
                const args = block.children.map((c) => c.varName).join(", ");
                this.insertBlock(`multi([${args}])`, block, ctx);
            }
            return block.varName;
        }
        compileTForeach(ast, ctx) {
            let { block } = ctx;
            if (block) {
                this.insertAnchor(block);
            }
            block = this.createBlock(block, "list", ctx);
            this.target.loopLevel++;
            const loopVar = `i${this.target.loopLevel}`;
            this.addLine(`ctx = Object.create(ctx);`);
            const vals = `v_block${block.id}`;
            const keys = `k_block${block.id}`;
            const l = `l_block${block.id}`;
            const c = `c_block${block.id}`;
            this.helpers.add("prepareList");
            this.define(`[${keys}, ${vals}, ${l}, ${c}]`, `prepareList(${compileExpr(ast.collection)});`);
            // Throw errors on duplicate keys in dev mode
            if (this.dev) {
                this.define(`keys${block.id}`, `new Set()`);
            }
            this.addLine(`for (let ${loopVar} = 0; ${loopVar} < ${l}; ${loopVar}++) {`);
            this.target.indentLevel++;
            this.addLine(`ctx[\`${ast.elem}\`] = ${keys}[${loopVar}];`);
            if (!ast.hasNoFirst) {
                this.addLine(`ctx[\`${ast.elem}_first\`] = ${loopVar} === 0;`);
            }
            if (!ast.hasNoLast) {
                this.addLine(`ctx[\`${ast.elem}_last\`] = ${loopVar} === ${keys}.length - 1;`);
            }
            if (!ast.hasNoIndex) {
                this.addLine(`ctx[\`${ast.elem}_index\`] = ${loopVar};`);
            }
            if (!ast.hasNoValue) {
                this.addLine(`ctx[\`${ast.elem}_value\`] = ${vals}[${loopVar}];`);
            }
            this.define(`key${this.target.loopLevel}`, ast.key ? compileExpr(ast.key) : loopVar);
            if (this.dev) {
                // Throw error on duplicate keys in dev mode
                this.helpers.add("OwlError");
                this.addLine(`if (keys${block.id}.has(String(key${this.target.loopLevel}))) { throw new OwlError(\`Got duplicate key in t-foreach: \${key${this.target.loopLevel}}\`)}`);
                this.addLine(`keys${block.id}.add(String(key${this.target.loopLevel}));`);
            }
            let id;
            if (ast.memo) {
                this.target.hasCache = true;
                id = generateId();
                this.define(`memo${id}`, compileExpr(ast.memo));
                this.define(`vnode${id}`, `cache[key${this.target.loopLevel}];`);
                this.addLine(`if (vnode${id}) {`);
                this.target.indentLevel++;
                this.addLine(`if (shallowEqual(vnode${id}.memo, memo${id})) {`);
                this.target.indentLevel++;
                this.addLine(`${c}[${loopVar}] = vnode${id};`);
                this.addLine(`nextCache[key${this.target.loopLevel}] = vnode${id};`);
                this.addLine(`continue;`);
                this.target.indentLevel--;
                this.addLine("}");
                this.target.indentLevel--;
                this.addLine("}");
            }
            const subCtx = createContext(ctx, { block, index: loopVar });
            this.compileAST(ast.body, subCtx);
            if (ast.memo) {
                this.addLine(`nextCache[key${this.target.loopLevel}] = Object.assign(${c}[${loopVar}], {memo: memo${id}});`);
            }
            this.target.indentLevel--;
            this.target.loopLevel--;
            this.addLine(`}`);
            if (!ctx.isLast) {
                this.addLine(`ctx = ctx.__proto__;`);
            }
            this.insertBlock("l", block, ctx);
            return block.varName;
        }
        compileTKey(ast, ctx) {
            const tKeyExpr = generateId("tKey_");
            this.define(tKeyExpr, compileExpr(ast.expr));
            ctx = createContext(ctx, {
                tKeyExpr,
                block: ctx.block,
                index: ctx.index,
            });
            return this.compileAST(ast.content, ctx);
        }
        compileMulti(ast, ctx) {
            let { block, forceNewBlock } = ctx;
            const isNewBlock = !block || forceNewBlock;
            let codeIdx = this.target.code.length;
            if (isNewBlock) {
                const n = ast.content.filter((c) => c.type !== 6 /* TSet */).length;
                let result = null;
                if (n <= 1) {
                    for (let child of ast.content) {
                        const blockName = this.compileAST(child, ctx);
                        result = result || blockName;
                    }
                    return result;
                }
                block = this.createBlock(block, "multi", ctx);
            }
            let index = 0;
            for (let i = 0, l = ast.content.length; i < l; i++) {
                const child = ast.content[i];
                const isTSet = child.type === 6 /* TSet */;
                const subCtx = createContext(ctx, {
                    block,
                    index,
                    forceNewBlock: !isTSet,
                    isLast: ctx.isLast && i === l - 1,
                });
                this.compileAST(child, subCtx);
                if (!isTSet) {
                    index++;
                }
            }
            if (isNewBlock) {
                if (block.hasDynamicChildren && block.children.length) {
                    const code = this.target.code;
                    const children = block.children.slice();
                    let current = children.shift();
                    for (let i = codeIdx; i < code.length; i++) {
                        if (code[i].trimStart().startsWith(`const ${current.varName} `)) {
                            code[i] = code[i].replace(`const ${current.varName}`, current.varName);
                            current = children.shift();
                            if (!current)
                                break;
                        }
                    }
                    this.addLine(`let ${block.children.map((c) => c.varName).join(", ")};`, codeIdx);
                }
                const args = block.children.map((c) => c.varName).join(", ");
                this.insertBlock(`multi([${args}])`, block, ctx);
            }
            return block.varName;
        }
        compileTCall(ast, ctx) {
            let { block, forceNewBlock } = ctx;
            let ctxVar = ctx.ctxVar || "ctx";
            if (ast.context) {
                ctxVar = generateId("ctx");
                this.addLine(`let ${ctxVar} = ${compileExpr(ast.context)};`);
            }
            const isDynamic = INTERP_REGEXP.test(ast.name);
            const subTemplate = isDynamic ? interpolate(ast.name) : "`" + ast.name + "`";
            if (block && !forceNewBlock) {
                this.insertAnchor(block);
            }
            block = this.createBlock(block, "multi", ctx);
            if (ast.body) {
                this.addLine(`${ctxVar} = Object.create(${ctxVar});`);
                this.addLine(`${ctxVar}[isBoundary] = 1;`);
                this.helpers.add("isBoundary");
                const subCtx = createContext(ctx, { ctxVar });
                const bl = this.compileMulti({ type: 3 /* Multi */, content: ast.body }, subCtx);
                if (bl) {
                    this.helpers.add("zero");
                    this.addLine(`${ctxVar}[zero] = ${bl};`);
                }
            }
            const key = `key + \`${this.generateComponentKey()}\``;
            if (isDynamic) {
                const templateVar = generateId("template");
                if (!this.staticDefs.find((d) => d.id === "call")) {
                    this.staticDefs.push({ id: "call", expr: `app.callTemplate.bind(app)` });
                }
                this.define(templateVar, subTemplate);
                this.insertBlock(`call(this, ${templateVar}, ${ctxVar}, node, ${key})`, block, {
                    ...ctx,
                    forceNewBlock: !block,
                });
            }
            else {
                const id = generateId(`callTemplate_`);
                this.staticDefs.push({ id, expr: `app.getTemplate(${subTemplate})` });
                this.insertBlock(`${id}.call(this, ${ctxVar}, node, ${key})`, block, {
                    ...ctx,
                    forceNewBlock: !block,
                });
            }
            if (ast.body && !ctx.isLast) {
                this.addLine(`${ctxVar} = ${ctxVar}.__proto__;`);
            }
            return block.varName;
        }
        compileTCallBlock(ast, ctx) {
            let { block, forceNewBlock } = ctx;
            if (block) {
                if (!forceNewBlock) {
                    this.insertAnchor(block);
                }
            }
            block = this.createBlock(block, "multi", ctx);
            this.insertBlock(compileExpr(ast.name), block, { ...ctx, forceNewBlock: !block });
            return block.varName;
        }
        compileTSet(ast, ctx) {
            this.target.shouldProtectScope = true;
            this.helpers.add("isBoundary").add("withDefault");
            const expr = ast.value ? compileExpr(ast.value || "") : "null";
            if (ast.body) {
                this.helpers.add("LazyValue");
                const bodyAst = { type: 3 /* Multi */, content: ast.body };
                const name = this.compileInNewTarget("value", bodyAst, ctx);
                let key = this.target.currentKey(ctx);
                let value = `new LazyValue(${name}, ctx, this, node, ${key})`;
                value = ast.value ? (value ? `withDefault(${expr}, ${value})` : expr) : value;
                this.addLine(`ctx[\`${ast.name}\`] = ${value};`);
            }
            else {
                let value;
                if (ast.defaultValue) {
                    const defaultValue = ctx.translate ? this.translate(ast.defaultValue) : ast.defaultValue;
                    if (ast.value) {
                        value = `withDefault(${expr}, \`${defaultValue}\`)`;
                    }
                    else {
                        value = `\`${defaultValue}\``;
                    }
                }
                else {
                    value = expr;
                }
                this.helpers.add("setContextValue");
                this.addLine(`setContextValue(${ctx.ctxVar || "ctx"}, "${ast.name}", ${value});`);
            }
            return null;
        }
        generateComponentKey() {
            const parts = [generateId("__")];
            for (let i = 0; i < this.target.loopLevel; i++) {
                parts.push(`\${key${i + 1}}`);
            }
            return parts.join("__");
        }
        /**
         * Formats a prop name and value into a string suitable to be inserted in the
         * generated code. For example:
         *
         * Name              Value            Result
         * ---------------------------------------------------------
         * "number"          "state"          "number: ctx['state']"
         * "something"       ""               "something: undefined"
         * "some-prop"       "state"          "'some-prop': ctx['state']"
         * "onClick.bind"    "onClick"        "onClick: bind(ctx, ctx['onClick'])"
         */
        formatProp(name, value) {
            value = this.captureExpression(value);
            if (name.includes(".")) {
                let [_name, suffix] = name.split(".");
                name = _name;
                switch (suffix) {
                    case "bind":
                        value = `(${value}).bind(this)`;
                        break;
                    case "alike":
                        break;
                    default:
                        throw new OwlError("Invalid prop suffix");
                }
            }
            name = /^[a-z_]+$/i.test(name) ? name : `'${name}'`;
            return `${name}: ${value || undefined}`;
        }
        formatPropObject(obj) {
            return Object.entries(obj).map(([k, v]) => this.formatProp(k, v));
        }
        getPropString(props, dynProps) {
            let propString = `{${props.join(",")}}`;
            if (dynProps) {
                propString = `Object.assign({}, ${compileExpr(dynProps)}${props.length ? ", " + propString : ""})`;
            }
            return propString;
        }
        compileComponent(ast, ctx) {
            let { block } = ctx;
            // props
            const hasSlotsProp = "slots" in (ast.props || {});
            const props = ast.props ? this.formatPropObject(ast.props) : [];
            // slots
            let slotDef = "";
            if (ast.slots) {
                let ctxStr = "ctx";
                if (this.target.loopLevel || !this.hasSafeContext) {
                    ctxStr = generateId("ctx");
                    this.helpers.add("capture");
                    this.define(ctxStr, `capture(ctx)`);
                }
                let slotStr = [];
                for (let slotName in ast.slots) {
                    const slotAst = ast.slots[slotName];
                    const params = [];
                    if (slotAst.content) {
                        const name = this.compileInNewTarget("slot", slotAst.content, ctx, slotAst.on);
                        params.push(`__render: ${name}.bind(this), __ctx: ${ctxStr}`);
                    }
                    const scope = ast.slots[slotName].scope;
                    if (scope) {
                        params.push(`__scope: "${scope}"`);
                    }
                    if (ast.slots[slotName].attrs) {
                        params.push(...this.formatPropObject(ast.slots[slotName].attrs));
                    }
                    const slotInfo = `{${params.join(", ")}}`;
                    slotStr.push(`'${slotName}': ${slotInfo}`);
                }
                slotDef = `{${slotStr.join(", ")}}`;
            }
            if (slotDef && !(ast.dynamicProps || hasSlotsProp)) {
                this.helpers.add("markRaw");
                props.push(`slots: markRaw(${slotDef})`);
            }
            let propString = this.getPropString(props, ast.dynamicProps);
            let propVar;
            if ((slotDef && (ast.dynamicProps || hasSlotsProp)) || this.dev) {
                propVar = generateId("props");
                this.define(propVar, propString);
                propString = propVar;
            }
            if (slotDef && (ast.dynamicProps || hasSlotsProp)) {
                this.helpers.add("markRaw");
                this.addLine(`${propVar}.slots = markRaw(Object.assign(${slotDef}, ${propVar}.slots))`);
            }
            // cmap key
            const key = this.generateComponentKey();
            let expr;
            if (ast.isDynamic) {
                expr = generateId("Comp");
                this.define(expr, compileExpr(ast.name));
            }
            else {
                expr = `\`${ast.name}\``;
            }
            if (this.dev) {
                this.addLine(`helpers.validateProps(${expr}, ${propVar}, this);`);
            }
            if (block && (ctx.forceNewBlock === false || ctx.tKeyExpr)) {
                // todo: check the forcenewblock condition
                this.insertAnchor(block);
            }
            let keyArg = `key + \`${key}\``;
            if (ctx.tKeyExpr) {
                keyArg = `${ctx.tKeyExpr} + ${keyArg}`;
            }
            let id = generateId("comp");
            const propList = [];
            for (let p in ast.props || {}) {
                let [name, suffix] = p.split(".");
                if (!suffix) {
                    propList.push(`"${name}"`);
                }
            }
            this.staticDefs.push({
                id,
                expr: `app.createComponent(${ast.isDynamic ? null : expr}, ${!ast.isDynamic}, ${!!ast.slots}, ${!!ast.dynamicProps}, [${propList}])`,
            });
            if (ast.isDynamic) {
                // If the component class changes, this can cause delayed renders to go
                // through if the key doesn't change. Use the component name for now.
                // This means that two component classes with the same name isn't supported
                // in t-component. We can generate a unique id per class later if needed.
                keyArg = `(${expr}).name + ${keyArg}`;
            }
            let blockExpr = `${id}(${propString}, ${keyArg}, node, this, ${ast.isDynamic ? expr : null})`;
            if (ast.isDynamic) {
                blockExpr = `toggler(${expr}, ${blockExpr})`;
            }
            // event handling
            if (ast.on) {
                blockExpr = this.wrapWithEventCatcher(blockExpr, ast.on);
            }
            block = this.createBlock(block, "multi", ctx);
            this.insertBlock(blockExpr, block, ctx);
            return block.varName;
        }
        wrapWithEventCatcher(expr, on) {
            this.helpers.add("createCatcher");
            let name = generateId("catcher");
            let spec = {};
            let handlers = [];
            for (let ev in on) {
                let handlerId = generateId("hdlr");
                let idx = handlers.push(handlerId) - 1;
                spec[ev] = idx;
                const handler = this.generateHandlerCode(ev, on[ev]);
                this.define(handlerId, handler);
            }
            this.staticDefs.push({ id: name, expr: `createCatcher(${JSON.stringify(spec)})` });
            return `${name}(${expr}, [${handlers.join(",")}])`;
        }
        compileTSlot(ast, ctx) {
            this.helpers.add("callSlot");
            let { block } = ctx;
            let blockString;
            let slotName;
            let dynamic = false;
            let isMultiple = false;
            if (ast.name.match(INTERP_REGEXP)) {
                dynamic = true;
                isMultiple = true;
                slotName = interpolate(ast.name);
            }
            else {
                slotName = "'" + ast.name + "'";
                isMultiple = isMultiple || this.slotNames.has(ast.name);
                this.slotNames.add(ast.name);
            }
            const dynProps = ast.attrs ? ast.attrs["t-props"] : null;
            if (ast.attrs) {
                delete ast.attrs["t-props"];
            }
            let key = this.target.loopLevel ? `key${this.target.loopLevel}` : "key";
            if (isMultiple) {
                key = `${key} + \`${this.generateComponentKey()}\``;
            }
            const props = ast.attrs ? this.formatPropObject(ast.attrs) : [];
            const scope = this.getPropString(props, dynProps);
            if (ast.defaultContent) {
                const name = this.compileInNewTarget("defaultContent", ast.defaultContent, ctx);
                blockString = `callSlot(ctx, node, ${key}, ${slotName}, ${dynamic}, ${scope}, ${name}.bind(this))`;
            }
            else {
                if (dynamic) {
                    let name = generateId("slot");
                    this.define(name, slotName);
                    blockString = `toggler(${name}, callSlot(ctx, node, ${key}, ${name}, ${dynamic}, ${scope}))`;
                }
                else {
                    blockString = `callSlot(ctx, node, ${key}, ${slotName}, ${dynamic}, ${scope})`;
                }
            }
            // event handling
            if (ast.on) {
                blockString = this.wrapWithEventCatcher(blockString, ast.on);
            }
            if (block) {
                this.insertAnchor(block);
            }
            block = this.createBlock(block, "multi", ctx);
            this.insertBlock(blockString, block, { ...ctx, forceNewBlock: false });
            return block.varName;
        }
        compileTTranslation(ast, ctx) {
            if (ast.content) {
                return this.compileAST(ast.content, Object.assign({}, ctx, { translate: false }));
            }
            return null;
        }
        compileTPortal(ast, ctx) {
            if (!this.staticDefs.find((d) => d.id === "Portal")) {
                this.staticDefs.push({ id: "Portal", expr: `app.Portal` });
            }
            let { block } = ctx;
            const name = this.compileInNewTarget("slot", ast.content, ctx);
            const key = this.generateComponentKey();
            let ctxStr = "ctx";
            if (this.target.loopLevel || !this.hasSafeContext) {
                ctxStr = generateId("ctx");
                this.helpers.add("capture");
                this.define(ctxStr, `capture(ctx)`);
            }
            let id = generateId("comp");
            this.staticDefs.push({
                id,
                expr: `app.createComponent(null, false, true, false, false)`,
            });
            const target = compileExpr(ast.target);
            const blockString = `${id}({target: ${target},slots: {'default': {__render: ${name}.bind(this), __ctx: ${ctxStr}}}}, key + \`${key}\`, node, ctx, Portal)`;
            if (block) {
                this.insertAnchor(block);
            }
            block = this.createBlock(block, "multi", ctx);
            this.insertBlock(blockString, block, { ...ctx, forceNewBlock: false });
            return block.varName;
        }
    }

    // -----------------------------------------------------------------------------
    // Parser
    // -----------------------------------------------------------------------------
    const cache = new WeakMap();
    function parse(xml) {
        if (typeof xml === "string") {
            const elem = parseXML(`<t>${xml}</t>`).firstChild;
            return _parse(elem);
        }
        let ast = cache.get(xml);
        if (!ast) {
            // we clone here the xml to prevent modifying it in place
            ast = _parse(xml.cloneNode(true));
            cache.set(xml, ast);
        }
        return ast;
    }
    function _parse(xml) {
        normalizeXML(xml);
        const ctx = { inPreTag: false };
        return parseNode(xml, ctx) || { type: 0 /* Text */, value: "" };
    }
    function parseNode(node, ctx) {
        if (!(node instanceof Element)) {
            return parseTextCommentNode(node, ctx);
        }
        return (parseTDebugLog(node, ctx) ||
            parseTForEach(node, ctx) ||
            parseTIf(node, ctx) ||
            parseTPortal(node, ctx) ||
            parseTCall(node, ctx) ||
            parseTCallBlock(node) ||
            parseTEscNode(node, ctx) ||
            parseTOutNode(node, ctx) ||
            parseTKey(node, ctx) ||
            parseTTranslation(node, ctx) ||
            parseTSlot(node, ctx) ||
            parseComponent(node, ctx) ||
            parseDOMNode(node, ctx) ||
            parseTSetNode(node, ctx) ||
            parseTNode(node, ctx));
    }
    // -----------------------------------------------------------------------------
    // <t /> tag
    // -----------------------------------------------------------------------------
    function parseTNode(node, ctx) {
        if (node.tagName !== "t") {
            return null;
        }
        return parseChildNodes(node, ctx);
    }
    // -----------------------------------------------------------------------------
    // Text and Comment Nodes
    // -----------------------------------------------------------------------------
    const lineBreakRE = /[\r\n]/;
    function parseTextCommentNode(node, ctx) {
        if (node.nodeType === Node.TEXT_NODE) {
            let value = node.textContent || "";
            if (!ctx.inPreTag && lineBreakRE.test(value) && !value.trim()) {
                return null;
            }
            return { type: 0 /* Text */, value };
        }
        else if (node.nodeType === Node.COMMENT_NODE) {
            return { type: 1 /* Comment */, value: node.textContent || "" };
        }
        return null;
    }
    // -----------------------------------------------------------------------------
    // debugging
    // -----------------------------------------------------------------------------
    function parseTDebugLog(node, ctx) {
        if (node.hasAttribute("t-debug")) {
            node.removeAttribute("t-debug");
            return {
                type: 12 /* TDebug */,
                content: parseNode(node, ctx),
            };
        }
        if (node.hasAttribute("t-log")) {
            const expr = node.getAttribute("t-log");
            node.removeAttribute("t-log");
            return {
                type: 13 /* TLog */,
                expr,
                content: parseNode(node, ctx),
            };
        }
        return null;
    }
    // -----------------------------------------------------------------------------
    // Regular dom node
    // -----------------------------------------------------------------------------
    const hasDotAtTheEnd = /\.[\w_]+\s*$/;
    const hasBracketsAtTheEnd = /\[[^\[]+\]\s*$/;
    const ROOT_SVG_TAGS = new Set(["svg", "g", "path"]);
    function parseDOMNode(node, ctx) {
        const { tagName } = node;
        const dynamicTag = node.getAttribute("t-tag");
        node.removeAttribute("t-tag");
        if (tagName === "t" && !dynamicTag) {
            return null;
        }
        if (tagName.startsWith("block-")) {
            throw new OwlError(`Invalid tag name: '${tagName}'`);
        }
        ctx = Object.assign({}, ctx);
        if (tagName === "pre") {
            ctx.inPreTag = true;
        }
        let ns = !ctx.nameSpace && ROOT_SVG_TAGS.has(tagName) ? "http://www.w3.org/2000/svg" : null;
        const ref = node.getAttribute("t-ref");
        node.removeAttribute("t-ref");
        const nodeAttrsNames = node.getAttributeNames();
        let attrs = null;
        let on = null;
        let model = null;
        for (let attr of nodeAttrsNames) {
            const value = node.getAttribute(attr);
            if (attr === "t-on" || attr === "t-on-") {
                throw new OwlError("Missing event name with t-on directive");
            }
            if (attr.startsWith("t-on-")) {
                on = on || {};
                on[attr.slice(5)] = value;
            }
            else if (attr.startsWith("t-model")) {
                if (!["input", "select", "textarea"].includes(tagName)) {
                    throw new OwlError("The t-model directive only works with <input>, <textarea> and <select>");
                }
                let baseExpr, expr;
                if (hasDotAtTheEnd.test(value)) {
                    const index = value.lastIndexOf(".");
                    baseExpr = value.slice(0, index);
                    expr = `'${value.slice(index + 1)}'`;
                }
                else if (hasBracketsAtTheEnd.test(value)) {
                    const index = value.lastIndexOf("[");
                    baseExpr = value.slice(0, index);
                    expr = value.slice(index + 1, -1);
                }
                else {
                    throw new OwlError(`Invalid t-model expression: "${value}" (it should be assignable)`);
                }
                const typeAttr = node.getAttribute("type");
                const isInput = tagName === "input";
                const isSelect = tagName === "select";
                const isCheckboxInput = isInput && typeAttr === "checkbox";
                const isRadioInput = isInput && typeAttr === "radio";
                const hasLazyMod = attr.includes(".lazy");
                const hasNumberMod = attr.includes(".number");
                const hasTrimMod = attr.includes(".trim");
                const eventType = isRadioInput ? "click" : isSelect || hasLazyMod ? "change" : "input";
                model = {
                    baseExpr,
                    expr,
                    targetAttr: isCheckboxInput ? "checked" : "value",
                    specialInitTargetAttr: isRadioInput ? "checked" : null,
                    eventType,
                    hasDynamicChildren: false,
                    shouldTrim: hasTrimMod,
                    shouldNumberize: hasNumberMod,
                };
                if (isSelect) {
                    // don't pollute the original ctx
                    ctx = Object.assign({}, ctx);
                    ctx.tModelInfo = model;
                }
            }
            else if (attr.startsWith("block-")) {
                throw new OwlError(`Invalid attribute: '${attr}'`);
            }
            else if (attr === "xmlns") {
                ns = value;
            }
            else if (attr !== "t-name") {
                if (attr.startsWith("t-") && !attr.startsWith("t-att")) {
                    throw new OwlError(`Unknown QWeb directive: '${attr}'`);
                }
                const tModel = ctx.tModelInfo;
                if (tModel && ["t-att-value", "t-attf-value"].includes(attr)) {
                    tModel.hasDynamicChildren = true;
                }
                attrs = attrs || {};
                attrs[attr] = value;
            }
        }
        if (ns) {
            ctx.nameSpace = ns;
        }
        const children = parseChildren(node, ctx);
        return {
            type: 2 /* DomNode */,
            tag: tagName,
            dynamicTag,
            attrs,
            on,
            ref,
            content: children,
            model,
            ns,
        };
    }
    // -----------------------------------------------------------------------------
    // t-esc
    // -----------------------------------------------------------------------------
    function parseTEscNode(node, ctx) {
        if (!node.hasAttribute("t-esc")) {
            return null;
        }
        const escValue = node.getAttribute("t-esc");
        node.removeAttribute("t-esc");
        const tesc = {
            type: 4 /* TEsc */,
            expr: escValue,
            defaultValue: node.textContent || "",
        };
        let ref = node.getAttribute("t-ref");
        node.removeAttribute("t-ref");
        const ast = parseNode(node, ctx);
        if (!ast) {
            return tesc;
        }
        if (ast.type === 2 /* DomNode */) {
            return {
                ...ast,
                ref,
                content: [tesc],
            };
        }
        return tesc;
    }
    // -----------------------------------------------------------------------------
    // t-out
    // -----------------------------------------------------------------------------
    function parseTOutNode(node, ctx) {
        if (!node.hasAttribute("t-out") && !node.hasAttribute("t-raw")) {
            return null;
        }
        if (node.hasAttribute("t-raw")) {
            console.warn(`t-raw has been deprecated in favor of t-out. If the value to render is not wrapped by the "markup" function, it will be escaped`);
        }
        const expr = (node.getAttribute("t-out") || node.getAttribute("t-raw"));
        node.removeAttribute("t-out");
        node.removeAttribute("t-raw");
        const tOut = { type: 8 /* TOut */, expr, body: null };
        const ref = node.getAttribute("t-ref");
        node.removeAttribute("t-ref");
        const ast = parseNode(node, ctx);
        if (!ast) {
            return tOut;
        }
        if (ast.type === 2 /* DomNode */) {
            tOut.body = ast.content.length ? ast.content : null;
            return {
                ...ast,
                ref,
                content: [tOut],
            };
        }
        return tOut;
    }
    // -----------------------------------------------------------------------------
    // t-foreach and t-key
    // -----------------------------------------------------------------------------
    function parseTForEach(node, ctx) {
        if (!node.hasAttribute("t-foreach")) {
            return null;
        }
        const html = node.outerHTML;
        const collection = node.getAttribute("t-foreach");
        node.removeAttribute("t-foreach");
        const elem = node.getAttribute("t-as") || "";
        node.removeAttribute("t-as");
        const key = node.getAttribute("t-key");
        if (!key) {
            throw new OwlError(`"Directive t-foreach should always be used with a t-key!" (expression: t-foreach="${collection}" t-as="${elem}")`);
        }
        node.removeAttribute("t-key");
        const memo = node.getAttribute("t-memo") || "";
        node.removeAttribute("t-memo");
        const body = parseNode(node, ctx);
        if (!body) {
            return null;
        }
        const hasNoTCall = !html.includes("t-call");
        const hasNoFirst = hasNoTCall && !html.includes(`${elem}_first`);
        const hasNoLast = hasNoTCall && !html.includes(`${elem}_last`);
        const hasNoIndex = hasNoTCall && !html.includes(`${elem}_index`);
        const hasNoValue = hasNoTCall && !html.includes(`${elem}_value`);
        return {
            type: 9 /* TForEach */,
            collection,
            elem,
            body,
            memo,
            key,
            hasNoFirst,
            hasNoLast,
            hasNoIndex,
            hasNoValue,
        };
    }
    function parseTKey(node, ctx) {
        if (!node.hasAttribute("t-key")) {
            return null;
        }
        const key = node.getAttribute("t-key");
        node.removeAttribute("t-key");
        const body = parseNode(node, ctx);
        if (!body) {
            return null;
        }
        return { type: 10 /* TKey */, expr: key, content: body };
    }
    // -----------------------------------------------------------------------------
    // t-call
    // -----------------------------------------------------------------------------
    function parseTCall(node, ctx) {
        if (!node.hasAttribute("t-call")) {
            return null;
        }
        const subTemplate = node.getAttribute("t-call");
        const context = node.getAttribute("t-call-context");
        node.removeAttribute("t-call");
        node.removeAttribute("t-call-context");
        if (node.tagName !== "t") {
            const ast = parseNode(node, ctx);
            const tcall = { type: 7 /* TCall */, name: subTemplate, body: null, context };
            if (ast && ast.type === 2 /* DomNode */) {
                ast.content = [tcall];
                return ast;
            }
            if (ast && ast.type === 11 /* TComponent */) {
                return {
                    ...ast,
                    slots: { default: { content: tcall, scope: null, on: null, attrs: null } },
                };
            }
        }
        const body = parseChildren(node, ctx);
        return {
            type: 7 /* TCall */,
            name: subTemplate,
            body: body.length ? body : null,
            context,
        };
    }
    // -----------------------------------------------------------------------------
    // t-call-block
    // -----------------------------------------------------------------------------
    function parseTCallBlock(node, ctx) {
        if (!node.hasAttribute("t-call-block")) {
            return null;
        }
        const name = node.getAttribute("t-call-block");
        return {
            type: 15 /* TCallBlock */,
            name,
        };
    }
    // -----------------------------------------------------------------------------
    // t-if
    // -----------------------------------------------------------------------------
    function parseTIf(node, ctx) {
        if (!node.hasAttribute("t-if")) {
            return null;
        }
        const condition = node.getAttribute("t-if");
        node.removeAttribute("t-if");
        const content = parseNode(node, ctx) || { type: 0 /* Text */, value: "" };
        let nextElement = node.nextElementSibling;
        // t-elifs
        const tElifs = [];
        while (nextElement && nextElement.hasAttribute("t-elif")) {
            const condition = nextElement.getAttribute("t-elif");
            nextElement.removeAttribute("t-elif");
            const tElif = parseNode(nextElement, ctx);
            const next = nextElement.nextElementSibling;
            nextElement.remove();
            nextElement = next;
            if (tElif) {
                tElifs.push({ condition, content: tElif });
            }
        }
        // t-else
        let tElse = null;
        if (nextElement && nextElement.hasAttribute("t-else")) {
            nextElement.removeAttribute("t-else");
            tElse = parseNode(nextElement, ctx);
            nextElement.remove();
        }
        return {
            type: 5 /* TIf */,
            condition,
            content,
            tElif: tElifs.length ? tElifs : null,
            tElse,
        };
    }
    // -----------------------------------------------------------------------------
    // t-set directive
    // -----------------------------------------------------------------------------
    function parseTSetNode(node, ctx) {
        if (!node.hasAttribute("t-set")) {
            return null;
        }
        const name = node.getAttribute("t-set");
        const value = node.getAttribute("t-value") || null;
        const defaultValue = node.innerHTML === node.textContent ? node.textContent || null : null;
        let body = null;
        if (node.textContent !== node.innerHTML) {
            body = parseChildren(node, ctx);
        }
        return { type: 6 /* TSet */, name, value, defaultValue, body };
    }
    // -----------------------------------------------------------------------------
    // Components
    // -----------------------------------------------------------------------------
    // Error messages when trying to use an unsupported directive on a component
    const directiveErrorMap = new Map([
        [
            "t-ref",
            "t-ref is no longer supported on components. Consider exposing only the public part of the component's API through a callback prop.",
        ],
        ["t-att", "t-att makes no sense on component: props are already treated as expressions"],
        [
            "t-attf",
            "t-attf is not supported on components: use template strings for string interpolation in props",
        ],
    ]);
    function parseComponent(node, ctx) {
        let name = node.tagName;
        const firstLetter = name[0];
        let isDynamic = node.hasAttribute("t-component");
        if (isDynamic && name !== "t") {
            throw new OwlError(`Directive 't-component' can only be used on <t> nodes (used on a <${name}>)`);
        }
        if (!(firstLetter === firstLetter.toUpperCase() || isDynamic)) {
            return null;
        }
        if (isDynamic) {
            name = node.getAttribute("t-component");
            node.removeAttribute("t-component");
        }
        const dynamicProps = node.getAttribute("t-props");
        node.removeAttribute("t-props");
        const defaultSlotScope = node.getAttribute("t-slot-scope");
        node.removeAttribute("t-slot-scope");
        let on = null;
        let props = null;
        for (let name of node.getAttributeNames()) {
            const value = node.getAttribute(name);
            if (name.startsWith("t-")) {
                if (name.startsWith("t-on-")) {
                    on = on || {};
                    on[name.slice(5)] = value;
                }
                else {
                    const message = directiveErrorMap.get(name.split("-").slice(0, 2).join("-"));
                    throw new OwlError(message || `unsupported directive on Component: ${name}`);
                }
            }
            else {
                props = props || {};
                props[name] = value;
            }
        }
        let slots = null;
        if (node.hasChildNodes()) {
            const clone = node.cloneNode(true);
            // named slots
            const slotNodes = Array.from(clone.querySelectorAll("[t-set-slot]"));
            for (let slotNode of slotNodes) {
                if (slotNode.tagName !== "t") {
                    throw new OwlError(`Directive 't-set-slot' can only be used on <t> nodes (used on a <${slotNode.tagName}>)`);
                }
                const name = slotNode.getAttribute("t-set-slot");
                // check if this is defined in a sub component (in which case it should
                // be ignored)
                let el = slotNode.parentElement;
                let isInSubComponent = false;
                while (el !== clone) {
                    if (el.hasAttribute("t-component") || el.tagName[0] === el.tagName[0].toUpperCase()) {
                        isInSubComponent = true;
                        break;
                    }
                    el = el.parentElement;
                }
                if (isInSubComponent) {
                    continue;
                }
                slotNode.removeAttribute("t-set-slot");
                slotNode.remove();
                const slotAst = parseNode(slotNode, ctx);
                let on = null;
                let attrs = null;
                let scope = null;
                for (let attributeName of slotNode.getAttributeNames()) {
                    const value = slotNode.getAttribute(attributeName);
                    if (attributeName === "t-slot-scope") {
                        scope = value;
                        continue;
                    }
                    else if (attributeName.startsWith("t-on-")) {
                        on = on || {};
                        on[attributeName.slice(5)] = value;
                    }
                    else {
                        attrs = attrs || {};
                        attrs[attributeName] = value;
                    }
                }
                slots = slots || {};
                slots[name] = { content: slotAst, on, attrs, scope };
            }
            // default slot
            const defaultContent = parseChildNodes(clone, ctx);
            slots = slots || {};
            // t-set-slot="default" has priority over content
            if (defaultContent && !slots.default) {
                slots.default = { content: defaultContent, on, attrs: null, scope: defaultSlotScope };
            }
        }
        return { type: 11 /* TComponent */, name, isDynamic, dynamicProps, props, slots, on };
    }
    // -----------------------------------------------------------------------------
    // Slots
    // -----------------------------------------------------------------------------
    function parseTSlot(node, ctx) {
        if (!node.hasAttribute("t-slot")) {
            return null;
        }
        const name = node.getAttribute("t-slot");
        node.removeAttribute("t-slot");
        let attrs = null;
        let on = null;
        for (let attributeName of node.getAttributeNames()) {
            const value = node.getAttribute(attributeName);
            if (attributeName.startsWith("t-on-")) {
                on = on || {};
                on[attributeName.slice(5)] = value;
            }
            else {
                attrs = attrs || {};
                attrs[attributeName] = value;
            }
        }
        return {
            type: 14 /* TSlot */,
            name,
            attrs,
            on,
            defaultContent: parseChildNodes(node, ctx),
        };
    }
    function parseTTranslation(node, ctx) {
        if (node.getAttribute("t-translation") !== "off") {
            return null;
        }
        node.removeAttribute("t-translation");
        return {
            type: 16 /* TTranslation */,
            content: parseNode(node, ctx),
        };
    }
    // -----------------------------------------------------------------------------
    // Portal
    // -----------------------------------------------------------------------------
    function parseTPortal(node, ctx) {
        if (!node.hasAttribute("t-portal")) {
            return null;
        }
        const target = node.getAttribute("t-portal");
        node.removeAttribute("t-portal");
        const content = parseNode(node, ctx);
        if (!content) {
            return {
                type: 0 /* Text */,
                value: "",
            };
        }
        return {
            type: 17 /* TPortal */,
            target,
            content,
        };
    }
    // -----------------------------------------------------------------------------
    // helpers
    // -----------------------------------------------------------------------------
    /**
     * Parse all the child nodes of a given node and return a list of ast elements
     */
    function parseChildren(node, ctx) {
        const children = [];
        for (let child of node.childNodes) {
            const childAst = parseNode(child, ctx);
            if (childAst) {
                if (childAst.type === 3 /* Multi */) {
                    children.push(...childAst.content);
                }
                else {
                    children.push(childAst);
                }
            }
        }
        return children;
    }
    /**
     * Parse all the child nodes of a given node and return an ast if possible.
     * In the case there are multiple children, they are wrapped in a astmulti.
     */
    function parseChildNodes(node, ctx) {
        const children = parseChildren(node, ctx);
        switch (children.length) {
            case 0:
                return null;
            case 1:
                return children[0];
            default:
                return { type: 3 /* Multi */, content: children };
        }
    }
    /**
     * Normalizes the content of an Element so that t-if/t-elif/t-else directives
     * immediately follow one another (by removing empty text nodes or comments).
     * Throws an error when a conditional branching statement is malformed. This
     * function modifies the Element in place.
     *
     * @param el the element containing the tree that should be normalized
     */
    function normalizeTIf(el) {
        let tbranch = el.querySelectorAll("[t-elif], [t-else]");
        for (let i = 0, ilen = tbranch.length; i < ilen; i++) {
            let node = tbranch[i];
            let prevElem = node.previousElementSibling;
            let pattr = (name) => prevElem.getAttribute(name);
            let nattr = (name) => +!!node.getAttribute(name);
            if (prevElem && (pattr("t-if") || pattr("t-elif"))) {
                if (pattr("t-foreach")) {
                    throw new OwlError("t-if cannot stay at the same level as t-foreach when using t-elif or t-else");
                }
                if (["t-if", "t-elif", "t-else"].map(nattr).reduce(function (a, b) {
                    return a + b;
                }) > 1) {
                    throw new OwlError("Only one conditional branching directive is allowed per node");
                }
                // All text (with only spaces) and comment nodes (nodeType 8) between
                // branch nodes are removed
                let textNode;
                while ((textNode = node.previousSibling) !== prevElem) {
                    if (textNode.nodeValue.trim().length && textNode.nodeType !== 8) {
                        throw new OwlError("text is not allowed between branching directives");
                    }
                    textNode.remove();
                }
            }
            else {
                throw new OwlError("t-elif and t-else directives must be preceded by a t-if or t-elif directive");
            }
        }
    }
    /**
     * Normalizes the content of an Element so that t-esc directives on components
     * are removed and instead places a <t t-esc=""> as the default slot of the
     * component. Also throws if the component already has content. This function
     * modifies the Element in place.
     *
     * @param el the element containing the tree that should be normalized
     */
    function normalizeTEscTOut(el) {
        for (const d of ["t-esc", "t-out"]) {
            const elements = [...el.querySelectorAll(`[${d}]`)].filter((el) => el.tagName[0] === el.tagName[0].toUpperCase() || el.hasAttribute("t-component"));
            for (const el of elements) {
                if (el.childNodes.length) {
                    throw new OwlError(`Cannot have ${d} on a component that already has content`);
                }
                const value = el.getAttribute(d);
                el.removeAttribute(d);
                const t = el.ownerDocument.createElement("t");
                if (value != null) {
                    t.setAttribute(d, value);
                }
                el.appendChild(t);
            }
        }
    }
    /**
     * Normalizes the tree inside a given element and do some preliminary validation
     * on it. This function modifies the Element in place.
     *
     * @param el the element containing the tree that should be normalized
     */
    function normalizeXML(el) {
        normalizeTIf(el);
        normalizeTEscTOut(el);
    }
    /**
     * Parses an XML string into an XML document, throwing errors on parser errors
     * instead of returning an XML document containing the parseerror.
     *
     * @param xml the string to parse
     * @returns an XML document corresponding to the content of the string
     */
    function parseXML(xml) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(xml, "text/xml");
        if (doc.getElementsByTagName("parsererror").length) {
            let msg = "Invalid XML in template.";
            const parsererrorText = doc.getElementsByTagName("parsererror")[0].textContent;
            if (parsererrorText) {
                msg += "\nThe parser has produced the following error message:\n" + parsererrorText;
                const re = /\d+/g;
                const firstMatch = re.exec(parsererrorText);
                if (firstMatch) {
                    const lineNumber = Number(firstMatch[0]);
                    const line = xml.split("\n")[lineNumber - 1];
                    const secondMatch = re.exec(parsererrorText);
                    if (line && secondMatch) {
                        const columnIndex = Number(secondMatch[0]) - 1;
                        if (line[columnIndex]) {
                            msg +=
                                `\nThe error might be located at xml line ${lineNumber} column ${columnIndex}\n` +
                                    `${line}\n${"-".repeat(columnIndex - 1)}^`;
                        }
                    }
                }
            }
            throw new OwlError(msg);
        }
        return doc;
    }
<<<<<<< HEAD
=======
    function escapeQuotes(str) {
        return str.replace(/\'/g, "\\'");
    }
    //------------------------------------------------------------------------------
    // QWeb rendering engine
    //------------------------------------------------------------------------------
    class QWeb extends EventBus {
        constructor(config = {}) {
            super();
            this.h = h;
            // subTemplates are stored in two objects: a (local) mapping from a name to an
            // id, and a (global) mapping from an id to the compiled function.  This is
            // necessary to ensure that global templates can be called with more than one
            // QWeb instance.
            this.subTemplates = {};
            this.isUpdating = false;
            this.templates = Object.create(QWeb.TEMPLATES);
            if (config.templates) {
                this.addTemplates(config.templates);
            }
            if (config.translateFn) {
                this.translateFn = config.translateFn;
            }
        }
        static addDirective(directive) {
            if (directive.name in QWeb.DIRECTIVE_NAMES) {
                throw new Error(`Directive "${directive.name} already registered`);
            }
            QWeb.DIRECTIVES.push(directive);
            QWeb.DIRECTIVE_NAMES[directive.name] = 1;
            QWeb.DIRECTIVES.sort((d1, d2) => d1.priority - d2.priority);
            if (directive.extraNames) {
                directive.extraNames.forEach((n) => (QWeb.DIRECTIVE_NAMES[n] = 1));
            }
        }
        static registerComponent(name, Component) {
            if (QWeb.components[name]) {
                throw new Error(`Component '${name}' has already been registered`);
            }
            QWeb.components[name] = Component;
        }
        /**
         * Register globally a template.  All QWeb instances will obtain their
         * templates from their own template map, and then, from the global static
         * TEMPLATES property.
         */
        static registerTemplate(name, template) {
            if (QWeb.TEMPLATES[name]) {
                throw new Error(`Template '${name}' has already been registered`);
            }
            const qweb = new QWeb();
            qweb.addTemplate(name, template);
            QWeb.TEMPLATES[name] = qweb.templates[name];
        }
        /**
         * Add a template to the internal template map.  Note that it is not
         * immediately compiled.
         */
        addTemplate(name, xmlString, allowDuplicate) {
            if (allowDuplicate && name in this.templates) {
                return;
            }
            const doc = parseXML(xmlString);
            if (!doc.firstChild) {
                throw new Error("Invalid template (should not be empty)");
            }
            this._addTemplate(name, doc.firstChild);
        }
        /**
         * Load templates from a xml (as a string or xml document).  This will look up
         * for the first <templates> tag, and will consider each child of this as a
         * template, with the name given by the t-name attribute.
         */
        addTemplates(xmlstr) {
            if (!xmlstr) {
                return;
            }
            const doc = typeof xmlstr === "string" ? parseXML(xmlstr) : xmlstr;
            const templates = doc.getElementsByTagName("templates")[0];
            if (!templates) {
                return;
            }
            for (let elem of templates.children) {
                const name = elem.getAttribute("t-name");
                this._addTemplate(name, elem);
            }
        }
        _addTemplate(name, elem) {
            if (name in this.templates) {
                throw new Error(`Template ${name} already defined`);
            }
            this._processTemplate(elem);
            const template = {
                elem,
                fn: function (context, extra) {
                    const compiledFunction = this._compile(name);
                    template.fn = compiledFunction;
                    return compiledFunction.call(this, context, extra);
                },
            };
            this.templates[name] = template;
        }
        _processTemplate(elem) {
            let tbranch = elem.querySelectorAll("[t-elif], [t-else]");
            for (let i = 0, ilen = tbranch.length; i < ilen; i++) {
                let node = tbranch[i];
                let prevElem = node.previousElementSibling;
                let pattr = function (name) {
                    return prevElem.getAttribute(name);
                };
                let nattr = function (name) {
                    return +!!node.getAttribute(name);
                };
                if (prevElem && (pattr("t-if") || pattr("t-elif"))) {
                    if (pattr("t-foreach")) {
                        throw new Error("t-if cannot stay at the same level as t-foreach when using t-elif or t-else");
                    }
                    if (["t-if", "t-elif", "t-else"].map(nattr).reduce(function (a, b) {
                        return a + b;
                    }) > 1) {
                        throw new Error("Only one conditional branching directive is allowed per node");
                    }
                    // All text (with only spaces) and comment nodes (nodeType 8) between
                    // branch nodes are removed
                    let textNode;
                    while ((textNode = node.previousSibling) !== prevElem) {
                        if (textNode.nodeValue.trim().length && textNode.nodeType !== 8) {
                            throw new Error("text is not allowed between branching directives");
                        }
                        textNode.remove();
                    }
                }
                else {
                    throw new Error("t-elif and t-else directives must be preceded by a t-if or t-elif directive");
                }
            }
        }
        /**
         * Render a template
         *
         * @param {string} name the template should already have been added
         */
        render(name, context = {}, extra = null) {
            const template = this.templates[name];
            if (!template) {
                throw new Error(`Template ${name} does not exist`);
            }
            return template.fn.call(this, context, extra);
        }
        /**
         * Render a template to a html string.
         *
         * Note that this is more limited than the `render` method: it is not suitable
         * to render a full component tree, since this is an asynchronous operation.
         * This method can only render templates without components.
         */
        renderToString(name, context = {}, extra) {
            const vnode = this.render(name, context, extra);
            if (vnode.sel === undefined) {
                return vnode.text;
            }
            const node = document.createElement(vnode.sel);
            const result = patch(node, vnode);
            return result.elm.outerHTML;
        }
        /**
         * Force all widgets connected to this QWeb instance to rerender themselves.
         *
         * This method is mostly useful for external code that want to modify the
         * application in some cases.  For example, a router plugin.
         */
        forceUpdate() {
            this.isUpdating = true;
            Promise.resolve().then(() => {
                if (this.isUpdating) {
                    this.isUpdating = false;
                    this.trigger("update");
                }
            });
        }
        _compile(name, options = {}) {
            const elem = options.elem || this.templates[name].elem;
            const isDebug = elem.attributes.hasOwnProperty("t-debug");
            const ctx = new CompilationContext(name);
            if (elem.tagName !== "t") {
                ctx.shouldDefineResult = false;
            }
            if (options.hasParent) {
                ctx.variables = Object.create(null);
                ctx.parentNode = ctx.generateID();
                ctx.allowMultipleRoots = true;
                ctx.shouldDefineParent = true;
                ctx.hasParentWidget = true;
                ctx.shouldDefineResult = false;
                ctx.addLine(`let c${ctx.parentNode} = extra.parentNode;`);
                if (options.defineKey) {
                    ctx.addLine(`let key0 = extra.key || "";`);
                    ctx.hasKey0 = true;
                }
            }
            this._compileNode(elem, ctx);
            if (!options.hasParent) {
                if (ctx.shouldDefineResult) {
                    ctx.addLine(`return result;`);
                }
                else {
                    if (!ctx.rootNode) {
                        throw new Error(`A template should have one root node (${ctx.templateName})`);
                    }
                    ctx.addLine(`return vn${ctx.rootNode};`);
                }
            }
            let code = ctx.generateCode();
            const templateName = ctx.templateName.replace(/`/g, "'").slice(0, 200);
            code.unshift(`    // Template name: "${templateName}"`);
            let template;
            try {
                template = new Function("context, extra", code.join("\n"));
            }
            catch (e) {
                console.groupCollapsed(`Invalid Code generated by ${templateName}`);
                console.warn(code.join("\n"));
                console.groupEnd();
                throw new Error(`Invalid generated code while compiling template '${templateName}': ${e.message}`);
            }
            if (isDebug) {
                const tpl = this.templates[name];
                if (tpl) {
                    const msg = `Template: ${tpl.elem.outerHTML}\nCompiled code:\n${template.toString()}`;
                    console.log(msg);
                }
            }
            return template;
        }
        /**
         * Generate code from an xml node
         *
         */
        _compileNode(node, ctx) {
            if (!(node instanceof Element)) {
                // this is a text node, there are no directive to apply
                let text = node.textContent;
                if (!ctx.inPreTag) {
                    if (lineBreakRE.test(text) && !text.trim()) {
                        return;
                    }
                    text = text.replace(whitespaceRE, " ");
                }
                if (this.translateFn) {
                    if (node.parentNode.getAttribute("t-translation") !== "off") {
                        const match = translationRE.exec(text);
                        text = match[1] + this.translateFn(match[2]) + match[3];
                    }
                }
                if (ctx.parentNode) {
                    if (node.nodeType === 3) {
                        ctx.addLine(`c${ctx.parentNode}.push({text: \`${text}\`});`);
                    }
                    else if (node.nodeType === 8) {
                        ctx.addLine(`c${ctx.parentNode}.push(h('!', \`${text}\`));`);
                    }
                }
                else if (ctx.parentTextNode) {
                    ctx.addLine(`vn${ctx.parentTextNode}.text += \`${text}\`;`);
                }
                else {
                    // this is an unusual situation: this text node is the result of the
                    // template rendering.
                    let nodeID = ctx.generateID();
                    ctx.addLine(`let vn${nodeID} = {text: \`${text}\`};`);
                    ctx.addLine(`result = vn${nodeID};`);
                    ctx.rootContext.rootNode = nodeID;
                    ctx.rootContext.parentTextNode = nodeID;
                }
                return;
            }
            if (node.tagName !== "t" && node.hasAttribute("t-call")) {
                const tCallNode = document.implementation.createDocument("http://www.w3.org/1999/xhtml", "t", null).documentElement;
                tCallNode.setAttribute("t-call", node.getAttribute("t-call"));
                node.removeAttribute("t-call");
                node.prepend(tCallNode);
            }
            const firstLetter = node.tagName[0];
            if (firstLetter === firstLetter.toUpperCase()) {
                // this is a component, we modify in place the xml document to change
                // <SomeComponent ... /> to <SomeComponent t-component="SomeComponent" ... />
                node.setAttribute("t-component", node.tagName);
            }
            else if (node.tagName !== "t" && node.hasAttribute("t-component")) {
                throw new Error(`Directive 't-component' can only be used on <t> nodes (used on a <${node.tagName}>)`);
            }
            const attributes = node.attributes;
            const validDirectives = [];
            const finalizers = [];
            // maybe this is not optimal: we iterate on all attributes here, and again
            // just after for each directive.
            for (let i = 0; i < attributes.length; i++) {
                let attrName = attributes[i].name;
                if (attrName.startsWith("t-")) {
                    let dName = attrName.slice(2).split(/-|\./)[0];
                    if (!(dName in QWeb.DIRECTIVE_NAMES)) {
                        throw new Error(`Unknown QWeb directive: '${attrName}'`);
                    }
                    if (node.tagName !== "t" && (attrName === "t-esc" || attrName === "t-raw")) {
                        const tNode = document.implementation.createDocument("http://www.w3.org/1999/xhtml", "t", null).documentElement;
                        tNode.setAttribute(attrName, node.getAttribute(attrName));
                        for (let child of Array.from(node.childNodes)) {
                            tNode.appendChild(child);
                        }
                        node.appendChild(tNode);
                        node.removeAttribute(attrName);
                    }
                }
            }
            const DIR_N = QWeb.DIRECTIVES.length;
            const ATTR_N = attributes.length;
            let withHandlers = false;
            for (let i = 0; i < DIR_N; i++) {
                let directive = QWeb.DIRECTIVES[i];
                let fullName;
                let value;
                for (let j = 0; j < ATTR_N; j++) {
                    const name = attributes[j].name;
                    if (name === "t-" + directive.name ||
                        name.startsWith("t-" + directive.name + "-") ||
                        name.startsWith("t-" + directive.name + ".")) {
                        fullName = name;
                        value = attributes[j].textContent;
                        validDirectives.push({ directive, value, fullName });
                        if (directive.name === "on" || directive.name === "model") {
                            withHandlers = true;
                        }
                    }
                }
            }
            for (let { directive, value, fullName } of validDirectives) {
                if (directive.finalize) {
                    finalizers.push({ directive, value, fullName });
                }
                if (directive.atNodeEncounter) {
                    const isDone = directive.atNodeEncounter({
                        node,
                        qweb: this,
                        ctx,
                        fullName,
                        value,
                    });
                    if (isDone) {
                        for (let { directive, value, fullName } of finalizers) {
                            directive.finalize({ node, qweb: this, ctx, fullName, value });
                        }
                        return;
                    }
                }
            }
            if (node.nodeName !== "t" || node.hasAttribute("t-tag")) {
                let nodeHooks = {};
                let addNodeHook = function (hook, handler) {
                    nodeHooks[hook] = nodeHooks[hook] || [];
                    nodeHooks[hook].push(handler);
                };
                if (node.tagName === "select" && node.hasAttribute("t-att-value")) {
                    const value = node.getAttribute("t-att-value");
                    let exprId = ctx.generateID();
                    ctx.addLine(`let expr${exprId} = ${ctx.formatExpression(value)};`);
                    let expr = `expr${exprId}`;
                    node.setAttribute("t-att-value", expr);
                    addNodeHook("create", `n.elm.value=${expr};`);
                }
                let nodeID = this._compileGenericNode(node, ctx, withHandlers);
                ctx = ctx.withParent(nodeID);
                for (let { directive, value, fullName } of validDirectives) {
                    if (directive.atNodeCreation) {
                        directive.atNodeCreation({
                            node,
                            qweb: this,
                            ctx,
                            fullName,
                            value,
                            nodeID,
                            addNodeHook,
                        });
                    }
                }
                if (Object.keys(nodeHooks).length) {
                    ctx.addLine(`p${nodeID}.hook = {`);
                    for (let hook in nodeHooks) {
                        ctx.addLine(`  ${hook}: ${NODE_HOOKS_PARAMS[hook]} => {`);
                        for (let handler of nodeHooks[hook]) {
                            ctx.addLine(`    ${handler}`);
                        }
                        ctx.addLine(`  },`);
                    }
                    ctx.addLine(`};`);
                }
            }
            if (node.nodeName === "pre") {
                ctx = ctx.subContext("inPreTag", true);
            }
            this._compileChildren(node, ctx);
            // svg support
            // we hadd svg namespace if it is a svg or if it is a g, but only if it is
            // the root node.  This is the easiest way to support svg sub components:
            // they need to have a g tag as root. Otherwise, we would need a complete
            // list of allowed svg tags.
            const shouldAddNS = node.nodeName === "svg" || (node.nodeName === "g" && ctx.rootNode === ctx.parentNode);
            if (shouldAddNS) {
                ctx.rootContext.shouldDefineUtils = true;
                ctx.addLine(`utils.addNameSpace(vn${ctx.parentNode});`);
            }
            for (let { directive, value, fullName } of finalizers) {
                directive.finalize({ node, qweb: this, ctx, fullName, value });
            }
        }
        _compileGenericNode(node, ctx, withHandlers = true) {
            // nodeType 1 is generic tag
            if (node.nodeType !== 1) {
                throw new Error("unsupported node type");
            }
            const attributes = node.attributes;
            const attrs = [];
            const props = [];
            const tattrs = [];
            function handleProperties(key, val) {
                let isProp = false;
                switch (node.nodeName) {
                    case "input":
                        let type = node.getAttribute("type");
                        if (type === "checkbox" || type === "radio") {
                            if (key === "checked" || key === "indeterminate") {
                                isProp = true;
                            }
                        }
                        if (key === "value" || key === "readonly" || key === "disabled") {
                            isProp = true;
                        }
                        break;
                    case "option":
                        isProp = key === "selected" || key === "disabled";
                        break;
                    case "textarea":
                        isProp = key === "readonly" || key === "disabled" || key === "value";
                        break;
                    case "select":
                        isProp = key === "disabled" || key === "value";
                        break;
                    case "button":
                    case "optgroup":
                        isProp = key === "disabled";
                        break;
                }
                if (isProp) {
                    props.push(`${key}: ${val}`);
                }
            }
            let classObj = "";
            for (let i = 0; i < attributes.length; i++) {
                let name = attributes[i].name;
                let value = attributes[i].textContent;
                if (this.translateFn && TRANSLATABLE_ATTRS.includes(name)) {
                    value = this.translateFn(value);
                }
                // regular attributes
                if (!name.startsWith("t-") && !node.getAttribute("t-attf-" + name)) {
                    const attID = ctx.generateID();
                    if (name === "class") {
                        if ((value = value.trim())) {
                            let classDef = value
                                .split(/\s+/)
                                .map((a) => `'${escapeQuotes(a)}':true`)
                                .join(",");
                            if (classObj) {
                                ctx.addLine(`Object.assign(${classObj}, {${classDef}})`);
                            }
                            else {
                                classObj = `_${ctx.generateID()}`;
                                ctx.addLine(`let ${classObj} = {${classDef}};`);
                            }
                        }
                    }
                    else {
                        ctx.addLine(`let _${attID} = '${escapeQuotes(value)}';`);
                        if (!name.match(/^[a-zA-Z]+$/)) {
                            // attribute contains 'non letters' => we want to quote it
                            name = '"' + name + '"';
                        }
                        attrs.push(`${name}: _${attID}`);
                        handleProperties(name, `_${attID}`);
                    }
                }
                // dynamic attributes
                if (name.startsWith("t-att-")) {
                    let attName = name.slice(6);
                    const v = ctx.getValue(value);
                    let formattedValue = typeof v === "string" ? ctx.formatExpression(v) : `scope.${v.id}`;
                    if (attName === "class") {
                        ctx.rootContext.shouldDefineUtils = true;
                        formattedValue = `utils.toClassObj(${formattedValue})`;
                        if (classObj) {
                            ctx.addLine(`Object.assign(${classObj}, ${formattedValue})`);
                        }
                        else {
                            classObj = `_${ctx.generateID()}`;
                            ctx.addLine(`let ${classObj} = ${formattedValue};`);
                        }
                    }
                    else {
                        const attID = ctx.generateID();
                        if (!attName.match(/^[a-zA-Z]+$/)) {
                            // attribute contains 'non letters' => we want to quote it
                            attName = '"' + attName + '"';
                        }
                        // we need to combine dynamic with non dynamic attributes:
                        // class="a" t-att-class="'yop'" should be rendered as class="a yop"
                        const attValue = node.getAttribute(attName);
                        if (attValue) {
                            const attValueID = ctx.generateID();
                            ctx.addLine(`let _${attValueID} = ${formattedValue};`);
                            formattedValue = `'${attValue}' + (_${attValueID} ? ' ' + _${attValueID} : '')`;
                            const attrIndex = attrs.findIndex((att) => att.startsWith(attName + ":"));
                            attrs.splice(attrIndex, 1);
                        }
                        if (node.nodeName === "select" && attName === "value") {
                            attrs.push(`${attName}: ${v}`);
                            handleProperties(attName, v);
                        }
                        else {
                            ctx.addLine(`let _${attID} = ${formattedValue};`);
                            attrs.push(`${attName}: _${attID}`);
                            handleProperties(attName, "_" + attID);
                        }
                    }
                }
                if (name.startsWith("t-attf-")) {
                    let attName = name.slice(7);
                    if (!attName.match(/^[a-zA-Z]+$/)) {
                        // attribute contains 'non letters' => we want to quote it
                        attName = '"' + attName + '"';
                    }
                    const formattedExpr = ctx.interpolate(value);
                    const attID = ctx.generateID();
                    let staticVal = node.getAttribute(attName);
                    if (staticVal) {
                        ctx.addLine(`let _${attID} = '${staticVal} ' + ${formattedExpr};`);
                    }
                    else {
                        ctx.addLine(`let _${attID} = ${formattedExpr};`);
                    }
                    attrs.push(`${attName}: _${attID}`);
                }
                // t-att= attributes
                if (name === "t-att") {
                    let id = ctx.generateID();
                    ctx.addLine(`let _${id} = ${ctx.formatExpression(value)};`);
                    tattrs.push(id);
                }
            }
            let nodeID = ctx.generateID();
            let key = ctx.loopNumber || ctx.hasKey0 ? `\`\${key${ctx.loopNumber}}_${nodeID}\`` : nodeID;
            const parts = [`key:${key}`];
            if (attrs.length + tattrs.length > 0) {
                parts.push(`attrs:{${attrs.join(",")}}`);
            }
            if (props.length > 0) {
                parts.push(`props:{${props.join(",")}}`);
            }
            if (classObj) {
                parts.push(`class:${classObj}`);
            }
            if (withHandlers) {
                parts.push(`on:{}`);
            }
            ctx.addLine(`let c${nodeID} = [], p${nodeID} = {${parts.join(",")}};`);
            for (let id of tattrs) {
                ctx.addIf(`_${id} instanceof Array`);
                ctx.addLine(`p${nodeID}.attrs[_${id}[0]] = _${id}[1];`);
                ctx.addElse();
                ctx.addLine(`for (let key in _${id}) {`);
                ctx.indent();
                ctx.addLine(`p${nodeID}.attrs[key] = _${id}[key];`);
                ctx.dedent();
                ctx.addLine(`}`);
                ctx.closeIf();
            }
            let nodeName = `'${node.nodeName}'`;
            if (node.hasAttribute("t-tag")) {
                const tagExpr = node.getAttribute("t-tag");
                node.removeAttribute("t-tag");
                nodeName = `tag${ctx.generateID()}`;
                ctx.addLine(`let ${nodeName} = ${ctx.formatExpression(tagExpr)};`);
            }
            ctx.addLine(`let vn${nodeID} = h(${nodeName}, p${nodeID}, c${nodeID});`);
            if (ctx.parentNode) {
                ctx.addLine(`c${ctx.parentNode}.push(vn${nodeID});`);
            }
            else if (ctx.loopNumber || ctx.hasKey0) {
                ctx.rootContext.shouldDefineResult = true;
                ctx.addLine(`result = vn${nodeID};`);
            }
            return nodeID;
        }
        _compileChildren(node, ctx) {
            if (node.childNodes.length > 0) {
                for (let child of Array.from(node.childNodes)) {
                    this._compileNode(child, ctx);
                }
            }
        }
    }
    QWeb.utils = UTILS;
    QWeb.components = Object.create(null);
    QWeb.DIRECTIVE_NAMES = {
        name: 1,
        att: 1,
        attf: 1,
        translation: 1,
        tag: 1,
    };
    QWeb.DIRECTIVES = [];
    QWeb.TEMPLATES = {};
    QWeb.nextId = 1;
    // dev mode enables better error messages or more costly validations
    QWeb.dev = false;
    QWeb.enableTransitions = true;
    // slots contains sub templates defined with t-set inside t-component nodes, and
    // are meant to be used by the t-slot directive.
    QWeb.slots = {};
    QWeb.nextSlotId = 1;
    QWeb.subTemplates = {};
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    function compile(template, options = {}) {
        // parsing
        const ast = parse(template);
        // some work
        const hasSafeContext = template instanceof Node
            ? !(template instanceof Element) || template.querySelector("[t-set], [t-call]") === null
            : !template.includes("t-set") && !template.includes("t-call");
        // code generation
        const codeGenerator = new CodeGenerator(ast, { ...options, hasSafeContext });
        const code = codeGenerator.generateCode();
        // template function
        try {
            return new Function("app, bdom, helpers", code);
        }
<<<<<<< HEAD
        catch (originalError) {
            const { name } = options;
            const nameStr = name ? `template "${name}"` : "anonymous template";
            const err = new OwlError(`Failed to compile ${nameStr}: ${originalError.message}\n\ngenerated code:\nfunction(app, bdom, helpers) {\n${code}\n}`);
            err.cause = originalError;
            throw err;
        }
    }

    // do not modify manually. This file is generated by the release script.
    const version = "2.2.6";
=======
        return result;
    }
    function htmlToVNode(node) {
        if (!(node instanceof Element)) {
            if (node instanceof Comment) {
                return h("!", node.textContent);
            }
            return { text: node.textContent };
        }
        const attrs = {};
        for (let attr of node.attributes) {
            attrs[attr.name] = attr.textContent;
        }
        const children = [];
        for (let c of node.childNodes) {
            children.push(htmlToVNode(c));
        }
        const vnode = h(node.tagName, { attrs }, children);
        if (vnode.sel === "svg") {
            addNS(vnode.data, vnode.children, vnode.sel);
        }
        return vnode;
    }

    /**
     * Owl QWeb Directives
     *
     * This file contains the implementation of most standard QWeb directives:
     * - t-esc
     * - t-raw
     * - t-set/t-value
     * - t-if/t-elif/t-else
     * - t-call
     * - t-foreach/t-as
     * - t-debug
     * - t-log
     */
    //------------------------------------------------------------------------------
    // t-esc and t-raw
    //------------------------------------------------------------------------------
    QWeb.utils.htmlToVDOM = htmlToVDOM;
    function compileValueNode(value, node, qweb, ctx) {
        ctx.rootContext.shouldDefineScope = true;
        if (value === "0") {
            if (ctx.parentNode) {
                // the 'zero' magical symbol is where we can find the result of the rendering
                // of  the body of the t-call.
                ctx.rootContext.shouldDefineUtils = true;
                const zeroArgs = ctx.escaping
                    ? `{text: utils.vDomToString(scope[utils.zero])}`
                    : `...scope[utils.zero]`;
                ctx.addLine(`c${ctx.parentNode}.push(${zeroArgs});`);
            }
            return;
        }
        let exprID;
        if (typeof value === "string") {
            exprID = `_${ctx.generateID()}`;
            ctx.addLine(`let ${exprID} = ${ctx.formatExpression(value)};`);
        }
        else {
            exprID = `scope.${value.id}`;
        }
        ctx.addIf(`${exprID} != null`);
        if (ctx.escaping) {
            let protectID;
            if (value.hasBody) {
                ctx.rootContext.shouldDefineUtils = true;
                protectID = ctx.startProtectScope();
                ctx.addLine(`${exprID} = ${exprID} instanceof utils.VDomArray ? utils.vDomToString(${exprID}) : ${exprID};`);
            }
            if (ctx.parentTextNode) {
                ctx.addLine(`vn${ctx.parentTextNode}.text += ${exprID};`);
            }
            else if (ctx.parentNode) {
                ctx.addLine(`c${ctx.parentNode}.push({text: ${exprID}});`);
            }
            else {
                let nodeID = ctx.generateID();
                ctx.rootContext.rootNode = nodeID;
                ctx.rootContext.parentTextNode = nodeID;
                ctx.addLine(`let vn${nodeID} = {text: ${exprID}};`);
                if (ctx.rootContext.shouldDefineResult) {
                    ctx.addLine(`result = vn${nodeID}`);
                }
            }
            if (value.hasBody) {
                ctx.stopProtectScope(protectID);
            }
        }
        else {
            ctx.rootContext.shouldDefineUtils = true;
            if (value.hasBody) {
                ctx.addLine(`const vnodeArray = ${exprID} instanceof utils.VDomArray ? ${exprID} : utils.htmlToVDOM(${exprID});`);
                ctx.addLine(`c${ctx.parentNode}.push(...vnodeArray);`);
            }
            else {
                ctx.addLine(`c${ctx.parentNode}.push(...utils.htmlToVDOM(${exprID}));`);
            }
        }
        if (node.childNodes.length) {
            ctx.addElse();
            qweb._compileChildren(node, ctx);
        }
        ctx.closeIf();
    }
    QWeb.addDirective({
        name: "esc",
        priority: 70,
        atNodeEncounter({ node, qweb, ctx }) {
            let value = ctx.getValue(node.getAttribute("t-esc"));
            compileValueNode(value, node, qweb, ctx.subContext("escaping", true));
            return true;
        },
    });
    QWeb.addDirective({
        name: "raw",
        priority: 80,
        atNodeEncounter({ node, qweb, ctx }) {
            let value = ctx.getValue(node.getAttribute("t-raw"));
            compileValueNode(value, node, qweb, ctx);
            return true;
        },
    });
    //------------------------------------------------------------------------------
    // t-set
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "set",
        extraNames: ["value"],
        priority: 60,
        atNodeEncounter({ node, qweb, ctx }) {
            ctx.rootContext.shouldDefineScope = true;
            const variable = node.getAttribute("t-set");
            let value = node.getAttribute("t-value");
            ctx.variables[variable] = ctx.variables[variable] || {};
            let qwebvar = ctx.variables[variable];
            const hasBody = node.hasChildNodes();
            qwebvar.id = variable;
            qwebvar.expr = `scope.${variable}`;
            if (value) {
                const formattedValue = ctx.formatExpression(value);
                let scopeExpr = `scope`;
                if (ctx.protectedScopeNumber) {
                    ctx.rootContext.shouldDefineUtils = true;
                    scopeExpr = `utils.getScope(scope, '${variable}')`;
                }
                ctx.addLine(`${scopeExpr}.${variable} = ${formattedValue};`);
                qwebvar.value = formattedValue;
            }
            if (hasBody) {
                ctx.rootContext.shouldDefineUtils = true;
                if (value) {
                    ctx.addIf(`!(${qwebvar.expr})`);
                }
                const tempParentNodeID = ctx.generateID();
                const _parentNode = ctx.parentNode;
                ctx.parentNode = tempParentNodeID;
                ctx.addLine(`let c${tempParentNodeID} = new utils.VDomArray();`);
                const nodeCopy = node.cloneNode(true);
                for (let attr of ["t-set", "t-value", "t-if", "t-else", "t-elif"]) {
                    nodeCopy.removeAttribute(attr);
                }
                qweb._compileNode(nodeCopy, ctx);
                ctx.addLine(`${qwebvar.expr} = c${tempParentNodeID}`);
                qwebvar.value = `c${tempParentNodeID}`;
                qwebvar.hasBody = true;
                ctx.parentNode = _parentNode;
                if (value) {
                    ctx.closeIf();
                }
            }
            return true;
        },
    });
    //------------------------------------------------------------------------------
    // t-if, t-elif, t-else
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "if",
        priority: 20,
        atNodeEncounter({ node, ctx }) {
            let cond = ctx.getValue(node.getAttribute("t-if"));
            ctx.addIf(typeof cond === "string" ? ctx.formatExpression(cond) : `scope.${cond.id}`);
            return false;
        },
        finalize({ ctx }) {
            ctx.closeIf();
        },
    });
    QWeb.addDirective({
        name: "elif",
        priority: 30,
        atNodeEncounter({ node, ctx }) {
            let cond = ctx.getValue(node.getAttribute("t-elif"));
            ctx.addLine(`else if (${typeof cond === "string" ? ctx.formatExpression(cond) : `scope.${cond.id}`}) {`);
            ctx.indent();
            return false;
        },
        finalize({ ctx }) {
            ctx.closeIf();
        },
    });
    QWeb.addDirective({
        name: "else",
        priority: 40,
        atNodeEncounter({ ctx }) {
            ctx.addLine(`else {`);
            ctx.indent();
            return false;
        },
        finalize({ ctx }) {
            ctx.closeIf();
        },
    });
    //------------------------------------------------------------------------------
    // t-call
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "call",
        priority: 50,
        atNodeEncounter({ node, qweb, ctx }) {
            // Step 1: sanity checks
            // ------------------------------------------------
            ctx.rootContext.shouldDefineScope = true;
            ctx.rootContext.shouldDefineUtils = true;
            const subTemplate = node.getAttribute("t-call");
            const isDynamic = INTERP_REGEXP.test(subTemplate);
            const nodeTemplate = qweb.templates[subTemplate];
            if (!isDynamic && !nodeTemplate) {
                throw new Error(`Cannot find template "${subTemplate}" (t-call)`);
            }
            // Step 2: compile target template in sub templates
            // ------------------------------------------------
            let subIdstr;
            if (isDynamic) {
                const _id = ctx.generateID();
                ctx.addLine(`let tname${_id} = ${ctx.interpolate(subTemplate)};`);
                ctx.addLine(`let tid${_id} = this.subTemplates[tname${_id}];`);
                ctx.addIf(`!tid${_id}`);
                ctx.addLine(`tid${_id} = this.constructor.nextId++;`);
                ctx.addLine(`this.subTemplates[tname${_id}] = tid${_id};`);
                ctx.addLine(`this.constructor.subTemplates[tid${_id}] = this._compile(tname${_id}, {hasParent: true, defineKey: true});`);
                ctx.closeIf();
                subIdstr = `tid${_id}`;
            }
            else {
                let subId = qweb.subTemplates[subTemplate];
                if (!subId) {
                    subId = QWeb.nextId++;
                    qweb.subTemplates[subTemplate] = subId;
                    const subTemplateFn = qweb._compile(subTemplate, { hasParent: true, defineKey: true });
                    QWeb.subTemplates[subId] = subTemplateFn;
                }
                subIdstr = `'${subId}'`;
            }
            // Step 3: compile t-call body if necessary
            // ------------------------------------------------
            let hasBody = node.hasChildNodes();
            const protectID = ctx.startProtectScope();
            if (hasBody) {
                // we add a sub scope to protect the ambient scope
                ctx.addLine(`{`);
                ctx.indent();
                const nodeCopy = node.cloneNode(true);
                for (let attr of ["t-if", "t-else", "t-elif", "t-call"]) {
                    nodeCopy.removeAttribute(attr);
                }
                // this local scope is intended to trap c__0
                ctx.addLine(`{`);
                ctx.indent();
                ctx.addLine("let c__0 = [];");
                qweb._compileNode(nodeCopy, ctx.subContext("parentNode", "__0"));
                ctx.rootContext.shouldDefineUtils = true;
                ctx.addLine("scope[utils.zero] = c__0;");
                ctx.dedent();
                ctx.addLine(`}`);
            }
            // Step 4: add the appropriate function call to current component
            // ------------------------------------------------
            const parentComponent = ctx.rootContext.shouldDefineParent
                ? `parent`
                : `utils.getComponent(context)`;
            const key = ctx.generateTemplateKey();
            const parentNode = ctx.parentNode ? `c${ctx.parentNode}` : "result";
            const extra = `Object.assign({}, extra, {parentNode: ${parentNode}, parent: ${parentComponent}, key: ${key}})`;
            if (ctx.parentNode) {
                ctx.addLine(`this.constructor.subTemplates[${subIdstr}].call(this, scope, ${extra});`);
            }
            else {
                // this is a t-call with no parentnode, we need to extract the result
                ctx.rootContext.shouldDefineResult = true;
                ctx.addLine(`result = []`);
                ctx.addLine(`this.constructor.subTemplates[${subIdstr}].call(this, scope, ${extra});`);
                ctx.addLine(`result = result[0]`);
            }
            // Step 5: restore previous scope
            // ------------------------------------------------
            if (hasBody) {
                ctx.dedent();
                ctx.addLine(`}`);
            }
            ctx.stopProtectScope(protectID);
            return true;
        },
    });
    //------------------------------------------------------------------------------
    // t-foreach
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "foreach",
        extraNames: ["as"],
        priority: 10,
        atNodeEncounter({ node, qweb, ctx }) {
            ctx.rootContext.shouldDefineScope = true;
            ctx = ctx.subContext("loopNumber", ctx.loopNumber + 1);
            const elems = node.getAttribute("t-foreach");
            const name = node.getAttribute("t-as");
            let arrayID = ctx.generateID();
            ctx.addLine(`let _${arrayID} = ${ctx.formatExpression(elems)};`);
            ctx.addLine(`if (!_${arrayID}) { throw new Error('QWeb error: Invalid loop expression')}`);
            let keysID = ctx.generateID();
            let valuesID = ctx.generateID();
            ctx.addLine(`let _${keysID} = _${arrayID};`);
            ctx.addLine(`let _${valuesID} = _${arrayID};`);
            ctx.addIf(`!(_${arrayID} instanceof Array)`);
            ctx.addLine(`_${keysID} = Object.keys(_${arrayID});`);
            ctx.addLine(`_${valuesID} = Object.values(_${arrayID});`);
            ctx.closeIf();
            ctx.addLine(`let _length${keysID} = _${keysID}.length;`);
            let varsID = ctx.startProtectScope(true);
            const loopVar = `i${ctx.loopNumber}`;
            ctx.addLine(`for (let ${loopVar} = 0; ${loopVar} < _length${keysID}; ${loopVar}++) {`);
            ctx.indent();
            ctx.addLine(`scope.${name}_first = ${loopVar} === 0`);
            ctx.addLine(`scope.${name}_last = ${loopVar} === _length${keysID} - 1`);
            ctx.addLine(`scope.${name}_index = ${loopVar}`);
            ctx.addLine(`scope.${name} = _${keysID}[${loopVar}]`);
            ctx.addLine(`scope.${name}_value = _${valuesID}[${loopVar}]`);
            const nodeCopy = node.cloneNode(true);
            let shouldWarn = !nodeCopy.hasAttribute("t-key") &&
                node.children.length === 1 &&
                node.children[0].tagName !== "t" &&
                !node.children[0].hasAttribute("t-key");
            if (shouldWarn) {
                console.warn(`Directive t-foreach should always be used with a t-key! (in template: '${ctx.templateName}')`);
            }
            if (nodeCopy.hasAttribute("t-key")) {
                const expr = ctx.formatExpression(nodeCopy.getAttribute("t-key"));
                ctx.addLine(`let key${ctx.loopNumber} = ${expr};`);
                nodeCopy.removeAttribute("t-key");
            }
            else {
                ctx.addLine(`let key${ctx.loopNumber} = i${ctx.loopNumber};`);
            }
            nodeCopy.removeAttribute("t-foreach");
            qweb._compileNode(nodeCopy, ctx);
            ctx.dedent();
            ctx.addLine("}");
            ctx.stopProtectScope(varsID);
            return true;
        },
    });
    //------------------------------------------------------------------------------
    // t-debug
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "debug",
        priority: 1,
        atNodeEncounter({ ctx }) {
            ctx.addLine("debugger;");
        },
    });
    //------------------------------------------------------------------------------
    // t-log
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "log",
        priority: 1,
        atNodeEncounter({ ctx, value }) {
            const expr = ctx.formatExpression(value);
            ctx.addLine(`console.log(${expr})`);
        },
    });

    /**
     * Owl QWeb Extensions
     *
     * This file contains the implementation of non standard QWeb directives, added
     * by Owl and that will only work on Owl projects:
     *
     * - t-on
     * - t-ref
     * - t-transition
     * - t-mounted
     * - t-slot
     * - t-model
     */
    //------------------------------------------------------------------------------
    // t-on
    //------------------------------------------------------------------------------
    // these are pieces of code that will be injected into the event handler if
    // modifiers are specified
    const MODS_CODE = {
        prevent: "e.preventDefault();",
        self: "if (e.target !== this.elm) {return}",
        stop: "e.stopPropagation();",
    };
    const FNAMEREGEXP = /^[$A-Z_][0-9A-Z_$]*$/i;
    function makeHandlerCode(ctx, fullName, value, putInCache, modcodes = MODS_CODE) {
        let [event, ...mods] = fullName.slice(5).split(".");
        if (mods.includes("capture")) {
            event = "!" + event;
        }
        if (!event) {
            throw new Error("Missing event name with t-on directive");
        }
        let code;
        // check if it is a method with no args, a method with args or an expression
        let args = "";
        const name = value.replace(/\(.*\)/, function (_args) {
            args = _args.slice(1, -1);
            return "";
        });
        const isMethodCall = name.match(FNAMEREGEXP);
        // then generate code
        if (isMethodCall) {
            ctx.rootContext.shouldDefineUtils = true;
            const comp = `utils.getComponent(context)`;
            if (args) {
                const argId = ctx.generateID();
                ctx.addLine(`let args${argId} = [${ctx.formatExpression(args)}];`);
                code = `${comp}['${name}'](...args${argId}, e);`;
                putInCache = false;
            }
            else {
                code = `${comp}['${name}'](e);`;
            }
        }
        else {
            // if we get here, then it is an expression
            // we need to capture every variable in it
            putInCache = false;
            code = ctx.captureExpression(value);
            code = `const res = (() => { return ${code} })(); if (typeof res === 'function') { res(e) }`;
        }
        const modCode = mods.map((mod) => modcodes[mod]).join("");
        let handler = `function (e) {if (context.__owl__.status === ${5 /* DESTROYED */}){return}${modCode}${code}}`;
        if (putInCache) {
            const key = ctx.generateTemplateKey(event);
            ctx.addLine(`extra.handlers[${key}] = extra.handlers[${key}] || ${handler};`);
            handler = `extra.handlers[${key}]`;
        }
        return { event, handler };
    }
    QWeb.addDirective({
        name: "on",
        priority: 90,
        atNodeCreation({ ctx, fullName, value, nodeID }) {
            const { event, handler } = makeHandlerCode(ctx, fullName, value, true);
            ctx.addLine(`p${nodeID}.on['${event}'] = ${handler};`);
        },
    });
    //------------------------------------------------------------------------------
    // t-ref
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "ref",
        priority: 95,
        atNodeCreation({ ctx, value, addNodeHook }) {
            ctx.rootContext.shouldDefineRefs = true;
            const refKey = `ref${ctx.generateID()}`;
            ctx.addLine(`const ${refKey} = ${ctx.interpolate(value)};`);
            addNodeHook("create", `context.__owl__.refs[${refKey}] = n.elm;`);
            addNodeHook("destroy", `delete context.__owl__.refs[${refKey}];`);
        },
    });
    //------------------------------------------------------------------------------
    // t-transition
    //------------------------------------------------------------------------------
    QWeb.utils.nextFrame = function (cb) {
        requestAnimationFrame(() => requestAnimationFrame(cb));
    };
    QWeb.utils.transitionInsert = function (vn, name) {
        const elm = vn.elm;
        // remove potential duplicated vnode that is currently being removed, to
        // prevent from having twice the same node in the DOM during an animation
        const dup = elm.parentElement && elm.parentElement.querySelector(`*[data-owl-key='${vn.key}']`);
        if (dup) {
            dup.remove();
        }
        elm.classList.add(name + "-enter");
        elm.classList.add(name + "-enter-active");
        elm.classList.remove(name + "-leave-active");
        elm.classList.remove(name + "-leave-to");
        const finalize = () => {
            elm.classList.remove(name + "-enter-active");
            elm.classList.remove(name + "-enter-to");
        };
        this.nextFrame(() => {
            elm.classList.remove(name + "-enter");
            elm.classList.add(name + "-enter-to");
            whenTransitionEnd(elm, finalize);
        });
    };
    QWeb.utils.transitionRemove = function (vn, name, rm) {
        const elm = vn.elm;
        elm.setAttribute("data-owl-key", vn.key);
        elm.classList.add(name + "-leave");
        elm.classList.add(name + "-leave-active");
        const finalize = () => {
            if (!elm.classList.contains(name + "-leave-active")) {
                return;
            }
            elm.classList.remove(name + "-leave-active");
            elm.classList.remove(name + "-leave-to");
            rm();
        };
        this.nextFrame(() => {
            elm.classList.remove(name + "-leave");
            elm.classList.add(name + "-leave-to");
            whenTransitionEnd(elm, finalize);
        });
    };
    function getTimeout(delays, durations) {
        /* istanbul ignore next */
        while (delays.length < durations.length) {
            delays = delays.concat(delays);
        }
        return Math.max.apply(null, durations.map((d, i) => {
            return toMs(d) + toMs(delays[i]);
        }));
    }
    // Old versions of Chromium (below 61.0.3163.100) formats floating pointer numbers
    // in a locale-dependent way, using a comma instead of a dot.
    // If comma is not replaced with a dot, the input will be rounded down (i.e. acting
    // as a floor function) causing unexpected behaviors
    function toMs(s) {
        return Number(s.slice(0, -1).replace(",", ".")) * 1000;
    }
    function whenTransitionEnd(elm, cb) {
        if (!elm.parentNode) {
            // if we get here, this means that the element was removed for some other
            // reasons, and in that case, we don't want to work on animation since nothing
            // will be displayed anyway.
            return;
        }
        const styles = window.getComputedStyle(elm);
        const delays = (styles.transitionDelay || "").split(", ");
        const durations = (styles.transitionDuration || "").split(", ");
        const timeout = getTimeout(delays, durations);
        if (timeout > 0) {
            const transitionEndCB = () => {
                if (!elm.parentNode)
                    return;
                cb();
                browser.clearTimeout(fallbackTimeout);
                elm.removeEventListener("transitionend", transitionEndCB);
            };
            elm.addEventListener("transitionend", transitionEndCB, { once: true });
            const fallbackTimeout = browser.setTimeout(transitionEndCB, timeout + 1);
        }
        else {
            cb();
        }
    }
    QWeb.addDirective({
        name: "transition",
        priority: 96,
        atNodeCreation({ ctx, value, addNodeHook }) {
            if (!QWeb.enableTransitions) {
                return;
            }
            ctx.rootContext.shouldDefineUtils = true;
            let name = value;
            const hooks = {
                insert: `utils.transitionInsert(vn, '${name}');`,
                remove: `utils.transitionRemove(vn, '${name}', rm);`,
            };
            for (let hookName in hooks) {
                addNodeHook(hookName, hooks[hookName]);
            }
        },
    });
    //------------------------------------------------------------------------------
    // t-slot
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "slot",
        priority: 80,
        atNodeEncounter({ ctx, value, node, qweb }) {
            const slotKey = ctx.generateID();
            const valueExpr = value.match(INTERP_REGEXP) ? ctx.interpolate(value) : `'${value}'`;
            ctx.addLine(`const slot${slotKey} = this.constructor.slots[context.__owl__.slotId + '_' + ${valueExpr}];`);
            ctx.addIf(`slot${slotKey}`);
            let parentNode = `c${ctx.parentNode}`;
            if (!ctx.parentNode) {
                ctx.rootContext.shouldDefineResult = true;
                ctx.rootContext.shouldDefineUtils = true;
                parentNode = `children${ctx.generateID()}`;
                ctx.addLine(`let ${parentNode}= []`);
                ctx.addLine(`result = {}`);
            }
            ctx.addLine(`slot${slotKey}.call(this, context.__owl__.scope, Object.assign({}, extra, {parentNode: ${parentNode}, parent: extra.parent || context}));`);
            if (!ctx.parentNode) {
                ctx.addLine(`utils.defineProxy(result, ${parentNode}[0]);`);
            }
            if (node.hasChildNodes()) {
                ctx.addElse();
                const nodeCopy = node.cloneNode(true);
                nodeCopy.removeAttribute("t-slot");
                qweb._compileNode(nodeCopy, ctx);
            }
            ctx.closeIf();
            return true;
        },
    });
    //------------------------------------------------------------------------------
    // t-model
    //------------------------------------------------------------------------------
    QWeb.utils.toNumber = function (val) {
        const n = parseFloat(val);
        return isNaN(n) ? val : n;
    };
    const hasDotAtTheEnd = /\.[\w_]+\s*$/;
    const hasBracketsAtTheEnd = /\[[^\[]+\]\s*$/;
    QWeb.addDirective({
        name: "model",
        priority: 42,
        atNodeCreation({ ctx, nodeID, value, node, fullName, addNodeHook }) {
            const type = node.getAttribute("type");
            let handler;
            let event = fullName.includes(".lazy") ? "change" : "input";
            // First step: we need to understand the structure of the expression, and
            // from it, extract a base expression (that we can capture, which is
            // important because it will be used in a handler later) and a formatted
            // expression (which uses the captured base expression)
            //
            // Also, we support 2 kinds of values: some.expr.value or some.expr[value]
            // For the first one, we have:
            // - base expression = scope[some].expr
            // - expression = exprX.value (where exprX is the var that captures the base expr)
            // and for the expression with brackets:
            // - base expression = scope[some].expr
            // - expression = exprX[keyX] (where exprX is the var that captures the base expr
            //        and keyX captures scope[value])
            let expr;
            let baseExpr;
            if (hasDotAtTheEnd.test(value)) {
                // we manage the case where the expr has a dot: some.expr.value
                const index = value.lastIndexOf(".");
                baseExpr = value.slice(0, index);
                ctx.addLine(`let expr${nodeID} = ${ctx.formatExpression(baseExpr)};`);
                expr = `expr${nodeID}${value.slice(index)}`;
            }
            else if (hasBracketsAtTheEnd.test(value)) {
                // we manage here the case where the expr ends in a bracket expression:
                //    some.expr[value]
                const index = value.lastIndexOf("[");
                baseExpr = value.slice(0, index);
                ctx.addLine(`let expr${nodeID} = ${ctx.formatExpression(baseExpr)};`);
                let exprKey = value.trimRight().slice(index + 1, -1);
                ctx.addLine(`let exprKey${nodeID} = ${ctx.formatExpression(exprKey)};`);
                expr = `expr${nodeID}[exprKey${nodeID}]`;
            }
            else {
                throw new Error(`Invalid t-model expression: "${value}" (it should be assignable)`);
            }
            const key = ctx.generateTemplateKey();
            if (node.tagName === "select") {
                ctx.addLine(`p${nodeID}.props = {value: ${expr}};`);
                addNodeHook("create", `n.elm.value=${expr};`);
                event = "change";
                handler = `(ev) => {${expr} = ev.target.value}`;
            }
            else if (type === "checkbox") {
                ctx.addLine(`p${nodeID}.props = {checked: ${expr}};`);
                handler = `(ev) => {${expr} = ev.target.checked}`;
            }
            else if (type === "radio") {
                const nodeValue = node.getAttribute("value");
                ctx.addLine(`p${nodeID}.props = {checked:${expr} === '${nodeValue}'};`);
                handler = `(ev) => {${expr} = ev.target.value}`;
                event = "click";
            }
            else {
                ctx.addLine(`p${nodeID}.props = {value: ${expr}};`);
                const trimCode = fullName.includes(".trim") ? ".trim()" : "";
                let valueCode = `ev.target.value${trimCode}`;
                if (fullName.includes(".number")) {
                    ctx.rootContext.shouldDefineUtils = true;
                    valueCode = `utils.toNumber(${valueCode})`;
                }
                handler = `(ev) => {${expr} = ${valueCode}}`;
            }
            ctx.addLine(`extra.handlers[${key}] = extra.handlers[${key}] || (${handler});`);
            ctx.addLine(`p${nodeID}.on['${event}'] = extra.handlers[${key}];`);
        },
    });
    //------------------------------------------------------------------------------
    // t-key
    //------------------------------------------------------------------------------
    QWeb.addDirective({
        name: "key",
        priority: 45,
        atNodeEncounter({ ctx, value, node }) {
            if (ctx.loopNumber === 0) {
                ctx.keyStack.push(ctx.rootContext.hasKey0);
                ctx.rootContext.hasKey0 = true;
            }
            ctx.addLine("{");
            ctx.indent();
            ctx.addLine(`let key${ctx.loopNumber} = ${ctx.formatExpression(value)};`);
        },
        finalize({ ctx }) {
            ctx.dedent();
            ctx.addLine("}");
            if (ctx.loopNumber === 0) {
                ctx.rootContext.hasKey0 = ctx.keyStack.pop();
            }
        },
    });

    const config = {
        translatableAttributes: TRANSLATABLE_ATTRS,
    };
    Object.defineProperty(config, "mode", {
        get() {
            return QWeb.dev ? "dev" : "prod";
        },
        set(mode) {
            QWeb.dev = mode === "dev";
            if (QWeb.dev) {
                console.info(`Owl is running in 'dev' mode.

This is not suitable for production use.
See https://github.com/odoo/owl/blob/master/doc/reference/config.md#mode for more information.`);
            }
        },
    });
    Object.defineProperty(config, "enableTransitions", {
        get() {
            return QWeb.enableTransitions;
        },
        set(value) {
            QWeb.enableTransitions = value;
        },
    });

    /**
     * We define here OwlEvent, a subclass of CustomEvent, with an additional
     * attribute:
     *  - originalComponent: the component that triggered the event
     */
    class OwlEvent extends CustomEvent {
        constructor(component, eventType, options) {
            super(eventType, options);
            this.originalComponent = component;
        }
    }

    //------------------------------------------------------------------------------
    // t-component
    //------------------------------------------------------------------------------
    const T_COMPONENT_MODS_CODE = Object.assign({}, MODS_CODE, {
        self: "if (e.target !== vn.elm) {return}",
    });
    QWeb.utils.defineProxy = function defineProxy(target, source) {
        for (let k in source) {
            Object.defineProperty(target, k, {
                get() {
                    return source[k];
                },
                set(val) {
                    source[k] = val;
                },
            });
        }
    };
    QWeb.utils.assignHooks = function assignHooks(dataObj, hooks) {
        if ("hook" in dataObj) {
            const hookObject = dataObj.hook;
            for (let name in hooks) {
                const current = hookObject[name];
                const fn = hooks[name];
                if (current) {
                    hookObject[name] = (...args) => {
                        current(...args);
                        fn(...args);
                    };
                }
                else {
                    hookObject[name] = fn;
                }
            }
        }
        else {
            dataObj.hook = hooks;
        }
    };
    /**
     * The t-component directive is certainly a complicated and hard to maintain piece
     * of code.  To help you, fellow developer, if you have to maintain it, I offer
     * you this advice: Good luck...
     *
     * Since it is not 'direct' code, but rather code that generates other code, it
     * is not easy to understand.  To help you, here  is a detailed and commented
     * explanation of the code generated by the t-component directive for the following
     * situation:
     * ```xml
     *   <Child
     *      t-key="'somestring'"
     *      flag="state.flag"
     *      t-transition="fade"/>
     * ```
     *
     * ```js
     * // we assign utils on top of the function because it will be useful for
     * // each components
     * let utils = this.utils;
     *
     * // this is the virtual node representing the parent div
     * let c1 = [], p1 = { key: 1 };
     * var vn1 = h("div", p1, c1);
     *
     * // t-component directive: we start by evaluating the expression given by t-key:
     * let key5 = "somestring";
     *
     * // def3 is the promise that will contain later either the new component
     * // creation, or the props update...
     * let def3;
     *
     * // this is kind of tricky: we need here to find if the component was already
     * // created by a previous rendering.  This is done by checking the internal
     * // `cmap` (children map) of the parent component: it maps keys to component ids,
     * // and, then, if there is an id, we look into the children list to get the
     * // instance
     * let w4 =
     *   key5 in context.__owl__.cmap
     *   ? context.__owl__.children[context.__owl__.cmap[key5]]
     *   : false;
     *
     * // We keep the index of the position of the component in the closure.  We push
     * // null to reserve the slot, and will replace it later by the component vnode,
     * // when it will be ready (do not forget that preparing/rendering a component is
     * // asynchronous)
     * let _2_index = c1.length;
     * c1.push(null);
     *
     * // we evaluate here the props given to the component. It is done here to be
     * // able to easily reference it later, and also, it might be an expensive
     * // computation, so it is certainly better to do it only once
     * let props4 = { flag: context["state"].flag };
     *
     * // If we have a component, currently rendering, but not ready yet, we do not want
     * // to wait for it to be ready if we can avoid it
     * if (w4 && w4.__owl__.renderPromise && !w4.__owl__.vnode) {
     *   // we check if the props are the same.  In that case, we can simply reuse
     *   // the previous rendering and skip all useless work
     *   if (utils.shallowEqual(props4, w4.__owl__.renderProps)) {
     *     def3 = w4.__owl__.renderPromise;
     *   } else {
     *     // if the props are not the same, we destroy the component and starts anew.
     *     // this will be faster than waiting for its rendering, then updating it
     *     w4.destroy();
     *     w4 = false;
     *   }
     * }
     *
     * if (!w4) {
     *   // in this situation, we need to create a new component.  First step is
     *   // to get a reference to the class, then create an instance with
     *   // current context as parent, and the props.
     *   let W4 = context.component && context.components[componentKey4] || QWeb.component[componentKey4];

     *   if (!W4) {
     *     throw new Error("Cannot find the definition of component 'child'");
     *   }
     *   w4 = new W4(owner, props4);
     *
     *   // Whenever we rerender the parent component, we need to be sure that we
     *   // are able to find the component instance. To do that, we register it to
     *   // the parent cmap (children map).  Note that the 'template' key is
     *   // used here, since this is what identify the component from the template
     *   // perspective.
     *   context.__owl__.cmap[key5] = w4.__owl__.id;
     *
     *   // __prepare is called, to basically call willStart, then render the
     *   // component
     *   def3 = w4.__prepare();
     *
     *   def3 = def3.then(vnode => {
     *     // we create here a virtual node for the parent (NOT the component). This
     *     // means that the vdom of the parent will be stopped here, and from
     *     // the parent's perspective, it simply is a vnode with no children.
     *     // However, it shares the same dom element with the component root
     *     // vnode.
     *     let pvnode = h(vnode.sel, { key: key5 });
     *
     *     // we add hooks to the parent vnode so we can interact with the new
     *     // component at the proper time
     *     pvnode.data.hook = {
     *       insert(vn) {
     *         // the __mount method will patch the component vdom into the elm vn.elm,
     *         // then call the mounted hooks. However, suprisingly, the snabbdom
     *         // patch method actually replace the elm by a new elm, so we need
     *         // to synchronise the pvnode elm with the resulting elm
     *         let nvn = w4.__mount(vnode, vn.elm);
     *         pvnode.elm = nvn.elm;
     *         // what follows is only present if there are animations on the component
     *         utils.transitionInsert(vn, "fade");
     *       },
     *       remove() {
     *         // override with empty function to prevent from removing the node
     *         // directly. It will be removed when destroy is called anyway, which
     *         // delays the removal if there are animations.
     *       },
     *       destroy() {
     *         // if there are animations, we delay the call to destroy on the
     *         // component, if not, we call it directly.
     *         let finalize = () => {
     *           w4.destroy();
     *         };
     *         utils.transitionRemove(vn, "fade", finalize);
     *       }
     *     };
     *     // the pvnode is inserted at the correct position in the div's children
     *     c1[_2_index] = pvnode;
     *
     *     // we keep here a reference to the parent vnode (representing the
     *     // component, so we can reuse it later whenever we update the component
     *     w4.__owl__.pvnode = pvnode;
     *   });
     * } else {
     *   // this is the 'update' path of the directive.
     *   // the call to __updateProps is the actual component update
     *   // Note that we only update the props if we cannot reuse the previous
     *   // rendering work (in the case it was rendered with the same props)
     *   def3 = def3 || w4.__updateProps(props4, extra.forceUpdate, extra.patchQueue);
     *   def3 = def3.then(() => {
     *     // if component was destroyed in the meantime, we do nothing (so, this
     *     // means that the parent's element children list will have a null in
     *     // the component's position, which will cause the pvnode to be removed
     *     // when it is patched.
     *     if (w4.__owl__.isDestroyed) {
     *       return;
     *     }
     *     // like above, we register the pvnode to the children list, so it
     *     // will not be patched out of the dom.
     *     let pvnode = w4.__owl__.pvnode;
     *     c1[_2_index] = pvnode;
     *   });
     * }
     *
     * // we register the deferred here so the parent can coordinate its patch operation
     * // with all the children.
     * extra.promises.push(def3);
     * return vn1;
     * ```
     */
    QWeb.addDirective({
        name: "component",
        extraNames: ["props"],
        priority: 100,
        atNodeEncounter({ ctx, value, node, qweb }) {
            ctx.addLine(`// Component '${value}'`);
            ctx.rootContext.shouldDefineQWeb = true;
            ctx.rootContext.shouldDefineParent = true;
            ctx.rootContext.shouldDefineUtils = true;
            ctx.rootContext.shouldDefineScope = true;
            let hasDynamicProps = node.getAttribute("t-props") ? true : false;
            // t-on- events and t-transition
            const events = [];
            let transition = "";
            const attributes = node.attributes;
            const props = {};
            for (let i = 0; i < attributes.length; i++) {
                const name = attributes[i].name;
                const value = attributes[i].textContent;
                if (name.startsWith("t-on-")) {
                    events.push([name, value]);
                }
                else if (name === "t-transition") {
                    if (QWeb.enableTransitions) {
                        transition = value;
                    }
                }
                else if (!name.startsWith("t-")) {
                    if (name !== "class" && name !== "style") {
                        // this is a prop!
                        if (value.includes("=>")) {
                            props[name] = ctx.captureExpression(value);
                        }
                        else {
                            props[name] = ctx.formatExpression(value) || "undefined";
                        }
                    }
                }
            }
            // computing the props string representing the props object
            let propStr = Object.keys(props)
                .map((k) => k + ":" + props[k])
                .join(",");
            let componentID = ctx.generateID();
            let hasDefinedKey = false;
            let templateKey;
            if (node.tagName === "t" && !node.hasAttribute("t-key") && value.match(INTERP_REGEXP)) {
                defineComponentKey();
                const id = ctx.generateID();
                // the ___ is to make sure we have no possible conflict with normal
                // template keys
                ctx.addLine(`let k${id} = '___' + componentKey${componentID}`);
                templateKey = `k${id}`;
            }
            else {
                templateKey = ctx.generateTemplateKey();
            }
            let ref = node.getAttribute("t-ref");
            let refExpr = "";
            let refKey = "";
            if (ref) {
                ctx.rootContext.shouldDefineRefs = true;
                refKey = `ref${ctx.generateID()}`;
                ctx.addLine(`const ${refKey} = ${ctx.interpolate(ref)};`);
                refExpr = `context.__owl__.refs[${refKey}] = w${componentID};`;
            }
            let finalizeComponentCode = `w${componentID}.destroy();`;
            if (ref) {
                finalizeComponentCode += `delete context.__owl__.refs[${refKey}];`;
            }
            if (transition) {
                finalizeComponentCode = `let finalize = () => {
          ${finalizeComponentCode}
        };
        delete w${componentID}.__owl__.transitionInserted;
        utils.transitionRemove(vn, '${transition}', finalize);`;
            }
            let createHook = "";
            let classAttr = node.getAttribute("class");
            let tattClass = node.getAttribute("t-att-class");
            let styleAttr = node.getAttribute("style");
            let tattStyle = node.getAttribute("t-att-style");
            if (tattStyle) {
                const attVar = `_${ctx.generateID()}`;
                ctx.addLine(`const ${attVar} = ${ctx.formatExpression(tattStyle)};`);
                tattStyle = attVar;
            }
            let classObj = "";
            if (classAttr || tattClass || styleAttr || tattStyle || events.length) {
                if (classAttr) {
                    let classDef = classAttr
                        .trim()
                        .split(/\s+/)
                        .map((a) => `'${a}':true`)
                        .join(",");
                    classObj = `_${ctx.generateID()}`;
                    ctx.addLine(`let ${classObj} = {${classDef}};`);
                }
                if (tattClass) {
                    let tattExpr = ctx.formatExpression(tattClass);
                    if (tattExpr[0] !== "{" || tattExpr[tattExpr.length - 1] !== "}") {
                        tattExpr = `utils.toClassObj(${tattExpr})`;
                    }
                    if (classAttr) {
                        ctx.addLine(`Object.assign(${classObj}, ${tattExpr})`);
                    }
                    else {
                        classObj = `_${ctx.generateID()}`;
                        ctx.addLine(`let ${classObj} = ${tattExpr};`);
                    }
                }
                let eventsCode = events
                    .map(function ([name, value]) {
                    const capture = name.match(/\.capture/);
                    name = capture ? name.replace(/\.capture/, "") : name;
                    const { event, handler } = makeHandlerCode(ctx, name, value, false, T_COMPONENT_MODS_CODE);
                    if (capture) {
                        return `vn.elm.addEventListener('${event}', ${handler}, true);`;
                    }
                    return `vn.elm.addEventListener('${event}', ${handler});`;
                })
                    .join("");
                const styleExpr = tattStyle || (styleAttr ? `'${styleAttr}'` : false);
                const styleCode = styleExpr ? `vn.elm.style = ${styleExpr};` : "";
                createHook = `utils.assignHooks(vnode.data, {create(_, vn){${styleCode}${eventsCode}}});`;
            }
            ctx.addLine(`let w${componentID} = ${templateKey} in parent.__owl__.cmap ? parent.__owl__.children[parent.__owl__.cmap[${templateKey}]] : false;`);
            let shouldProxy = !ctx.parentNode;
            if (shouldProxy) {
                let id = ctx.generateID();
                ctx.rootContext.rootNode = id;
                shouldProxy = true;
                ctx.rootContext.shouldDefineResult = true;
                ctx.addLine(`let vn${id} = {};`);
                ctx.addLine(`result = vn${id};`);
            }
            if (hasDynamicProps) {
                const dynamicProp = ctx.formatExpression(node.getAttribute("t-props"));
                ctx.addLine(`let props${componentID} = Object.assign({}, ${dynamicProp}, {${propStr}});`);
            }
            else {
                ctx.addLine(`let props${componentID} = {${propStr}};`);
            }
            ctx.addIf(`w${componentID} && w${componentID}.__owl__.currentFiber && !w${componentID}.__owl__.vnode`);
            ctx.addLine(`w${componentID}.destroy();`);
            ctx.addLine(`w${componentID} = false;`);
            ctx.closeIf();
            let registerCode = "";
            if (shouldProxy) {
                registerCode = `utils.defineProxy(vn${ctx.rootNode}, pvnode);`;
            }
            // SLOTS
            const hasSlots = node.childNodes.length;
            let scope = hasSlots ? `utils.combine(context, scope)` : "undefined";
            ctx.addIf(`w${componentID}`);
            // need to update component
            let styleCode = "";
            if (tattStyle) {
                styleCode = `.then(()=>{if (w${componentID}.__owl__.status === ${5 /* DESTROYED */}) {return};w${componentID}.el.style=${tattStyle};});`;
            }
            ctx.addLine(`w${componentID}.__updateProps(props${componentID}, extra.fiber, ${scope})${styleCode};`);
            ctx.addLine(`let pvnode = w${componentID}.__owl__.pvnode;`);
            if (registerCode) {
                ctx.addLine(registerCode);
            }
            if (ctx.parentNode) {
                ctx.addLine(`c${ctx.parentNode}.push(pvnode);`);
            }
            ctx.addElse();
            // new component
            function defineComponentKey() {
                if (!hasDefinedKey) {
                    const interpValue = ctx.interpolate(value);
                    ctx.addLine(`let componentKey${componentID} = ${interpValue};`);
                    hasDefinedKey = true;
                }
            }
            defineComponentKey();
            const contextualValue = value.match(INTERP_REGEXP) ? "false" : ctx.formatExpression(value);
            ctx.addLine(`let W${componentID} = ${contextualValue} || context.constructor.components[componentKey${componentID}] || QWeb.components[componentKey${componentID}];`);
            // maybe only do this in dev mode...
            ctx.addLine(`if (!W${componentID}) {throw new Error('Cannot find the definition of component "' + componentKey${componentID} + '"')}`);
            ctx.addLine(`w${componentID} = new W${componentID}(parent, props${componentID});`);
            if (transition) {
                ctx.addLine(`const __patch${componentID} = w${componentID}.__patch;`);
                ctx.addLine(`w${componentID}.__patch = (t, vn) => {__patch${componentID}.call(w${componentID}, t, vn); if(!w${componentID}.__owl__.transitionInserted){w${componentID}.__owl__.transitionInserted = true;utils.transitionInsert(w${componentID}.__owl__.vnode, '${transition}');}};`);
            }
            ctx.addLine(`parent.__owl__.cmap[${templateKey}] = w${componentID}.__owl__.id;`);
            if (hasSlots) {
                const clone = node.cloneNode(true);
                // The next code is a fallback for compatibility reason. It accepts t-set
                // elements that are direct children with a non empty body as nodes defining
                // the content of a slot.
                //
                // This is wrong, but is necessary to prevent breaking all existing Owl
                // code using slots. This will be removed in v2.0 someday. Meanwhile,
                // please use t-set-slot everywhere you need to set the content of a
                // slot.
                for (let node of clone.children) {
                    if (node.hasAttribute("t-set") && node.hasChildNodes()) {
                        node.setAttribute("t-set-slot", node.getAttribute("t-set"));
                        node.removeAttribute("t-set");
                    }
                }
                const slotNodes = Array.from(clone.querySelectorAll("[t-set-slot]"));
                const slotNames = new Set();
                const slotId = QWeb.nextSlotId++;
                ctx.addLine(`w${componentID}.__owl__.slotId = ${slotId};`);
                if (slotNodes.length) {
                    for (let i = 0, length = slotNodes.length; i < length; i++) {
                        const slotNode = slotNodes[i];
                        // check if this is defined in a sub component (in which case it should
                        // be ignored)
                        let el = slotNode.parentElement;
                        let isInSubComponent = false;
                        while (el !== clone) {
                            if (el.hasAttribute("t-component") ||
                                el.tagName[0] === el.tagName[0].toUpperCase()) {
                                isInSubComponent = true;
                                break;
                            }
                            el = el.parentElement;
                        }
                        if (isInSubComponent) {
                            continue;
                        }
                        let key = slotNode.getAttribute("t-set-slot");
                        if (slotNames.has(key)) {
                            continue;
                        }
                        slotNames.add(key);
                        slotNode.removeAttribute("t-set-slot");
                        slotNode.parentElement.removeChild(slotNode);
                        const slotFn = qweb._compile(`slot_${key}_template`, { elem: slotNode, hasParent: true });
                        QWeb.slots[`${slotId}_${key}`] = slotFn;
                    }
                }
                if (clone.childNodes.length) {
                    let hasContent = false;
                    const t = clone.ownerDocument.createElement("t");
                    for (let child of Object.values(clone.childNodes)) {
                        hasContent =
                            hasContent || (child instanceof Text ? Boolean(child.textContent.trim().length) : true);
                        t.appendChild(child);
                    }
                    if (hasContent) {
                        const slotFn = qweb._compile(`slot_default_template`, { elem: t, hasParent: true });
                        QWeb.slots[`${slotId}_default`] = slotFn;
                    }
                }
            }
            ctx.addLine(`let fiber = w${componentID}.__prepare(extra.fiber, ${scope}, () => { const vnode = fiber.vnode; pvnode.sel = vnode.sel; ${createHook}});`);
            // hack: specify empty remove hook to prevent the node from being removed from the DOM
            const insertHook = refExpr ? `insert(vn) {${refExpr}},` : "";
            ctx.addLine(`let pvnode = h('dummy', {key: ${templateKey}, hook: {${insertHook}remove() {},destroy(vn) {${finalizeComponentCode}}}});`);
            if (registerCode) {
                ctx.addLine(registerCode);
            }
            if (ctx.parentNode) {
                ctx.addLine(`c${ctx.parentNode}.push(pvnode);`);
            }
            ctx.addLine(`w${componentID}.__owl__.pvnode = pvnode;`);
            ctx.closeIf();
            if (classObj) {
                ctx.addLine(`w${componentID}.__owl__.classObj=${classObj};`);
            }
            ctx.addLine(`w${componentID}.__owl__.parentLastFiberId = extra.fiber.id;`);
            return true;
        },
    });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    // -----------------------------------------------------------------------------
    //  Scheduler
    // -----------------------------------------------------------------------------
    class Scheduler {
        constructor() {
            this.tasks = new Set();
            this.frame = 0;
            this.delayedRenders = [];
            this.cancelledNodes = new Set();
            this.requestAnimationFrame = Scheduler.requestAnimationFrame;
        }
        addFiber(fiber) {
            this.tasks.add(fiber.root);
        }
        scheduleDestroy(node) {
            this.cancelledNodes.add(node);
            if (this.frame === 0) {
                this.frame = this.requestAnimationFrame(() => this.processTasks());
            }
        }
        /**
         * Process all current tasks. This only applies to the fibers that are ready.
         * Other tasks are left unchanged.
         */
        flush() {
<<<<<<< HEAD
            if (this.delayedRenders.length) {
                let renders = this.delayedRenders;
                this.delayedRenders = [];
                for (let f of renders) {
                    if (f.root && f.node.status !== 3 /* DESTROYED */ && f.node.fiber === f) {
                        f.render();
=======
            let tasks = this.tasks;
            this.tasks = [];
            tasks = tasks.filter((task) => {
                if (task.fiber.isCompleted) {
                    task.callback();
                    return false;
                }
                if (task.fiber.counter === 0) {
                    if (!task.fiber.error) {
                        try {
                            task.fiber.complete();
                        }
                        catch (e) {
                            task.fiber.handleError(e);
                        }
                    }
                    task.callback();
                    return false;
                }
                return true;
            });
            this.tasks = tasks.concat(this.tasks);
            if (this.tasks.length === 0) {
                this.stop();
            }
        }
        scheduleTasks() {
            this.requestAnimationFrame(() => {
                this.flush();
                if (this.isRunning) {
                    this.scheduleTasks();
                }
            });
        }
    }
    const scheduler = new Scheduler(browser.requestAnimationFrame);

    /**
     * Owl Fiber Class
     *
     * Fibers are small abstractions designed to contain all the internal state
     * associated with a "rendering work unit", relative to a specific component.
     *
     * A rendering will cause the creation of a fiber for each impacted components.
     *
     * Fibers capture all that necessary information, which is critical to owl
     * asynchronous rendering pipeline. Fibers can be cancelled, can be in different
     * states and in general determine the state of the rendering.
     */
    class Fiber {
        constructor(parent, component, force, target, position) {
            this.id = Fiber.nextId++;
            // isCompleted means that the rendering corresponding to this fiber's work is
            // done, either because the component has been mounted or patched, or because
            // fiber has been cancelled.
            this.isCompleted = false;
            // the fibers corresponding to component updates (updateProps) need to call
            // the willPatch and patched hooks from the corresponding component. However,
            // fibers corresponding to a new component do not need to do that. So, the
            // shouldPatch hook is the boolean that we check whenever we need to apply
            // a patch.
            this.shouldPatch = true;
            // isRendered is the last state of a fiber. If true, this means that it has
            // been rendered and is inert (so, it should not be taken into account when
            // counting the number of active fibers).
            this.isRendered = false;
            // the counter number is a critical information. It is only necessary for a
            // root fiber.  For that fiber, this number counts the number of active sub
            // fibers.  When that number reaches 0, the fiber can be applied by the
            // scheduler.
            this.counter = 0;
            this.vnode = null;
            this.child = null;
            this.sibling = null;
            this.lastChild = null;
            this.parent = null;
            this.component = component;
            this.force = force;
            this.target = target;
            this.position = position;
            const __owl__ = component.__owl__;
            this.scope = __owl__.scope;
            this.root = parent ? parent.root : this;
            this.parent = parent;
            let oldFiber = __owl__.currentFiber;
            if (oldFiber && !oldFiber.isCompleted) {
                this.force = true;
                if (oldFiber.root === oldFiber && !parent) {
                    // both oldFiber and this fiber are root fibers
                    this._reuseFiber(oldFiber);
                    return oldFiber;
                }
                else {
                    this._remapFiber(oldFiber);
                }
            }
            this.root.counter++;
            __owl__.currentFiber = this;
        }
        /**
         * When the oldFiber is not completed yet, and both oldFiber and this fiber
         * are root fibers, we want to reuse the oldFiber instead of creating a new
         * one. Doing so will guarantee that the initiator(s) of those renderings will
         * be notified (the promise will resolve) when the last rendering will be done.
         *
         * This function thus assumes that oldFiber is a root fiber.
         */
        _reuseFiber(oldFiber) {
            oldFiber.cancel(); // cancel children fibers
            oldFiber.target = this.target || oldFiber.target;
            oldFiber.position = this.position || oldFiber.position;
            oldFiber.isCompleted = false; // keep the root fiber alive
            oldFiber.isRendered = false; // the fiber has to be re-rendered
            if (oldFiber.child) {
                // remove relation to children
                oldFiber.child.parent = null;
                oldFiber.child = null;
                oldFiber.lastChild = null;
            }
            oldFiber.counter = 1; // re-initialize counter
            oldFiber.id = Fiber.nextId++;
        }
        /**
         * In some cases, a rendering initiated at some component can detect that it
         * should be part of a larger rendering initiated somewhere up the component
         * tree.  In that case, it needs to cancel the previous rendering and
         * remap itself as a part of the current parent rendering.
         */
        _remapFiber(oldFiber) {
            oldFiber.cancel();
            this.shouldPatch = oldFiber.shouldPatch;
            if (oldFiber === oldFiber.root) {
                oldFiber.counter++;
            }
            if (oldFiber.parent && !this.parent) {
                // re-map links
                this.parent = oldFiber.parent;
                this.root = this.parent.root;
                this.sibling = oldFiber.sibling;
                if (this.parent.lastChild === oldFiber) {
                    this.parent.lastChild = this;
                }
                if (this.parent.child === oldFiber) {
                    this.parent.child = this;
                }
                else {
                    let current = this.parent.child;
                    while (true) {
                        if (current.sibling === oldFiber) {
                            current.sibling = this;
                            break;
                        }
                        current = current.sibling;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                    }
                }
            }
            if (this.frame === 0) {
                this.frame = this.requestAnimationFrame(() => this.processTasks());
            }
        }
<<<<<<< HEAD
        processTasks() {
            this.frame = 0;
            for (let node of this.cancelledNodes) {
                node._destroy();
            }
            this.cancelledNodes.clear();
            for (let task of this.tasks) {
                this.processFiber(task);
            }
            for (let task of this.tasks) {
                if (task.node.status === 3 /* DESTROYED */) {
                    this.tasks.delete(task);
                }
            }
        }
        processFiber(fiber) {
            if (fiber.root !== fiber) {
                this.tasks.delete(fiber);
                return;
            }
            const hasError = fibersInError.has(fiber);
            if (hasError && fiber.counter !== 0) {
                this.tasks.delete(fiber);
                return;
            }
            if (fiber.node.status === 3 /* DESTROYED */) {
                this.tasks.delete(fiber);
                return;
=======
        /**
         * Successfully complete the work of the fiber: call the mount or patch hooks
         * and patch the DOM. This function is called once the fiber and its children
         * are ready, and the scheduler decides to process it.
         */
        complete() {
            let component = this.component;
            this.isCompleted = true;
            const status = component.__owl__.status;
            if (status === 5 /* DESTROYED */) {
                return;
            }
            // build patchQueue
            const patchQueue = [];
            const doWork = function (f) {
                f.component.__owl__.currentFiber = null;
                patchQueue.push(f);
                return f.child;
            };
            this._walk(doWork);
            const patchLen = patchQueue.length;
            // call willPatch hook on each fiber of patchQueue
            if (status === 3 /* MOUNTED */) {
                for (let i = 0; i < patchLen; i++) {
                    const fiber = patchQueue[i];
                    if (fiber.shouldPatch) {
                        component = fiber.component;
                        if (component.__owl__.willPatchCB) {
                            component.__owl__.willPatchCB();
                        }
                        component.willPatch();
                    }
                }
            }
            // call __patch on each fiber of (reversed) patchQueue
            for (let i = patchLen - 1; i >= 0; i--) {
                const fiber = patchQueue[i];
                component = fiber.component;
                if (fiber.target && i === 0) {
                    let target;
                    if (fiber.position === "self") {
                        target = fiber.target;
                        if (target.tagName.toLowerCase() !== fiber.vnode.sel) {
                            throw new Error(`Cannot attach '${component.constructor.name}' to target node (not same tag name)`);
                        }
                        // In self mode, we *know* we are to take possession of the target
                        // Hence we manually create the corresponding VNode and copy the "key" in data
                        const selfVnodeData = fiber.vnode.data ? { key: fiber.vnode.data.key } : {};
                        const selfVnode = h(fiber.vnode.sel, selfVnodeData);
                        selfVnode.elm = target;
                        target = selfVnode;
                    }
                    else {
                        target = component.__owl__.vnode || document.createElement(fiber.vnode.sel);
                    }
                    component.__patch(target, fiber.vnode);
                }
                else {
                    const vnode = component.__owl__.vnode;
                    if (fiber.shouldPatch && vnode) {
                        component.__patch(vnode, fiber.vnode);
                        // When updating a Component's props (in directive),
                        // the component has a pvnode AND should be patched.
                        // However, its pvnode.elm may have changed if it is a High Order Component
                        if (component.__owl__.pvnode) {
                            component.__owl__.pvnode.elm = component.__owl__.vnode.elm;
                        }
                    }
                    else {
                        component.__patch(document.createElement(fiber.vnode.sel), fiber.vnode);
                        component.__owl__.pvnode.elm = component.__owl__.vnode.elm;
                    }
                }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
            if (fiber.counter === 0) {
                if (!hasError) {
                    fiber.complete();
                }
<<<<<<< HEAD
                this.tasks.delete(fiber);
=======
                inDOM = document.body.contains(this.component.el);
                this.component.env.qweb.trigger("dom-appended");
            }
            // call patched/mounted hook on each fiber of (reversed) patchQueue
            if (status === 3 /* MOUNTED */ || inDOM) {
                for (let i = patchLen - 1; i >= 0; i--) {
                    const fiber = patchQueue[i];
                    component = fiber.component;
                    if (fiber.shouldPatch && !this.target) {
                        component.patched();
                        if (component.__owl__.patchedCB) {
                            component.__owl__.patchedCB();
                        }
                    }
                    else {
                        component.__callMounted();
                    }
                }
            }
            else {
                for (let i = patchLen - 1; i >= 0; i--) {
                    const fiber = patchQueue[i];
                    component = fiber.component;
                    component.__owl__.status = 4 /* UNMOUNTED */;
                }
            }
        }
        /**
         * Cancel a fiber and all its children.
         */
        cancel() {
            this._walk((f) => {
                if (!f.isRendered) {
                    f.root.counter--;
                }
                f.isCompleted = true;
                return f.child;
            });
        }
        /**
         * This is the global error handler for errors occurring in Owl main lifecycle
         * methods.  Caught errors are triggered on the QWeb instance, and are
         * potentially given to some parent component which implements `catchError`.
         *
         * If there are no such component, we destroy everything. This is better than
         * being in a corrupted state.
         */
        handleError(error) {
            let component = this.component;
            this.vnode = component.__owl__.vnode || h("div");
            const qweb = component.env.qweb;
            let root = component;
            function handle(error) {
                let canCatch = false;
                qweb.trigger("error", error);
                while (component && !(canCatch = !!component.catchError)) {
                    root = component;
                    component = component.__owl__.parent;
                }
                if (canCatch) {
                    try {
                        component.catchError(error);
                    }
                    catch (e) {
                        root = component;
                        component = component.__owl__.parent;
                        return handle(e);
                    }
                    return true;
                }
                return false;
            }
            let isHandled = handle(error);
            if (!isHandled) {
                // the 3 next lines aim to mark the root fiber as being in error, and
                // to force it to end, without waiting for its children
                this.root.counter = 0;
                this.root.error = error;
                scheduler.flush();
                // at this point, the state of the application is corrupted and we could
                // have a lot of issues or crashes. So we destroy the application in a try
                // catch and swallow these errors because the fiber is already in error,
                // and this is the actual issue that needs to be solved, not those followup
                // errors.
                try {
                    root.destroy();
                }
                catch (e) { }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        }
    }
    // capture the value of requestAnimationFrame as soon as possible, to avoid
    // interactions with other code, such as test frameworks that override them
    Scheduler.requestAnimationFrame = window.requestAnimationFrame.bind(window);

<<<<<<< HEAD
    let hasBeenLogged = false;
    const DEV_MSG = () => {
        const hash = window.owl ? window.owl.__info__.hash : "master";
        return `Owl is running in 'dev' mode.

This is not suitable for production use.
See https://github.com/odoo/owl/blob/${hash}/doc/reference/app.md#configuration for more information.`;
    };
    const apps = new Set();
    window.__OWL_DEVTOOLS__ || (window.__OWL_DEVTOOLS__ = { apps, Fiber, RootFiber, toRaw, reactive });
    class App extends TemplateSet {
        constructor(Root, config = {}) {
            super(config);
            this.scheduler = new Scheduler();
            this.root = null;
            this.name = config.name || "";
            this.Root = Root;
            apps.add(this);
            if (config.test) {
                this.dev = true;
            }
            this.warnIfNoStaticProps = config.warnIfNoStaticProps || false;
            if (this.dev && !config.test && !hasBeenLogged) {
                console.info(DEV_MSG());
                hasBeenLogged = true;
            }
            const env = config.env || {};
            const descrs = Object.getOwnPropertyDescriptors(env);
            this.env = Object.freeze(Object.create(Object.getPrototypeOf(env), descrs));
            this.props = config.props || {};
        }
        mount(target, options) {
            App.validateTarget(target);
            if (this.dev) {
                validateProps(this.Root, this.props, { __owl__: { app: this } });
            }
            const node = this.makeNode(this.Root, this.props);
            const prom = this.mountNode(node, target, options);
            this.root = node;
            return prom;
        }
        makeNode(Component, props) {
            return new ComponentNode(Component, props, this, null, null);
        }
        mountNode(node, target, options) {
            const promise = new Promise((resolve, reject) => {
                let isResolved = false;
                // manually set a onMounted callback.
                // that way, we are independant from the current node.
                node.mounted.push(() => {
                    resolve(node.component);
                    isResolved = true;
                });
                // Manually add the last resort error handler on the node
                let handlers = nodeErrorHandlers.get(node);
                if (!handlers) {
                    handlers = [];
                    nodeErrorHandlers.set(node, handlers);
                }
                handlers.unshift((e) => {
                    if (!isResolved) {
                        reject(e);
                    }
                    throw e;
                });
=======
    //------------------------------------------------------------------------------
    // Prop validation helper
    //------------------------------------------------------------------------------
    /**
     * Validate the component props (or next props) against the (static) props
     * description.  This is potentially an expensive operation: it may needs to
     * visit recursively the props and all the children to check if they are valid.
     * This is why it is only done in 'dev' mode.
     */
    QWeb.utils.validateProps = function (Widget, props) {
        const propsDef = Widget.props;
        if (propsDef instanceof Array) {
            // list of strings (prop names)
            for (let i = 0, l = propsDef.length; i < l; i++) {
                const propName = propsDef[i];
                if (propName[propName.length - 1] === "?") {
                    // optional prop
                    break;
                }
                if (!(propName in props)) {
                    throw new Error(`Missing props '${propsDef[i]}' (component '${Widget.name}')`);
                }
            }
            for (let key in props) {
                if (!propsDef.includes(key) && !propsDef.includes(key + "?")) {
                    throw new Error(`Unknown prop '${key}' given to component '${Widget.name}'`);
                }
            }
        }
        else if (propsDef) {
            // propsDef is an object now
            for (let propName in propsDef) {
                if (props[propName] === undefined) {
                    if (propsDef[propName] && !propsDef[propName].optional) {
                        throw new Error(`Missing props '${propName}' (component '${Widget.name}')`);
                    }
                    else {
                        continue;
                    }
                }
                let whyInvalid;
                try {
                    whyInvalid = whyInvalidProp(props[propName], propsDef[propName]);
                }
                catch (e) {
                    e.message = `Invalid prop '${propName}' in component ${Widget.name} (${e.message})`;
                    throw e;
                }
                if (whyInvalid !== null) {
                    whyInvalid = whyInvalid.replace(/\${propName}/g, propName);
                    throw new Error(`Invalid Prop '${propName}' in component '${Widget.name}': ${whyInvalid}`);
                }
            }
            for (let propName in props) {
                if (!(propName in propsDef)) {
                    throw new Error(`Unknown prop '${propName}' given to component '${Widget.name}'`);
                }
            }
        }
    };
    /**
     * Check why an invidual prop value doesn't match its (static) prop definition
     */
    function whyInvalidProp(prop, propDef) {
        if (propDef === true) {
            return null;
        }
        if (typeof propDef === "function") {
            // Check if a value is constructed by some Constructor.  Note that there is a
            // slight abuse of language: we want to consider primitive values as well.
            //
            // So, even though 1 is not an instance of Number, we want to consider that
            // it is valid.
            if (typeof prop === "object") {
                if (prop instanceof propDef) {
                    return null;
                }
                return `\${propName} is not an instance of ${propDef.name}`;
            }
            if (typeof prop === propDef.name.toLowerCase()) {
                return null;
            }
            return `type of \${propName} is not ${propDef.name}`;
        }
        else if (propDef instanceof Array) {
            // If this code is executed, this means that we want to check if a prop
            // matches at least one of its descriptor.
            let reasons = [];
            for (let i = 0, iLen = propDef.length; i < iLen; i++) {
                const why = whyInvalidProp(prop, propDef[i]);
                if (why === null) {
                    return null;
                }
                reasons.push(why);
            }
            if (reasons.length > 1) {
                return reasons.slice(0, -1).join(", ") + " and " + reasons[reasons.length - 1];
            }
            else {
                return reasons[0];
            }
        }
        // propsDef is an object
        if (propDef.optional && prop === undefined) {
            return null;
        }
        if (propDef.type) {
            const why = whyInvalidProp(prop, propDef.type);
            if (why !== null) {
                return why;
            }
        }
        if (propDef.validate && !propDef.validate(prop)) {
            return "${propName} could not be validated by `validate` function";
        }
        if (propDef.type === Array && propDef.element) {
            for (let i = 0, iLen = prop.length; i < iLen; i++) {
                const why = whyInvalidProp(prop[i], propDef.element);
                if (why !== null) {
                    return why.replace(/\${propName}/g, `\${propName}[${i}]`);
                }
            }
        }
        if (propDef.type === Object && propDef.shape) {
            const shape = propDef.shape;
            for (let key in shape) {
                const why = whyInvalidProp(prop[key], shape[key]);
                if (why !== null) {
                    return why.replace(/\${propName}/g, `\${propName}['${key}']`);
                }
            }
            for (let propName in prop) {
                if (!(propName in shape)) {
                    return `unknown prop \${propName}['${propName}']`;
                }
            }
        }
        return null;
    }

    /**
     * Owl Style System
     *
     * This files contains the Owl code related to processing (extended) css strings
     * and creating/adding <style> tags to the document head.
     */
    const STYLESHEETS = {};
    function processSheet(str) {
        const tokens = str.split(/(\{|\}|;)/).map((s) => s.trim());
        const selectorStack = [];
        const parts = [];
        let rules = [];
        function generateSelector(stackIndex, parentSelector) {
            const parts = [];
            for (const selector of selectorStack[stackIndex]) {
                let part = (parentSelector && parentSelector + " " + selector) || selector;
                if (part.includes("&")) {
                    part = selector.replace(/&/g, parentSelector || "");
                }
                if (stackIndex < selectorStack.length - 1) {
                    part = generateSelector(stackIndex + 1, part);
                }
                parts.push(part);
            }
            return parts.join(", ");
        }
        function generateRules() {
            if (rules.length) {
                parts.push(generateSelector(0) + " {");
                parts.push(...rules);
                parts.push("}");
                rules = [];
            }
        }
        while (tokens.length) {
            let token = tokens.shift();
            if (token === "}") {
                generateRules();
                selectorStack.pop();
            }
            else {
                if (tokens[0] === "{") {
                    generateRules();
                    selectorStack.push(token.split(/\s*,\s*/));
                    tokens.shift();
                }
                if (tokens[0] === ";") {
                    rules.push("  " + token + ";");
                }
            }
        }
        return parts.join("\n");
    }
    function registerSheet(id, css) {
        const sheet = document.createElement("style");
        sheet.innerHTML = processSheet(css);
        STYLESHEETS[id] = sheet;
    }
    function activateSheet(id, name) {
        const sheet = STYLESHEETS[id];
        if (!sheet) {
            throw new Error(`Invalid css stylesheet for component '${name}'. Did you forget to use the 'css' tag helper?`);
        }
        sheet.setAttribute("component", name);
        document.head.appendChild(sheet);
    }

    var STATUS;
    (function (STATUS) {
        STATUS[STATUS["CREATED"] = 0] = "CREATED";
        STATUS[STATUS["WILLSTARTED"] = 1] = "WILLSTARTED";
        STATUS[STATUS["RENDERED"] = 2] = "RENDERED";
        STATUS[STATUS["MOUNTED"] = 3] = "MOUNTED";
        STATUS[STATUS["UNMOUNTED"] = 4] = "UNMOUNTED";
        STATUS[STATUS["DESTROYED"] = 5] = "DESTROYED";
    })(STATUS || (STATUS = {}));
    const portalSymbol = Symbol("portal"); // FIXME
    //------------------------------------------------------------------------------
    // Component
    //------------------------------------------------------------------------------
    let nextId = 1;
    class Component {
        //--------------------------------------------------------------------------
        // Lifecycle
        //--------------------------------------------------------------------------
        /**
         * Creates an instance of Component.
         *
         * Note that most of the time, only the root component needs to be created by
         * hand.  Other components should be created automatically by the framework (with
         * the t-component directive in a template)
         */
        constructor(parent, props) {
            Component.current = this;
            let constr = this.constructor;
            const defaultProps = constr.defaultProps;
            if (defaultProps) {
                props = props || {};
                this.__applyDefaultProps(props, defaultProps);
            }
            this.props = props;
            if (QWeb.dev) {
                QWeb.utils.validateProps(constr, this.props);
            }
            const id = nextId++;
            let depth;
            if (parent) {
                this.env = parent.env;
                const __powl__ = parent.__owl__;
                __powl__.children[id] = this;
                depth = __powl__.depth + 1;
            }
            else {
                // we are the root component
                this.env = this.constructor.env;
                if (!this.env.qweb) {
                    this.env.qweb = new QWeb();
                }
                // TODO: remove this in owl 2.0
                if (!this.env.browser) {
                    this.env.browser = browser;
                }
                this.env.qweb.on("update", this, () => {
                    switch (this.__owl__.status) {
                        case 3 /* MOUNTED */:
                            this.render(true);
                            break;
                        case 5 /* DESTROYED */:
                            // this is unlikely to happen, but if a root widget is destroyed,
                            // we want to remove our subscription.  The usual way to do that
                            // would be to perform some check in the destroy method, but since
                            // it is very performance sensitive, and since this is a rare event,
                            // we simply do it lazily
                            this.env.qweb.off("update", this);
                            break;
                    }
                });
                depth = 0;
            }
            const qweb = this.env.qweb;
            const template = constr.template || this.__getTemplate(qweb);
            this.__owl__ = {
                id: id,
                depth: depth,
                vnode: null,
                pvnode: null,
                status: 0 /* CREATED */,
                parent: parent || null,
                children: {},
                cmap: {},
                currentFiber: null,
                parentLastFiberId: 0,
                boundHandlers: {},
                mountedCB: null,
                willUnmountCB: null,
                willPatchCB: null,
                patchedCB: null,
                willStartCB: null,
                willUpdatePropsCB: null,
                observer: null,
                renderFn: qweb.render.bind(qweb, template),
                classObj: null,
                refs: null,
                scope: null,
            };
            if (constr.style) {
                this.__applyStyles(constr);
            }
            this.setup();
        }
        /**
         * The `el` is the root element of the component.  Note that it could be null:
         * this is the case if the component is not mounted yet, or is destroyed.
         */
        get el() {
            return this.__owl__.vnode ? this.__owl__.vnode.elm : null;
        }
        /**
         * setup is run just after the component is constructed. This is the standard
         * location where the component can setup its hooks. It has some advantages
         * over the constructor:
         *  - it can be patched (useful in odoo ecosystem)
         *  - it does not need to propagate the arguments to the super call
         *
         * Note: this method should not be called manually.
         */
        setup() { }
        /**
         * willStart is an asynchronous hook that can be implemented to perform some
         * action before the initial rendering of a component.
         *
         * It will be called exactly once before the initial rendering. It is useful
         * in some cases, for example, to load external assets (such as a JS library)
         * before the component is rendered.
         *
         * Note that a slow willStart method will slow down the rendering of the user
         * interface.  Therefore, some effort should be made to make this method as
         * fast as possible.
         *
         * Note: this method should not be called manually.
         */
        async willStart() { }
        /**
         * mounted is a hook that is called each time a component is attached to the
         * DOM. This is a good place to add some listeners, or to interact with the
         * DOM, if the component needs to perform some measure for example.
         *
         * Note: this method should not be called manually.
         *
         * @see willUnmount
         */
        mounted() { }
        /**
         * The willUpdateProps is an asynchronous hook, called just before new props
         * are set. This is useful if the component needs some asynchronous task
         * performed, depending on the props (for example, assuming that the props are
         * some record Id, fetching the record data).
         *
         * This hook is not called during the first render (but willStart is called
         * and performs a similar job).
         */
        async willUpdateProps(nextProps) { }
        /**
         * The willPatch hook is called just before the DOM patching process starts.
         * It is not called on the initial render.  This is useful to get some
         * information which are in the DOM.  For example, the current position of the
         * scrollbar
         */
        willPatch() { }
        /**
         * This hook is called whenever a component did actually update its props,
         * state or env.
         *
         * This method is not called on the initial render. It is useful to interact
         * with the DOM (for example, through an external library) whenever the
         * component was updated.
         *
         * Updating the component state in this hook is possible, but not encouraged.
         * One need to be careful, because updates here will cause rerender, which in
         * turn will cause other calls to updated. So, we need to be particularly
         * careful at avoiding endless cycles.
         */
        patched() { }
        /**
         * willUnmount is a hook that is called each time just before a component is
         * unmounted from the DOM. This is a good place to remove some listeners, for
         * example.
         *
         * Note: this method should not be called manually.
         *
         * @see mounted
         */
        willUnmount() { }
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
        /**
         * Mount the component to a target element.
         *
         * This should only be done if the component was created manually. Components
         * created declaratively in templates are managed by the Owl system.
         *
         * Note that a component can be mounted an unmounted several times
         */
        async mount(target, options = {}) {
            if (!(target instanceof HTMLElement || target instanceof DocumentFragment)) {
                let message = `Component '${this.constructor.name}' cannot be mounted: the target is not a valid DOM node.`;
                message += `\nMaybe the DOM is not ready yet? (in that case, you can use owl.utils.whenReady)`;
                throw new Error(message);
            }
            const position = options.position || "last-child";
            const __owl__ = this.__owl__;
            const currentFiber = __owl__.currentFiber;
            switch (__owl__.status) {
                case 0 /* CREATED */: {
                    const fiber = new Fiber(null, this, true, target, position);
                    fiber.shouldPatch = false;
                    this.__prepareAndRender(fiber, () => { });
                    return scheduler.addFiber(fiber);
                }
                case 1 /* WILLSTARTED */:
                case 2 /* RENDERED */:
                    currentFiber.target = target;
                    currentFiber.position = position;
                    return scheduler.addFiber(currentFiber);
                case 4 /* UNMOUNTED */: {
                    const fiber = new Fiber(null, this, true, target, position);
                    fiber.shouldPatch = false;
                    this.__render(fiber);
                    return scheduler.addFiber(fiber);
                }
                case 3 /* MOUNTED */: {
                    if (position !== "self" && this.el.parentNode !== target) {
                        const fiber = new Fiber(null, this, true, target, position);
                        fiber.shouldPatch = false;
                        this.__render(fiber);
                        return scheduler.addFiber(fiber);
                    }
                    else {
                        return Promise.resolve();
                    }
                }
                case 5 /* DESTROYED */:
                    throw new Error("Cannot mount a destroyed component");
            }
        }
        /**
         * The unmount method is the opposite of the mount method.  It is useful
         * to call willUnmount calls and remove the component from the DOM.
         */
        unmount() {
            if (this.__owl__.status === 3 /* MOUNTED */) {
                this.__callWillUnmount();
                this.el.remove();
            }
        }
        /**
         * The render method is the main entry point to render a component (once it
         * is ready. This method is not initially called when the component is
         * rendered the first time).
         *
         * This method will cause all its sub components to potentially rerender
         * themselves.  Note that `render` is not called if a component is updated via
         * its props.
         */
        async render(force = false) {
            const __owl__ = this.__owl__;
            const currentFiber = __owl__.currentFiber;
            if (!__owl__.vnode && !currentFiber) {
                return;
            }
            if (currentFiber && !currentFiber.isRendered && !currentFiber.isCompleted) {
                return scheduler.addFiber(currentFiber.root);
            }
            // if we aren't mounted at this point, it implies that there is a
            // currentFiber that is already rendered (isRendered is true), so we are
            // about to be mounted
            const status = __owl__.status;
            const fiber = new Fiber(null, this, force, null, null);
            Promise.resolve().then(() => {
                if (__owl__.status === 3 /* MOUNTED */ || status !== 3 /* MOUNTED */) {
                    if (fiber.isCompleted || fiber.isRendered) {
                        return;
                    }
                    this.__render(fiber);
                }
                else {
                    // we were mounted when render was called, but we aren't anymore, so we
                    // were actually about to be unmounted ; we can thus forget about this
                    // fiber
                    fiber.isCompleted = true;
                    __owl__.currentFiber = null;
                }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            });
            node.mountComponent(target, options);
            return promise;
        }
        destroy() {
<<<<<<< HEAD
            if (this.root) {
                this.root.destroy();
                this.scheduler.processTasks();
=======
            const __owl__ = this.__owl__;
            if (__owl__.status !== 5 /* DESTROYED */) {
                const el = this.el;
                this.__destroy(__owl__.parent);
                if (el) {
                    el.remove();
                }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
            apps.delete(this);
        }
<<<<<<< HEAD
        createComponent(name, isStatic, hasSlotsProp, hasDynamicPropList, propList) {
            const isDynamic = !isStatic;
            let arePropsDifferent;
            const hasNoProp = propList.length === 0;
            if (hasSlotsProp) {
                arePropsDifferent = (_1, _2) => true;
            }
            else if (hasDynamicPropList) {
                arePropsDifferent = function (props1, props2) {
                    for (let k in props1) {
                        if (props1[k] !== props2[k]) {
                            return true;
                        }
                    }
                    return Object.keys(props1).length !== Object.keys(props2).length;
=======
        /**
         * This method is called by the component system whenever its props are
         * updated. If it returns true, then the component will be rendered.
         * Otherwise, it will skip the rendering (also, its props will not be updated)
         */
        shouldUpdate(nextProps) {
            return true;
        }
        /**
         * Emit a custom event of type 'eventType' with the given 'payload' on the
         * component's el, if it exists. However, note that the event will only bubble
         * up to the parent DOM nodes. Thus, it must be called between mounted() and
         * willUnmount().
         */
        trigger(eventType, payload) {
            this.__trigger(this, eventType, payload);
        }
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        /**
         * Private helper to perform a full destroy, from the point of view of an Owl
         * component. It does not remove the el (this is done only once on the top
         * level destroyed component, for performance reasons).
         *
         * The job of this method is mostly to call willUnmount hooks, and to perform
         * all necessary internal cleanup.
         *
         * Note that it does not call the __callWillUnmount method to avoid visiting
         * all children many times.
         */
        __destroy(parent) {
            const __owl__ = this.__owl__;
            if (__owl__.status === 3 /* MOUNTED */) {
                if (__owl__.willUnmountCB) {
                    __owl__.willUnmountCB();
                }
                this.willUnmount();
                __owl__.status = 4 /* UNMOUNTED */;
            }
            const children = __owl__.children;
            for (let key in children) {
                children[key].__destroy(this);
            }
            if (parent) {
                let id = __owl__.id;
                delete parent.__owl__.children[id];
                __owl__.parent = null;
            }
            __owl__.status = 5 /* DESTROYED */;
            delete __owl__.vnode;
            if (__owl__.currentFiber) {
                __owl__.currentFiber.isCompleted = true;
            }
        }
        __callMounted() {
            const __owl__ = this.__owl__;
            __owl__.status = 3 /* MOUNTED */;
            this.mounted();
            if (__owl__.mountedCB) {
                __owl__.mountedCB();
            }
        }
        __callWillUnmount() {
            const __owl__ = this.__owl__;
            if (__owl__.willUnmountCB) {
                __owl__.willUnmountCB();
            }
            this.willUnmount();
            __owl__.status = 4 /* UNMOUNTED */;
            if (__owl__.currentFiber) {
                __owl__.currentFiber.isCompleted = true;
                __owl__.currentFiber.root.counter = 0;
            }
            const children = __owl__.children;
            for (let id in children) {
                const comp = children[id];
                if (comp.__owl__.status === 3 /* MOUNTED */) {
                    comp.__callWillUnmount();
                }
            }
        }
        /**
         * Private trigger method, allows to choose the component which triggered
         * the event in the first place
         */
        __trigger(component, eventType, payload) {
            if (this.el) {
                const ev = new OwlEvent(component, eventType, {
                    bubbles: true,
                    cancelable: true,
                    detail: payload,
                });
                const triggerHook = this.env[portalSymbol];
                if (triggerHook) {
                    triggerHook(ev);
                }
                this.el.dispatchEvent(ev);
            }
        }
        /**
         * The __updateProps method is called by the t-component directive whenever
         * it updates a component (so, when the parent template is rerendered).
         */
        async __updateProps(nextProps, parentFiber, scope) {
            this.__owl__.scope = scope;
            const shouldUpdate = parentFiber.force || this.shouldUpdate(nextProps);
            if (shouldUpdate) {
                const __owl__ = this.__owl__;
                const fiber = new Fiber(parentFiber, this, parentFiber.force, null, null);
                if (!parentFiber.child) {
                    parentFiber.child = fiber;
                }
                else {
                    parentFiber.lastChild.sibling = fiber;
                }
                parentFiber.lastChild = fiber;
                const defaultProps = this.constructor.defaultProps;
                if (defaultProps) {
                    this.__applyDefaultProps(nextProps, defaultProps);
                }
                if (QWeb.dev) {
                    QWeb.utils.validateProps(this.constructor, nextProps);
                }
                await Promise.all([
                    this.willUpdateProps(nextProps),
                    __owl__.willUpdatePropsCB && __owl__.willUpdatePropsCB(nextProps),
                ]);
                if (fiber.isCompleted) {
                    return;
                }
                this.props = nextProps;
                this.__render(fiber);
            }
        }
        /**
         * Main patching method. We call the virtual dom patch method here to convert
         * a virtual dom vnode into some actual dom.
         */
        __patch(target, vnode) {
            this.__owl__.vnode = patch(target, vnode);
        }
        /**
         * The __prepare method is only called by the t-component directive, when a
         * subcomponent is created. It gets its scope, if any, from the
         * parent template.
         */
        __prepare(parentFiber, scope, cb) {
            this.__owl__.scope = scope;
            const fiber = new Fiber(parentFiber, this, parentFiber.force, null, null);
            fiber.shouldPatch = false;
            if (!parentFiber.child) {
                parentFiber.child = fiber;
            }
            else {
                parentFiber.lastChild.sibling = fiber;
            }
            parentFiber.lastChild = fiber;
            this.__prepareAndRender(fiber, cb);
            return fiber;
        }
        /**
         * Apply the stylesheets defined by the component. Note that we need to make
         * sure all inherited stylesheets are applied as well.  We then delete the
         * `style` key from the constructor to make sure we do not apply it again.
         */
        __applyStyles(constr) {
            while (constr && constr.style) {
                if (constr.hasOwnProperty("style")) {
                    activateSheet(constr.style, constr.name);
                    delete constr.style;
                }
                constr = constr.__proto__;
            }
        }
        __getTemplate(qweb) {
            let p = this.constructor;
            if (!p.hasOwnProperty("_template")) {
                // here, the component and none of its superclasses defines a static `template`
                // key. So we fall back on looking for a template matching its name (or
                // one of its subclass).
                let template = p.name;
                while (!(template in qweb.templates) && p !== Component) {
                    p = p.__proto__;
                    template = p.name;
                }
                if (p === Component) {
                    throw new Error(`Could not find template for component "${this.constructor.name}"`);
                }
                else {
                    p._template = template;
                }
            }
            return p._template;
        }
        async __prepareAndRender(fiber, cb) {
            try {
                const proms = Promise.all([
                    this.willStart(),
                    this.__owl__.willStartCB && this.__owl__.willStartCB(),
                ]);
                this.__owl__.status = 1 /* WILLSTARTED */;
                await proms;
                if (this.__owl__.status === 5 /* DESTROYED */) {
                    return Promise.resolve();
                }
            }
            catch (e) {
                fiber.handleError(e);
                return Promise.resolve();
            }
            if (!fiber.isCompleted) {
                this.__render(fiber);
                this.__owl__.status = 2 /* RENDERED */;
                cb();
            }
        }
        __render(fiber) {
            const __owl__ = this.__owl__;
            if (__owl__.observer) {
                __owl__.observer.allowMutations = false;
            }
            let error;
            try {
                let vnode = __owl__.renderFn(this, {
                    handlers: __owl__.boundHandlers,
                    fiber: fiber,
                });
                // we iterate over the children to detect those that no longer belong to the
                // current rendering: those ones, if not mounted yet, can (and have to) be
                // destroyed right now, because they are not in the DOM, and thus we won't
                // be notified later on (when patching), that they are removed from the DOM
                for (let childKey in __owl__.children) {
                    const child = __owl__.children[childKey];
                    const childOwl = child.__owl__;
                    if (childOwl.status !== 3 /* MOUNTED */ && childOwl.parentLastFiberId < fiber.id) {
                        // we only do here a "soft" destroy, meaning that we leave the child
                        // dom node alone, without removing it.  Most of the time, it does not
                        // matter, because the child component is already unmounted.  However,
                        // if some of its parent have been unmounted, the child could actually
                        // still be attached to its parent, and this may be important if we
                        // want to remount the parent, because the vdom need to match the
                        // actual DOM
                        child.__destroy(childOwl.parent);
                        if (childOwl.pvnode) {
                            // we remove the key here to make sure that the patching algorithm
                            // is able to make the difference between this pvnode and an eventual
                            // other instance of the same component
                            delete childOwl.pvnode.key;
                            // Since the component has been unmounted, we do not want to actually
                            // call a remove hook.  This is pretty important, since the t-component
                            // directive actually disabled it, so the vdom algorithm will just
                            // not remove the child elm if we don't remove the hook.
                            delete childOwl.pvnode.data.hook.remove;
                        }
                    }
                }
                if (!vnode) {
                    throw new Error(`Rendering '${this.constructor.name}' did not return anything`);
                }
                fiber.vnode = vnode;
                // we apply here the class information described on the component by the
                // template (so, something like <MyComponent class="..."/>) to the actual
                // root vnode
                if (__owl__.classObj) {
                    const data = vnode.data;
                    data.class = Object.assign(data.class || {}, __owl__.classObj);
                }
            }
            catch (e) {
                error = e;
            }
            if (__owl__.observer) {
                __owl__.observer.allowMutations = true;
            }
            fiber.root.counter--;
            fiber.isRendered = true;
            if (error) {
                fiber.handleError(error);
            }
        }
        /**
         * Apply default props (only top level).
         *
         * Note that this method does modify in place the props
         */
        __applyDefaultProps(props, defaultProps) {
            for (let propName in defaultProps) {
                if (props[propName] === undefined) {
                    props[propName] = defaultProps[propName];
                }
            }
        }
    }
    Component.template = null;
    Component._template = null;
    Component.current = null;
    Component.components = {};
    Component.env = {};
    // expose scheduler s.t. it can be mocked for testing purposes
    Component.scheduler = scheduler;
    async function mount(C, params) {
        const { env, props, target } = params;
        let origEnv = C.hasOwnProperty("env") ? C.env : null;
        if (env) {
            C.env = env;
        }
        const component = new C(null, props);
        if (origEnv) {
            C.env = origEnv;
        }
        else {
            delete C.env;
        }
        const position = params.position || "last-child";
        await component.mount(target, { position });
        return component;
    }

    /**
     * The `Context` object provides a way to share data between an arbitrary number
     * of component. Usually, data is passed from a parent to its children component,
     * but when we have to deal with some mostly global information, this can be
     * annoying, since each component will need to pass the information to each
     * children, even though some or most of them will not use the information.
     *
     * With a `Context` object, each component can subscribe (with the `useContext`
     * hook) to its state, and will be updated whenever the context state is updated.
     */
    function partitionBy(arr, fn) {
        let lastGroup = false;
        let lastValue;
        return arr.reduce((acc, cur) => {
            let curVal = fn(cur);
            if (lastGroup) {
                if (curVal === lastValue) {
                    lastGroup.push(cur);
                }
                else {
                    lastGroup = false;
                }
            }
            if (!lastGroup) {
                lastGroup = [cur];
                acc.push(lastGroup);
            }
            lastValue = curVal;
            return acc;
        }, []);
    }
    class Context$1 extends EventBus {
        constructor(state = {}) {
            super();
            this.rev = 1;
            // mapping from component id to last observed context id
            this.mapping = {};
            this.observer = new Observer();
            this.observer.notifyCB = () => {
                // notify components in the next microtask tick to ensure that subscribers
                // are notified only once for all changes that occur in the same micro tick
                let rev = this.rev;
                return Promise.resolve().then(() => {
                    if (rev === this.rev) {
                        this.__notifyComponents();
                    }
                });
            };
            this.state = this.observer.observe(state);
            this.subscriptions.update = [];
        }
        /**
         * Instead of using trigger to emit an update event, we actually implement
         * our own function to do that.  The reason is that we need to be smarter than
         * a simple trigger function: we need to wait for parent components to be
         * done before doing children components.  More precisely, if an update
         * as an effect of destroying a children, we do not want to call any code
         * from the child, and certainly not render it.
         *
         * This method implements a simple grouping algorithm by depth. If we have
         * connected components of depths [2, 4,4,4,4, 3,8,8], the Context will notify
         * them in the following groups: [2], [4,4,4,4], [3], [8,8]. Each group will
         * be updated sequentially, but each components in a given group will be done in
         * parallel.
         *
         * This is a very simple algorithm, but it avoids checking if a given
         * component is a child of another.
         */
        async __notifyComponents() {
            const rev = ++this.rev;
            const subscriptions = this.subscriptions.update;
            const groups = partitionBy(subscriptions, (s) => (s.owner ? s.owner.__owl__.depth : -1));
            for (let group of groups) {
                const proms = group.map((sub) => sub.callback.call(sub.owner, rev));
                // at this point, each component in the current group has registered a
                // top level fiber in the scheduler. It could happen that rendering these
                // components is done (if they have no children).  This is why we manually
                // flush the scheduler.  This will force the scheduler to check
                // immediately if they are done, which will cause their rendering
                // promise to resolve earlier, which means that there is a chance of
                // processing the next group in the same frame.
                scheduler.flush();
                await Promise.all(proms);
            }
        }
    }
    /**
     * The`useContext` hook is the normal way for a component to register themselve
     * to context state changes. The `useContext` method returns the context state
     */
    function useContext(ctx) {
        const component = Component.current;
        return useContextWithCB(ctx, component, component.render.bind(component));
    }
    function useContextWithCB(ctx, component, method) {
        const __owl__ = component.__owl__;
        const id = __owl__.id;
        const mapping = ctx.mapping;
        if (id in mapping) {
            return ctx.state;
        }
        if (!__owl__.observer) {
            __owl__.observer = new Observer();
            __owl__.observer.notifyCB = component.render.bind(component);
        }
        mapping[id] = 0;
        const renderFn = __owl__.renderFn;
        __owl__.renderFn = function (comp, params) {
            mapping[id] = ctx.rev;
            return renderFn(comp, params);
        };
        ctx.on("update", component, async (contextRev) => {
            if (mapping[id] < contextRev) {
                mapping[id] = contextRev;
                await method();
            }
        });
        const __destroy = component.__destroy;
        component.__destroy = (parent) => {
            ctx.off("update", component);
            delete mapping[id];
            __destroy.call(component, parent);
        };
        return ctx.state;
    }

    /**
     * Owl Hook System
     *
     * This file introduces the concept of hooks, similar to React or Vue hooks.
     * We have currently an implementation of:
     * - useState (reactive state)
     * - onMounted
     * - onWillUnmount
     * - useRef
     */
    // -----------------------------------------------------------------------------
    // useState
    // -----------------------------------------------------------------------------
    /**
     * This is the main way a component can be made reactive.  The useState hook
     * will return an observed object (or array).  Changes to that value will then
     * trigger a rerendering of the current component.
     */
    function useState$1(state) {
        const component = Component.current;
        const __owl__ = component.__owl__;
        if (!__owl__.observer) {
            __owl__.observer = new Observer();
            __owl__.observer.notifyCB = component.render.bind(component);
        }
        return __owl__.observer.observe(state);
    }
    // -----------------------------------------------------------------------------
    // Life cycle hooks
    // -----------------------------------------------------------------------------
    function makeLifecycleHook(method, reverse = false) {
        if (reverse) {
            return function (cb) {
                const component = Component.current;
                if (component.__owl__[method]) {
                    const current = component.__owl__[method];
                    component.__owl__[method] = function () {
                        current.call(component);
                        cb.call(component);
                    };
                }
                else {
                    component.__owl__[method] = cb;
                }
            };
        }
        else {
            return function (cb) {
                const component = Component.current;
                if (component.__owl__[method]) {
                    const current = component.__owl__[method];
                    component.__owl__[method] = function () {
                        cb.call(component);
                        current.call(component);
                    };
                }
                else {
                    component.__owl__[method] = cb;
                }
            };
        }
    }
    function makeAsyncHook(method) {
        return function (cb) {
            const component = Component.current;
            if (component.__owl__[method]) {
                const current = component.__owl__[method];
                component.__owl__[method] = function (...args) {
                    return Promise.all([current.call(component, ...args), cb.call(component, ...args)]);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                };
            }
            else if (hasNoProp) {
                arePropsDifferent = (_1, _2) => false;
            }
            else {
                arePropsDifferent = function (props1, props2) {
                    for (let p of propList) {
                        if (props1[p] !== props2[p]) {
                            return true;
                        }
                    }
                    return false;
                };
            }
            const updateAndRender = ComponentNode.prototype.updateAndRender;
            const initiateRender = ComponentNode.prototype.initiateRender;
            return (props, key, ctx, parent, C) => {
                let children = ctx.children;
                let node = children[key];
                if (isDynamic && node && node.component.constructor !== C) {
                    node = undefined;
                }
                const parentFiber = ctx.fiber;
                if (node) {
                    if (arePropsDifferent(node.props, props) || parentFiber.deep || node.forceNextRender) {
                        node.forceNextRender = false;
                        updateAndRender.call(node, props, parentFiber);
                    }
                }
                else {
                    // new component
                    if (isStatic) {
                        const components = parent.constructor.components;
                        if (!components) {
                            throw new OwlError(`Cannot find the definition of component "${name}", missing static components key in parent`);
                        }
                        C = components[name];
                        if (!C) {
                            throw new OwlError(`Cannot find the definition of component "${name}"`);
                        }
                        else if (!(C.prototype instanceof Component)) {
                            throw new OwlError(`"${name}" is not a Component. It must inherit from the Component class`);
                        }
                    }
                    node = new ComponentNode(C, props, this, ctx, key);
                    children[key] = node;
                    initiateRender.call(node, new Fiber(node, parentFiber));
                }
                parentFiber.childrenMap[key] = node;
                return node;
            };
        }
        handleError(...args) {
            return handleError(...args);
        }
    }
    App.validateTarget = validateTarget;
    App.apps = apps;
    App.version = version;
    async function mount(C, target, config = {}) {
        return new App(C, config).mount(target, config);
    }

    const mainEventHandler = (data, ev, currentTarget) => {
        const { data: _data, modifiers } = filterOutModifiersFromData(data);
        data = _data;
        let stopped = false;
        if (modifiers.length) {
            let selfMode = false;
            const isSelf = ev.target === currentTarget;
            for (const mod of modifiers) {
                switch (mod) {
                    case "self":
                        selfMode = true;
                        if (isSelf) {
                            continue;
                        }
                        else {
                            return stopped;
                        }
                    case "prevent":
                        if ((selfMode && isSelf) || !selfMode)
                            ev.preventDefault();
                        continue;
                    case "stop":
                        if ((selfMode && isSelf) || !selfMode)
                            ev.stopPropagation();
                        stopped = true;
                        continue;
                }
            }
        }
        // If handler is empty, the array slot 0 will also be empty, and data will not have the property 0
        // We check this rather than data[0] being truthy (or typeof function) so that it crashes
        // as expected when there is a handler expression that evaluates to a falsy value
        if (Object.hasOwnProperty.call(data, 0)) {
            const handler = data[0];
            if (typeof handler !== "function") {
                throw new OwlError(`Invalid handler (expected a function, received: '${handler}')`);
            }
            let node = data[1] ? data[1].__owl__ : null;
            if (node ? node.status === 1 /* MOUNTED */ : true) {
                handler.call(node ? node.component : null, ev);
            }
        }
        return stopped;
    };

    function status(component) {
        switch (component.__owl__.status) {
            case 0 /* NEW */:
                return "new";
            case 2 /* CANCELLED */:
                return "cancelled";
            case 1 /* MOUNTED */:
                return "mounted";
            case 3 /* DESTROYED */:
                return "destroyed";
        }
    }

    // -----------------------------------------------------------------------------
    // useRef
    // -----------------------------------------------------------------------------
    /**
     * The purpose of this hook is to allow components to get a reference to a sub
     * html node or component.
     */
    function useRef(name) {
        const node = getCurrent();
        const refs = node.refs;
        return {
            get el() {
<<<<<<< HEAD
                const el = refs[name];
                return inOwnerDocument(el) ? el : null;
=======
                var _a, _b;
                const val = __owl__.refs && __owl__.refs[name];
                if (val instanceof Component) {
                    return val.el;
                }
                if (val instanceof HTMLElement) {
                    return val;
                }
                // Extra check in case the app was created outside an iframe but mounted into one
                // on Firefox 109+, the prototype of the element changes to use the iframe window's HTMLElement
                // see https://bugzilla.mozilla.org/show_bug.cgi?id=1813499
                const ownerWindow = (_b = (_a = val) === null || _a === void 0 ? void 0 : _a.ownerDocument) === null || _b === void 0 ? void 0 : _b.defaultView;
                if (ownerWindow && val instanceof ownerWindow.HTMLElement) {
                    return val;
                }
                return null;
            },
            get comp() {
                const val = __owl__.refs && __owl__.refs[name];
                return val instanceof Component ? val : null;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            },
        };
    }
    // -----------------------------------------------------------------------------
<<<<<<< HEAD
    // useEnv and useSubEnv
=======
    // "Builder" hooks
    // -----------------------------------------------------------------------------
    /**
     * This hook is useful as a building block for some customized hooks, that may
     * need a reference to the component calling them.
     */
    function useComponent() {
        return Component.current;
    }
    /**
     * This hook is useful as a building block for some customized hooks, that may
     * need a reference to the env of the component calling them.
     */
    function useEnv() {
        return Component.current.env;
    }
    // -----------------------------------------------------------------------------
    // useSubEnv
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    // -----------------------------------------------------------------------------
    /**
     * This hook is useful as a building block for some customized hooks, that may
     * need a reference to the env of the component calling them.
     */
    function useEnv() {
        return getCurrent().component.env;
    }
    function extendEnv(currentEnv, extension) {
        const env = Object.create(currentEnv);
        const descrs = Object.getOwnPropertyDescriptors(extension);
        return Object.freeze(Object.defineProperties(env, descrs));
    }
    /**
     * This hook is a simple way to let components use a sub environment.  Note that
     * like for all hooks, it is important that this is only called in the
     * constructor method.
     */
    function useSubEnv(envExtension) {
        const node = getCurrent();
        node.component.env = extendEnv(node.component.env, envExtension);
        useChildSubEnv(envExtension);
    }
    function useChildSubEnv(envExtension) {
        const node = getCurrent();
        node.childEnv = extendEnv(node.childEnv, envExtension);
    }
    /**
     * This hook will run a callback when a component is mounted and patched, and
     * will run a cleanup function before patching and before unmounting the
     * the component.
     *
     * @template T
     * @param {Effect<T>} effect the effect to run on component mount and/or patch
     * @param {()=>T} [computeDependencies=()=>[NaN]] a callback to compute
     *      dependencies that will decide if the effect needs to be cleaned up and
     *      run again. If the dependencies did not change, the effect will not run
     *      again. The default value returns an array containing only NaN because
     *      NaN !== NaN, which will cause the effect to rerun on every patch.
     */
    function useEffect(effect, computeDependencies = () => [NaN]) {
        let cleanup;
        let dependencies;
        onMounted(() => {
            dependencies = computeDependencies();
            cleanup = effect(...dependencies);
        });
        onPatched(() => {
            const newDeps = computeDependencies();
            const shouldReapply = newDeps.some((val, i) => val !== dependencies[i]);
            if (shouldReapply) {
                dependencies = newDeps;
                if (cleanup) {
                    cleanup();
                }
                cleanup = effect(...dependencies);
            }
        });
        onWillUnmount(() => cleanup && cleanup());
    }
    // -----------------------------------------------------------------------------
    // useExternalListener
    // -----------------------------------------------------------------------------
    /**
     * When a component needs to listen to DOM Events on element(s) that are not
     * part of his hierarchy, we can use the `useExternalListener` hook.
     * It will correctly add and remove the event listener, whenever the
     * component is mounted and unmounted.
     *
     * Example:
     *  a menu needs to listen to the click on window to be closed automatically
     *
     * Usage:
     *  in the constructor of the OWL component that needs to be notified,
     *  `useExternalListener(window, 'click', this._doSomething);`
     * */
    function useExternalListener(target, eventName, handler, eventParams) {
        const node = getCurrent();
        const boundHandler = handler.bind(node.component);
        onMounted(() => target.addEventListener(eventName, boundHandler, eventParams));
        onWillUnmount(() => target.removeEventListener(eventName, boundHandler, eventParams));
    }

<<<<<<< HEAD
    config.shouldNormalizeDom = false;
    config.mainEventHandler = mainEventHandler;
    const blockDom = {
        config,
        // bdom entry points
        mount: mount$1,
        patch,
        remove,
        // bdom block types
        list,
        multi,
        text,
        toggler,
        createBlock,
        html,
        comment,
    };
    const __info__ = {
        version: App.version,
    };

    TemplateSet.prototype._compileTemplate = function _compileTemplate(name, template) {
        return compile(template, {
            name,
            dev: this.dev,
            translateFn: this.translateFn,
            translatableAttributes: this.translatableAttributes,
        });
    };
=======
    var _hooks = /*#__PURE__*/Object.freeze({
        __proto__: null,
        useState: useState$1,
        onMounted: onMounted,
        onWillUnmount: onWillUnmount,
        onWillPatch: onWillPatch,
        onPatched: onPatched,
        onWillStart: onWillStart,
        onWillUpdateProps: onWillUpdateProps,
        useRef: useRef,
        useComponent: useComponent,
        useEnv: useEnv,
        useSubEnv: useSubEnv,
        useExternalListener: useExternalListener
    });

    class Store$1 extends Context$1 {
        constructor(config) {
            super(config.state);
            this.actions = config.actions;
            this.env = config.env;
            this.getters = {};
            this.updateFunctions = [];
            if (config.getters) {
                const firstArg = {
                    state: this.state,
                    getters: this.getters,
                };
                for (let g in config.getters) {
                    this.getters[g] = config.getters[g].bind(this, firstArg);
                }
            }
        }
        dispatch(action, ...payload) {
            if (!this.actions[action]) {
                throw new Error(`[Error] action ${action} is undefined`);
            }
            const result = this.actions[action]({
                dispatch: this.dispatch.bind(this),
                env: this.env,
                state: this.state,
                getters: this.getters,
            }, ...payload);
            return result;
        }
        __notifyComponents() {
            this.trigger("before-update");
            return super.__notifyComponents();
        }
    }
    const isStrictEqual = (a, b) => a === b;
    function useStore(selector, options = {}) {
        const component = Component.current;
        const componentId = component.__owl__.id;
        const store = options.store || component.env.store;
        if (!(store instanceof Store$1)) {
            throw new Error(`No store found when connecting '${component.constructor.name}'`);
        }
        let result = selector(store.state, component.props);
        const hashFn = store.observer.revNumber.bind(store.observer);
        let revNumber = hashFn(result);
        const isEqual = options.isEqual || isStrictEqual;
        if (!store.updateFunctions[componentId]) {
            store.updateFunctions[componentId] = [];
        }
        function selectCompareUpdate(state, props) {
            const oldResult = result;
            result = selector(state, props);
            const newRevNumber = hashFn(result);
            if ((newRevNumber > 0 && revNumber !== newRevNumber) || !isEqual(oldResult, result)) {
                revNumber = newRevNumber;
                return true;
            }
            return false;
        }
        if (options.onUpdate) {
            store.on("before-update", component, () => {
                const newValue = selector(store.state, component.props);
                options.onUpdate(newValue);
            });
        }
        store.updateFunctions[componentId].push(function () {
            return selectCompareUpdate(store.state, component.props);
        });
        useContextWithCB(store, component, function () {
            let shouldRender = false;
            for (let fn of store.updateFunctions[componentId]) {
                shouldRender = fn() || shouldRender;
            }
            if (shouldRender) {
                return component.render();
            }
        });
        onWillUpdateProps((props) => {
            selectCompareUpdate(store.state, props);
        });
        const __destroy = component.__destroy;
        component.__destroy = (parent) => {
            delete store.updateFunctions[componentId];
            if (options.onUpdate) {
                store.off("before-update", component);
            }
            __destroy.call(component, parent);
        };
        if (typeof result !== "object" || result === null) {
            return result;
        }
        return new Proxy(result, {
            get(target, k) {
                return result[k];
            },
            set(target, k, v) {
                throw new Error("Store state should only be modified through actions");
            },
            has(target, k) {
                return k in result;
            },
        });
    }
    function useDispatch(store) {
        store = store || Component.current.env.store;
        return store.dispatch.bind(store);
    }
    function useGetters(store) {
        store = store || Component.current.env.store;
        return store.getters;
    }

    /**
     * Owl Tags
     *
     * We have here a (very) small collection of tag functions:
     *
     * - xml
     *
     * The plan is to add a few other tags such as css, globalcss.
     */
    /**
     * XML tag helper for defining templates.  With this, one can simply define
     * an inline template with just the template xml:
     * ```js
     *   class A extends Component {
     *     static template = xml`<div>some template</div>`;
     *   }
     * ```
     */
    function xml(strings, ...args) {
        const name = `__template__${QWeb.nextId++}`;
        const value = String.raw(strings, ...args);
        QWeb.registerTemplate(name, value);
        return name;
    }
    /**
     * CSS tag helper for defining inline stylesheets.  With this, one can simply define
     * an inline stylesheet with just the following code:
     * ```js
     *   class A extends Component {
     *     static style = css`.component-a { color: red; }`;
     *   }
     * ```
     */
    function css(strings, ...args) {
        const name = `__sheet__${QWeb.nextId++}`;
        const value = String.raw(strings, ...args);
        registerSheet(name, value);
        return name;
    }

    var _tags = /*#__PURE__*/Object.freeze({
        __proto__: null,
        xml: xml,
        css: css
    });

    /**
     * AsyncRoot
     *
     * Owl is by default asynchronous, and the user interface will wait for all its
     * subcomponents to be rendered before updating the DOM. This is most of the
     * time what we want, but in some cases, it makes sense to "detach" a component
     * from this coordination.  This is the goal of the AsyncRoot component.
     */
    class AsyncRoot extends Component {
        async __updateProps(nextProps, parentFiber) {
            this.render(parentFiber.force);
        }
    }
    AsyncRoot.template = xml `<t t-slot="default"/>`;

    class Portal extends Component {
        constructor(parent, props) {
            super(parent, props);
            // boolean to indicate whether or not we must listen to 'dom-appended' event
            // to hook on the moment when the target is inserted into the DOM (because it
            // is not when the portal is rendered)
            this.doTargetLookUp = true;
            // set of encountered events that need to be redirected
            this._handledEvents = new Set();
            // function that will be the event's tunnel (needs to be an arrow function to
            // avoid having to rebind `this`)
            this._handlerTunnel = (ev) => {
                ev.stopPropagation();
                this.__trigger(ev.originalComponent, ev.type, ev.detail);
            };
            // Storing the parent's env
            this.parentEnv = null;
            // represents the element that is moved somewhere else
            this.portal = null;
            // the target where we will move `portal`
            this.target = null;
            this.parentEnv = parent ? parent.env : {};
            // put a callback in the env that is propagated to children s.t. portal can
            // register an handler to those events just before children will trigger them
            useSubEnv({
                [portalSymbol]: (ev) => {
                    if (!this._handledEvents.has(ev.type)) {
                        this.portal.elm.addEventListener(ev.type, this._handlerTunnel);
                        this._handledEvents.add(ev.type);
                    }
                },
            });
        }
        /**
         * Override to revert back to a classic Component's structure
         *
         * @override
         */
        __callWillUnmount() {
            super.__callWillUnmount();
            this.el.appendChild(this.portal.elm);
            this.doTargetLookUp = true;
        }
        /**
         * At each DOM change, we must ensure that the portal contains exactly one
         * child
         */
        __checkVNodeStructure(vnode) {
            const children = vnode.children;
            let countRealNodes = 0;
            for (let child of children) {
                if (child.sel) {
                    countRealNodes++;
                }
            }
            if (countRealNodes !== 1) {
                throw new Error(`Portal must have exactly one non-text child (has ${countRealNodes})`);
            }
        }
        /**
         * Ensure the target is still there at whichever time we render
         */
        __checkTargetPresence() {
            if (!this.target || !document.contains(this.target)) {
                throw new Error(`Could not find any match for "${this.props.target}"`);
            }
        }
        /**
         * Move the portal's element to the target
         */
        __deployPortal() {
            this.__checkTargetPresence();
            this.target.appendChild(this.portal.elm);
        }
        /**
         * Override to remove from the DOM the element we have teleported
         *
         * @override
         */
        __destroy(parent) {
            if (this.portal && this.portal.elm) {
                const displacedElm = this.portal.elm;
                const parent = displacedElm.parentNode;
                if (parent) {
                    parent.removeChild(displacedElm);
                }
            }
            super.__destroy(parent);
        }
        /**
         * Override to patch the element that has been teleported
         *
         * @override
         */
        __patch(target, vnode) {
            if (this.doTargetLookUp) {
                const target = document.querySelector(this.props.target);
                if (!target) {
                    this.env.qweb.on("dom-appended", this, () => {
                        this.doTargetLookUp = false;
                        this.env.qweb.off("dom-appended", this);
                        this.target = document.querySelector(this.props.target);
                        this.__deployPortal();
                    });
                }
                else {
                    this.doTargetLookUp = false;
                    this.target = target;
                }
            }
            this.__checkVNodeStructure(vnode);
            const shouldDeploy = (!this.portal || this.el.contains(this.portal.elm)) && !this.doTargetLookUp;
            if (!this.doTargetLookUp && !shouldDeploy) {
                // Only on pure patching, provided the
                // this.target's parent has not been unmounted
                this.__checkTargetPresence();
            }
            const portalPatch = this.portal ? this.portal : document.createElement(vnode.children[0].sel);
            this.portal = patch(portalPatch, vnode.children[0]);
            vnode.children = [];
            super.__patch(target, vnode);
            if (shouldDeploy) {
                this.__deployPortal();
            }
        }
        /**
         * Override to set the env
         */
        __trigger(component, eventType, payload) {
            const env = this.env;
            this.env = this.parentEnv;
            super.__trigger(component, eventType, payload);
            this.env = env;
        }
    }
    Portal.template = xml `<portal><t t-slot="default"/></portal>`;
    Portal.props = {
        target: {
            type: String,
        },
    };

    class Link extends Component {
        constructor() {
            super(...arguments);
            this.href = this.env.router.destToPath(this.props);
        }
        async willUpdateProps(nextProps) {
            this.href = this.env.router.destToPath(nextProps);
        }
        get isActive() {
            if (this.env.router.mode === "hash") {
                return document.location.hash === this.href;
            }
            return document.location.pathname === this.href;
        }
        navigate(ev) {
            // don't redirect with control keys
            if (ev.metaKey || ev.altKey || ev.ctrlKey || ev.shiftKey) {
                return;
            }
            // don't redirect on right click
            if (ev.button !== undefined && ev.button !== 0) {
                return;
            }
            // don't redirect if `target="_blank"`
            if (ev.currentTarget && ev.currentTarget.getAttribute) {
                const target = ev.currentTarget.getAttribute("target");
                if (/\b_blank\b/i.test(target)) {
                    return;
                }
            }
            ev.preventDefault();
            this.env.router.navigate(this.props);
        }
    }
    Link.template = xml `
    <a  t-att-class="{'router-link-active': isActive }"
        t-att-href="href"
        t-on-click="navigate">
        <t t-slot="default"/>
    </a>
  `;

    class RouteComponent extends Component {
        get routeComponent() {
            return this.env.router.currentRoute && this.env.router.currentRoute.component;
        }
    }
    RouteComponent.template = xml `
    <t>
        <t
            t-if="routeComponent"
            t-component="routeComponent"
            t-key="env.router.currentRouteName"
            t-props="env.router.currentParams" />
    </t>
  `;

    const paramRegexp = /\{\{(.*?)\}\}/;
    const globalParamRegexp = new RegExp(paramRegexp.source, "g");
    class Router {
        constructor(env, routes, options = { mode: "history" }) {
            this.currentRoute = null;
            this.currentParams = null;
            env.router = this;
            this.mode = options.mode;
            this.env = env;
            this.routes = {};
            this.routeIds = [];
            let nextId = 1;
            for (let partialRoute of routes) {
                if (!partialRoute.name) {
                    partialRoute.name = "__route__" + nextId++;
                }
                if (partialRoute.component) {
                    QWeb.registerComponent("__component__" + partialRoute.name, partialRoute.component);
                }
                if (partialRoute.redirect) {
                    this.validateDestination(partialRoute.redirect);
                }
                partialRoute.params = partialRoute.path ? findParams(partialRoute.path) : [];
                partialRoute.extractionRegExp = makeExtractionRegExp(partialRoute.path);
                this.routes[partialRoute.name] = partialRoute;
                this.routeIds.push(partialRoute.name);
            }
        }
        //--------------------------------------------------------------------------
        // Public API
        //--------------------------------------------------------------------------
        async start() {
            this._listener = (ev) => this._navigate(this.currentPath(), ev);
            window.addEventListener("popstate", this._listener);
            if (this.mode === "hash") {
                window.addEventListener("hashchange", this._listener);
            }
            const result = await this.matchAndApplyRules(this.currentPath());
            if (result.type === "match") {
                this.currentRoute = result.route;
                this.currentParams = result.params;
                const currentPath = this.routeToPath(result.route, result.params);
                if (currentPath !== this.currentPath()) {
                    this.setUrlFromPath(currentPath);
                }
            }
        }
        async navigate(to) {
            const path = this.destToPath(to);
            return this._navigate(path);
        }
        async _navigate(path, ev) {
            const initialName = this.currentRouteName;
            const initialParams = this.currentParams;
            const result = await this.matchAndApplyRules(path);
            if (result.type === "match") {
                let finalPath = this.routeToPath(result.route, result.params);
                if (path.indexOf("?") > -1) {
                    finalPath += "?" + path.split("?")[1];
                }
                const isPopStateEvent = ev && ev instanceof PopStateEvent;
                if (!isPopStateEvent) {
                    this.setUrlFromPath(finalPath);
                }
                this.currentRoute = result.route;
                this.currentParams = result.params;
            }
            else if (result.type === "nomatch") {
                this.currentRoute = null;
                this.currentParams = null;
            }
            const didChange = this.currentRouteName !== initialName || !shallowEqual(this.currentParams, initialParams);
            if (didChange) {
                this.env.qweb.forceUpdate();
                return true;
            }
            return false;
        }
        destToPath(dest) {
            this.validateDestination(dest);
            return dest.path || this.routeToPath(this.routes[dest.to], dest.params);
        }
        get currentRouteName() {
            return this.currentRoute && this.currentRoute.name;
        }
        //--------------------------------------------------------------------------
        // Private helpers
        //--------------------------------------------------------------------------
        setUrlFromPath(path) {
            const separator = this.mode === "hash" ? location.pathname : "";
            const url = location.origin + separator + path;
            if (url !== window.location.href) {
                window.history.pushState({}, path, url);
            }
        }
        validateDestination(dest) {
            if ((!dest.path && !dest.to) || (dest.path && dest.to)) {
                throw new Error(`Invalid destination: ${JSON.stringify(dest)}`);
            }
        }
        routeToPath(route, params) {
            const prefix = this.mode === "hash" ? "#" : "";
            return (prefix +
                route.path.replace(globalParamRegexp, (match, param) => {
                    const [key] = param.split(".");
                    return params[key];
                }));
        }
        currentPath() {
            let result = this.mode === "history" ? window.location.pathname : window.location.hash.slice(1);
            return result || "/";
        }
        match(path) {
            for (let routeId of this.routeIds) {
                let route = this.routes[routeId];
                let params = this.getRouteParams(route, path);
                if (params) {
                    return {
                        type: "match",
                        route: route,
                        params: params,
                    };
                }
            }
            return { type: "nomatch" };
        }
        async matchAndApplyRules(path) {
            const result = this.match(path);
            if (result.type === "match") {
                return this.applyRules(result);
            }
            return result;
        }
        async applyRules(matchResult) {
            const route = matchResult.route;
            if (route.redirect) {
                const path = this.destToPath(route.redirect);
                return this.matchAndApplyRules(path);
            }
            if (route.beforeRouteEnter) {
                const result = await route.beforeRouteEnter({
                    env: this.env,
                    from: this.currentRoute,
                    to: route,
                });
                if (result === false) {
                    return { type: "cancelled" };
                }
                else if (result !== true) {
                    // we want to navigate to another destination
                    const path = this.destToPath(result);
                    return this.matchAndApplyRules(path);
                }
            }
            return matchResult;
        }
        getRouteParams(route, path) {
            if (route.path === "*") {
                return {};
            }
            if (path.indexOf("?") > -1) {
                path = path.split("?")[0];
            }
            if (path.startsWith("#")) {
                path = path.slice(1);
            }
            const paramsMatch = path.match(route.extractionRegExp);
            if (!paramsMatch) {
                return false;
            }
            const result = {};
            route.params.forEach((param, index) => {
                const [key, suffix] = param.split(".");
                const paramValue = paramsMatch[index + 1];
                if (suffix === "number") {
                    return (result[key] = parseInt(paramValue, 10));
                }
                return (result[key] = paramValue);
            });
            return result;
        }
    }
    function findParams(str) {
        const result = [];
        let m;
        do {
            m = globalParamRegexp.exec(str);
            if (m) {
                result.push(m[1]);
            }
        } while (m);
        return result;
    }
    function escapeRegExp(str) {
        return str.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
    }
    function makeExtractionRegExp(path) {
        // replace param strings with capture groups so that we can build a regex to match over the path
        const extractionString = path
            .split(paramRegexp)
            .map((part, index) => {
            return index % 2 ? "(.*)" : escapeRegExp(part);
        })
            .join("");
        // Example: /home/{{param1}}/{{param2}} => ^\/home\/(.*)\/(.*)$
        return new RegExp(`^${extractionString}$`);
    }

    /**
     * This file is the main file packaged by rollup (see rollup.config.js).  From
     * this file, we export all public owl elements.
     *
     * Note that dynamic values, such as a date or a commit hash are added by rollup
     */
    const Context = Context$1;
    const useState = useState$1;
    const core = { EventBus, Observer };
    const router = { Router, RouteComponent, Link };
    const Store = Store$1;
    const utils = _utils;
    const tags = _tags;
    const misc = { AsyncRoot, Portal };
    const hooks = Object.assign({}, _hooks, {
        useContext: useContext,
        useDispatch: useDispatch,
        useGetters: useGetters,
        useStore: useStore,
    });
    const __info__ = {};
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    exports.App = App;
    exports.Component = Component;
<<<<<<< HEAD
    exports.EventBus = EventBus;
    exports.OwlError = OwlError;
    exports.__info__ = __info__;
    exports.blockDom = blockDom;
    exports.loadFile = loadFile;
    exports.markRaw = markRaw;
    exports.markup = markup;
    exports.mount = mount;
    exports.onError = onError;
    exports.onMounted = onMounted;
    exports.onPatched = onPatched;
    exports.onRendered = onRendered;
    exports.onWillDestroy = onWillDestroy;
    exports.onWillPatch = onWillPatch;
    exports.onWillRender = onWillRender;
    exports.onWillStart = onWillStart;
    exports.onWillUnmount = onWillUnmount;
    exports.onWillUpdateProps = onWillUpdateProps;
    exports.reactive = reactive;
    exports.status = status;
    exports.toRaw = toRaw;
    exports.useChildSubEnv = useChildSubEnv;
    exports.useComponent = useComponent;
    exports.useEffect = useEffect;
    exports.useEnv = useEnv;
    exports.useExternalListener = useExternalListener;
    exports.useRef = useRef;
    exports.useState = useState;
    exports.useSubEnv = useSubEnv;
    exports.validate = validate;
    exports.validateType = validateType;
    exports.whenReady = whenReady;
    exports.xml = xml;

    Object.defineProperty(exports, '__esModule', { value: true });
=======
    exports.Context = Context;
    exports.QWeb = QWeb;
    exports.Store = Store;
    exports.__info__ = __info__;
    exports.browser = browser;
    exports.config = config;
    exports.core = core;
    exports.hooks = hooks;
    exports.misc = misc;
    exports.mount = mount;
    exports.router = router;
    exports.tags = tags;
    exports.useState = useState;
    exports.utils = utils;

    Object.defineProperty(exports, '__esModule', { value: true });


    __info__.version = '1.4.11';
    __info__.date = '2023-01-30T13:09:39.141Z';
    __info__.hash = 'a38c534';
    __info__.url = 'https://github.com/odoo/owl';

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


    __info__.date = '2023-09-25T11:50:11.419Z';
    __info__.hash = '5dcee25';
    __info__.url = 'https://github.com/odoo/owl';


})(this.owl = this.owl || {});
