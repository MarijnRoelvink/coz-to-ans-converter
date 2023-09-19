import re
from main import code_parser as p
# from main import algorithm as a
#
#
# def test_answerlines():
#     alg = a.Algorithm([])
#     with open("../data/input/answer_lines.txt") as f:
#         lines = f.readlines()
#         lines = [line for line in lines if line != "\n"]
#         lines = [{"ans": re.sub(r"\$\d+ =", "", line).strip(),
#                   "id": re.match(r"(\$\d+) =", line).group(1)} for line in lines if re.match(r"(\$\d+) =", line)!= None]
#         for l in lines:
#             alg.addAnsLine(l["id"], l["ans"])
#
#     output = alg.formatAnswers()
#     # print("\n".join(output))

def test_simple_math():
    line = "(2*P1^2+5*P2+7*P3)/(P1+P2+P3)"
    expr = p.parseExpr(line, "$test")
    print(expr.toString())

def test_minus_sign():
    lines = ["-1*2", "2-1*2", "2*-1"]
    for line in lines:
        expr = p.parseExpr(line, "$test")
        print(expr.toString())

def test_function():
    lines = ["-P3/10*(SQR(P1)-SQR(P2))", "(2/(8+P1))*P2*SQRT(SQR(P1)+9)"]
    for line in lines:
        expr = p.parseExpr(line, "$test")
        print(expr.toString())

def test_assignment():
    lines = ["c := (a := b) * a"]
    for line in lines:
        expr = p.parseExpr(line, "$test")
        print(p.toString(expr))
        
def test_multiple_expressions():
    lines = [
        "c := b * a; c + 3",
             "A:=P1+P2;\r\nABS((A*P1^2*P3+2.*A*P1*P2*P3+A*P2^2*P3+A*P2^2*P4+P1*P2^2*P4)/(A^2+2.*A*P1+2.*A*P2+P1^2+2.*P1*P2+P2^2))"]
    for line in lines:
        expr = p.parseExpr(line, "$test")
        print(p.toString(expr))

if __name__ == "__main__":
    # test_answerlines()
    # test_simple_math()
    # test_minus_sign()
    # test_function()
    # test_assignment()
    test_multiple_expressions()