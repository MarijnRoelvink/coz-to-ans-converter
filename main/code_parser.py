import re


class Expr:
    def __init__(self, line, vars):
        self.id = vars["id"]
        d_print(line, vars["debug"])
        d_print(vars, vars["debug"])
        # Check if it was a replaced expression
        match = re.fullmatch(r"(-{0,1})(\[EXPR\d+\])", line)
        if (match != None):
            self.expr = self.parseExpr(match, vars)
        else:
            self.text = line
            self.expr = self.parseLine(line, vars)

    def getType(self):
        return self.expr.__class__.__name__

    # Returns a string version of the equation.
    # Subs: sub equations that will need to be printed above the final line
    # Returns: (line, subs); the final converted line + the sub equations
    def toString(self, subs):
        return self.expr.toString(subs)

    def parseLine(self, line, vars):

        sub_exprs = line.split(";")
        brackets = findClosingBrackets(line)
        args = line.split(",")
        assign_reg = r"(.+?)(:=)(.+)"
        func_reg = r"(\w+)(\[EXPR\d+?\])"
        plus_reg = r"(.+?)([+])(.+)"
        min_reg = r"(.*?[^^*/])([-])(.+)"  # Parse only minuses that aren't part of a multiplication
        times_div_reg = r"(.+?)([*/])(.+)"
        eqs_reg = r"(.+?)([=><]+)(.+)"
        pow_reg = r"(.+?)(\^)(.+)"

        # Parse expression separators
        if(len(sub_exprs) > 1):
            return MultExpr(sub_exprs, vars)

        # Parse brackets
        elif (len(brackets) > 0):
            return self.parseBrackets(line, brackets, vars)

        # Parse arguments
        elif (len(args) > 1):
            return MultiArg(args, vars)

        # Parse assignments
        elif (re.search(assign_reg, line) != None):
            return self.parseBinOp(assign_reg, line, vars)

        # Parse functions
        elif (re.search(func_reg, line) != None):
            return self.parseFunc(func_reg, line, vars)

        # Parse + expressions
        elif (re.search(plus_reg, line) != None):
            return self.parseBinOp(plus_reg, line, vars)

        # Parse - expressions
        elif (re.search(min_reg, line) != None):
            return self.parseBinOp(min_reg, line, vars)

        # Parse >=, <=, <, > and = expressions
        elif (re.search(eqs_reg, line) != None):
            return self.parseBinOp(eqs_reg, line, vars)

        # Parse * and / expressions
        elif (re.search(times_div_reg, line) != None):
            return self.parseBinOp(times_div_reg, line, vars)

        # Parse ^ expressions
        elif (re.search(pow_reg, line) != None):
            return self.parseBinOp(pow_reg, line, vars)

        # Parse numbers
        elif (re.fullmatch(r"-{0,1}\d+\.{0,1}\d*", line)):
            return Number(line, vars)

        # Parse variables
        else:
            return Var(line, vars)

    def parseExpr(self, match, vars):
        minus_sign = match.group(1)
        expr_line = match.group(2)
        v_line, subs = vars[expr_line].toString([])
        d_print(f"Replace {expr_line} with {v_line}", vars["debug"])
        if (minus_sign == "-"):
            return Minus(vars[expr_line])
        else:
            return vars[expr_line]

    def parseBinOp(self, regex, line, vars):
        match = re.search(regex, line)
        expr = BinOp(match.group(1),
                     match.group(3),
                     match.group(2), vars)
        return expr

    def parseFunc(self, regex, line, vars):
        match = re.search(regex, line)
        # Store key and expression in vars
        newExpr = f"[EXPR{vars['count']}]"
        vars[newExpr] = Func(match.group(2), match.group(1), vars)
        vars["count"] = vars["count"] + 1

        # Replace brackets with EXPR, to be swapped later
        line = line[:match.start()] + newExpr + line[match.end():]
        d_print(line, vars["debug"])
        return Expr(line, vars)

    def parseBrackets(self, line, brackets, vars):
        key = list(brackets.keys())[0]

        # Store key and expression in vars
        newExpr = f"[EXPR{vars['count']}]"
        vars[newExpr] = Bracket(line[key + 1:brackets[key]], vars)
        vars["count"] = vars["count"] + 1

        # Replace brackets with EXPR, to be swapped later
        line = line[:key] + newExpr + line[brackets[key] + 1:]
        d_print(line, vars["debug"])
        return Expr(line, vars)


