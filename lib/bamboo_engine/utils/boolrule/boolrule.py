# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from pyparsing import (
    CaselessLiteral,
    Combine,
    Forward,
    Group,
    Keyword,
    Optional,
    ParseException,
    ParseResults,
    QuotedString,
    Suppress,
    Word,
    ZeroOrMore,
    alphanums,
    alphas,
    delimitedList,
    nums,
    oneOf,
)

PATH_DELIMITER = "."


class SubstituteVal(object):
    """
    Represents a token that will later be replaced by a context value.
    """

    def __init__(self, t):
        self._path = t[0]

    def get_val(self, context):
        if not context:
            # raise MissingVariableException(
            #     'context missing or empty'
            # )
            return self._path

        val = context

        try:
            for part in self._path.split(PATH_DELIMITER):
                val = getattr(val, part) if hasattr(val, part) else val[part]

        except KeyError:
            raise MissingVariableException("no value supplied for {}".format(self._path))

        return val

    def __repr__(self):
        return "SubstituteVal(%s)" % self._path


def get_bool_expression():

    # Grammar definition
    # match gcloud's variable
    identifier = Combine(Optional("${") + Optional("_") + Word(alphas, alphanums + "_") + Optional("}"))
    # identifier = Word(alphas, alphanums + "_")
    propertyPath = delimitedList(identifier, PATH_DELIMITER, combine=True)

    and_ = Keyword("and", caseless=True)
    or_ = Keyword("or", caseless=True)

    lparen = Suppress("(")
    rparen = Suppress(")")

    binaryOp = oneOf("== != < > >= <= in notin issuperset notissuperset", caseless=True)("operator")

    E = CaselessLiteral("E")
    numberSign = Word("+-", exact=1)
    realNumber = Combine(
        Optional(numberSign)
        + (Word(nums) + "." + Optional(Word(nums)) | ("." + Word(nums)))
        + Optional(E + Optional(numberSign) + Word(nums))
    )

    integer = Combine(Optional(numberSign) + Word(nums) + Optional(E + Optional("+") + Word(nums)))

    # str_ = quotedString.addParseAction(removeQuotes)
    str_ = QuotedString('"') | QuotedString("'")
    bool_ = oneOf("true false", caseless=True)

    simpleVals = (
        realNumber.setParseAction(lambda toks: float(toks[0]))
        | integer.setParseAction(lambda toks: int(toks[0]))
        | str_
        | bool_.setParseAction(lambda toks: toks[0] == "true")
        | propertyPath.setParseAction(lambda toks: SubstituteVal(toks))
    )  # need to add support for alg expressions

    propertyVal = simpleVals | (lparen + Group(delimitedList(simpleVals)) + rparen)

    boolExpression = Forward()
    boolCondition = Group(
        (Group(propertyVal)("lval") + binaryOp + Group(propertyVal)("rval")) | (lparen + boolExpression + rparen)
    )
    boolExpression << boolCondition + ZeroOrMore((and_ | or_) + boolExpression)

    return boolExpression


def double_equals_trans(lval, rval, operator):
    # double equals
    if operator in ["in", "notin"]:
        if isinstance(rval, list) and len(rval):
            transed_rval = []
            if isinstance(lval, int):
                for item in rval:
                    try:
                        transed_rval.append(int(item))
                    except Exception:
                        pass
            elif isinstance(lval, str):
                for item in rval:
                    try:
                        transed_rval.append(str(item))
                    except Exception:
                        pass
            rval += transed_rval

    elif operator in ["issuperset", "notissuperset"]:
        # avoid convert set('abc') to {a, b, c}, but keep {'abc'}
        if isinstance(lval, str):
            lval = [lval]
        if isinstance(rval, str):
            rval = [rval]

    else:
        try:
            if isinstance(lval, int):
                rval = int(rval)
            elif isinstance(rval, int):
                lval = int(lval)
            if isinstance(lval, str):
                rval = str(rval)
            elif isinstance(rval, str):
                lval = str(lval)
        except Exception:
            pass

    return lval, rval


class BoolRule(object):
    """
    Represents a boolean expression and provides a `test` method to evaluate
    the expression and determine its truthiness.

    :param query: A string containing the query to be evaluated
    :param lazy: If ``True``, parse the query the first time it's tested rather
                 than immediately. This can help with performance if you
                 instantiate a lot of rules and only end up evaluating a
                 small handful.
    """

    _compiled = False
    _tokens = None
    _query = None

    def __init__(self, query, lazy=False, strict=True):
        self._query = query
        self.strict = strict
        if not lazy:
            self._compile()

    def test(self, context=None):
        """
        Test the expression against the given context and return the result.

        :param context: A dict context to evaluate the expression against.
        :return: True if the expression succesfully evaluated against the
                 context, or False otherwise.
        """
        if self._is_match_all():
            return True

        self._compile()
        return self._test_tokens(self._tokens, context)

    def _is_match_all(self):
        return True if self._query == "*" else False

    def _compile(self):
        if not self._compiled:

            # special case match-all query
            if self._is_match_all():
                return

            try:
                self._tokens = get_bool_expression().parseString(self._query, parseAll=self.strict)
            except ParseException:
                raise

            self._compiled = True

    def _expand_val(self, val, context):
        if type(val) == list:
            val = [self._expand_val(v, context) for v in val]

        if isinstance(val, SubstituteVal):
            ret = val.get_val(context)
            return ret

        if isinstance(val, ParseResults):
            return [self._expand_val(x, context) for x in val.asList()]

        return val

    def _test_tokens(self, tokens, context):
        passed = False

        for token in tokens:

            if not isinstance(token, ParseResults):
                if token == "or" and passed:
                    return True
                elif token == "and" and not passed:
                    return False
                continue

            if not token.getName():
                passed = self._test_tokens(token, context)
                continue

            items = token.asDict()

            operator = items["operator"]
            lval = self._expand_val(items["lval"][0], context)
            rval = self._expand_val(items["rval"][0], context)
            lval, rval = double_equals_trans(lval, rval, operator)

            if operator in ("=", "==", "eq"):
                passed = lval == rval
            elif operator in ("!=", "ne"):
                passed = lval != rval
            elif operator in (">", "gt"):
                passed = lval > rval
            elif operator in (">=", "ge"):
                passed = lval >= rval
            elif operator in ("<", "lt"):
                passed = lval < rval
            elif operator in ("<=", "le"):
                passed = lval <= rval
            elif operator == "in":
                passed = lval in rval
            elif operator == "notin":
                passed = lval not in rval
            elif operator == "issuperset":
                passed = set(lval).issuperset(set(rval))
            elif operator == "notissuperset":
                passed = not set(lval).issuperset(set(rval))
            else:
                raise UnknownOperatorException("Unknown operator '{}'".format(operator))

        return passed


class MissingVariableException(Exception):
    """
    Raised when an expression contains a property path that's not supplied in
    the context.
    """

    pass


class UnknownOperatorException(Exception):
    """
    Raised when an expression uses an unknown operator.

    This should never be thrown since the operator won't be correctly parsed as
    a token by pyparsing, but it's useful to have this hanging around for when
    additional operators are being added.
    """

    pass