class Number:
    def __init__(self, num, vars):
        d_print(f"Number: {num}", vars["debug"])
        self.number = num

    def toString(self, subs):
        return (self.number, subs)


class Var:
    def __init__(self, var, vars):
        d_print(f"Variable: {var}", vars["debug"])
        self.var = var
        self.alg_vars = vars["alg_vars"]

    def toString(self, subs):
        # Capture sign of variable
        sign = re.match(r"(-{0,1}).+", self.var).group(1)
        res = re.sub("-", "", self.var)

        if (res == "PI"):
            res = sign + "Pi"
        elif (self.alg_vars != None and not (res in self.alg_vars)):
            res = f"FLAG[unknown var: {res}]"
        else:
            res = sign + "$" + res

        return (res, subs)

class MultExpr:
    def __init__(self, sub_exprs, vars):
        d_print(f"Multiple expressions separated by ;", vars["debug"])
        self.exprs = [Expr(expr.strip(), vars) for expr in sub_exprs]
        self.id = vars["id"]

    def toString(self, subs):
        # Parse all the sub expressions except the last line and add them to subs
        num_expr = len(self.exprs)
        if(num_expr > 1):
            for i in range(num_expr - 1):
                expr = self.exprs[i]
                line, subs = expr.toString(subs)

                #Check if the line isn't a simple variable assignment, in this case, we don't need to output the left side
                if (not(expr.getType() == "BinOp" and expr.expr.type == ":=")):
                    subs.append(line)
        # Parse the last line (which is the answer) and return the string
        return self.exprs[-1].toString(subs)

class BinOp:
    def __init__(self, expr1, expr2, type, vars):
        d_print(f"Binary operation: {type}", vars["debug"])
        self.expr1 = Expr(expr1, vars)
        self.expr2 = Expr(expr2, vars)
        self.type = type
        self.id = vars["id"]

    def toString(self, subs):
        res = ""
        # >= = ge
        # <= = le
        # > = gt
        # < = lt
        # = = eq

        functions = {">": "gt",
                     "<": "lt",
                     "=": "eq"}

        double_functions = {">=": "gt", "<=": "lt"}

        assignment = ":="

        str1, subs = self.expr1.toString(subs)
        str2, subs = self.expr2.toString(subs)

        # Substitute "... than or equal" questions into two separate checks
        # for "... than" and "equal" and add the results in the final answer
        if (self.type in double_functions):
            formula = double_functions[self.type]
            res_comp = f"{self.id}_{len(subs)}"
            subs.append(f"{res_comp} = {formula}({str1}, {str2})")
            res_eq = f"{self.id}_{len(subs)}"
            subs.append(f"{res_eq} = eq({str1}, {str2})")
            res = f"{res_comp}+{res_eq}"
        elif (self.type == assignment):
            res = str1
            subs.append(f"{str1} = {str2}")
        elif (self.type in functions):
            res = f"{self.id}_{len(subs)}"
            subs.append(f"{res} = {functions[self.type]}({str1}, {str2})")
        else:
            res = str1 + self.type + str2
        return (res, subs)


class Bracket:
    def __init__(self, line, vars):
        d_print(f"Bracket: {line}", vars["debug"])
        self.expr = Expr(line, vars)

    def toString(self, subs):
        str_expr, subs = self.expr.toString(subs)

        return ("(" + str_expr + ")", subs)


class Minus:
    def __init__(self, expr):
        self.expr = expr

    def toString(self, subs):
        str_expr, subs = self.expr.toString(subs)

        return ("-" + str_expr, subs)


class MultiArg:
    def __init__(self, args, vars):
        d_print(f"Multiple arguments separated by ,", vars["debug"])
        self.exprs = [Expr(expr.strip(), vars) for expr in args]
        self.id = vars["id"]

    def toString(self, subs):
        args = []
        for expr in self.exprs:
            arg, subs = expr.toString(subs)
            args.append(arg)

        return (",".join(args), subs)

class Func:
    simple_functions = ["ABS",
                        "ARCCOS",
                        "ARCSIN",
                        "ARCTAN",
                        "COS",
                        "COT",
                        "EXP",
                        "FACT",
                        "INT",
                        "LN",
                        "LOG",
                        "MAX",
                        "MIN",
                        "SIN",
                        "SQRT",
                        "TAN"]

    mappable_functions = {
        "ARCSINH": "archypsin",
        "COSH": "hypcos",
        "SINH": "hypsin",
        "TANH": "hyptan",
        "ARCCOSD": "180/Pi*arccos",
        "ARCSIND": "180/Pi*arcsin",
        "ARCTAND": "180/Pi*arctan",
    }

    # These functions process the angles as degrees instead of radians
    degree_in_functions = {
        "COSD": "cos",
        "SIND": "sin",
        "TAND": "tan"
    }

    less_simple_functions = ["ARCCOSH",
                             "ARCCOT",
                             "ARCTANH",
                             "AVG",
                             "CL",
                             "CNT",
                             "DEG",
                             "FL",
                             "FOR",
                             "FR",
                             "NEG",
                             "POS",
                             "RAD",
                             "RANDOM",
                             "RCA",
                             "RCL",
                             "RCM",
                             "RND",
                             "SELECT",
                             "SIGN",
                             "STA",
                             "STM",
                             "STO",
                             "WHILE",
                             "IF"]

    def __init__(self, line, fun, vars):
        d_print(f"Function: {line}", vars["debug"])
        self.fun = fun
        self.expr = Expr(line, vars)

    def toString(self, subs):
        str_expr, subs = self.expr.toString(subs)
        res = ""

        if (self.fun in Func.simple_functions):
            res = self.fun.lower() + str_expr
        elif (self.fun in Func.mappable_functions):
            res = Func.mappable_functions[self.fun] + str_expr
        elif (self.fun in Func.degree_in_functions):
            res = Func.degree_in_functions[self.fun] + "(" + str_expr + "*Pi/180)"
        elif (self.fun == "SQR"):
            res = str_expr + "^2"
        elif (self.fun in Func.less_simple_functions):
            res = f"FLAG[unsupported function (by us, ANS or both): {self.fun}]" + str_expr
        else:
            res = f"FLAG[unknown function: {self.fun}]"

        return (res, subs)


# Returns the starting and endplace of each corresponding bracket pair
# Taken from: https://stackoverflow.com/questions/29991917/indices-of-matching-parentheses-in-python
def findClosingBrackets(line):
    istart = []  # stack of indices of opening parentheses
    d = {}

    for i, c in enumerate(line):
        if c == '(':
            istart.append(i)
        if c == ')':
            try:
                d[istart.pop()] = i
            except IndexError:
                print('Too many closing parentheses')
    if istart:  # check if stack is empty afterwards
        print('Too many opening parentheses')
    return d


def hasValidBrackets(line):
    istart = []  # stack of indices of opening parentheses
    d = {}

    for i, c in enumerate(line):
        if c == '(':
            istart.append(i)
        if c == ')':
            if len(istart) > 0:
                d[istart.pop()] = i
            else:
                return False
    if istart:  # check if stack is empty afterwards
        return False
    return True


def parseExpr(line, id, alg_vars=None):
    line = re.sub(" ", "", line)
    vars = {"count": 0, "debug": False, "id": id, "alg_vars": alg_vars}
    d_print(line, vars["debug"])
    return Expr(line, vars)


def toString(expr):
    line, subs = expr.toString([])
    line = f"{expr.id} = {line}"
    return "\n".join(subs + [line])


def d_print(text, on=False):
    if (on):
        print(text)
