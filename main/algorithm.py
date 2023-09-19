import re
import cleaner as c
import code_parser as p

# Formats the text for the algorithm tag. In this code goes the
# Initialization of params Pi with random vars
# Initialization of text params (a = P1)
# Initialization of the answers for different subquestions


class Algorithm:

    # Input: Ranges - array of ranges for each param Pi
    #   Example: ['8..20/2,', '2..8/2,', '2..20/2,']
    def __init__(self, ranges, params):
        self.p_vars = [f"P{i+1}" for i in range(len(ranges))]
        self.ranges = self.parseRanges(ranges)
        self.ans_lines = {}
        self.params = params

    # Adds an answer formula from a subquestion to the algorithm,
    #   Example: subID - $2512045, line - (P1<=P2)*4*P3*P2/(4+P2)+(P1>P2)*4*P3*P1/(4+P2)
    def addAnsLine(self, subID, line):
        self.ans_lines[subID] = line

    def parseRanges(self, ranges):
        res = []
        for range in ranges:
            sub_res = []
            subranges = range.split(",")
            for r in subranges:
                r = r.strip()
                # Check if the range matches the pattern of: start..stop/step (1..8/2)
                match_full = re.match(r"([\d.]+)\.\.([\d.]+)/([\d.]+)", r)
                # Check if the range matches the pattern of: start..stop
                match_stop = re.match(r"([\d.]+)\.\.([\d.]+)", r)
                # Check if the range matches the pattern of: start
                match_start = re.match(r"([\d.]+)", r)

                start,stop,step = ("0","0","0")

                if match_full != None:
                    start = match_full.group(1)
                    stop = match_full.group(2)
                    step = match_full.group(3)
                elif match_stop != None:
                    start = match_stop.group(1)
                    stop = match_stop.group(2)
                    step = 1
                elif match_start != None:
                    start = match_start.group(1)
                    stop = match_start.group(1)
                    step = 1

                if(r != ""):
                    sub_res.append({
                        "start": start,
                        "stop": stop,
                        "step": step,
                        "old": r
                    })
            res.append(sub_res)
        return res

    def formatParamText(self):
        items = "\n"
        for i, line in enumerate(self.params):
            line = re.sub(r"(P\d{1,2})", r"$\1", line)
            items = items + f"\t<li>{line}</li>\n"
        res_str = f"\n<h4>Parameters:</h4>\n<ul>{items}</ul>"
        return res_str

    def formatAnswers(self):
        # Loop through all subquestion-answer combi's
        # s = subId ($ans_3636280)
        # a = answer_line (-P2*P1*P1/(P3+2))
        res = []
        for s, a in self.ans_lines.items():
            if(a != ""):
                res.append(self.replaceANSCode(a, s))
        return res

    def formatRanges(self):
        res = []
        for i, r in enumerate(self.ranges):
            p_var = f"${self.p_vars[i]}"

            # Case: range consists just of one simple range
            if(len(r) == 1):
                r = r[0]
                res.append(f"{p_var}={self.formatSubrange(r)}")
            # Case: range is empty
            elif (len(r) == 0):
                pass
            # Case: range consists of sequence: 1,2,3
            elif(self.range_is_sequence(r)):
                sub_lines = []
                sub_lines.append(f"{p_var}_arr = [{','.join([subr['start'] for subr in r])}];")
                sub_lines.append(f"{p_var} = {p_var}_arr[rint({len(r)})];")
                res.append("\n".join(sub_lines))
            # Case: range consists of multiple subranges
            else:
                sub_lines = []
                sub_vars = [""] * len(r)
                for j, subrange in enumerate(r):
                    sub_vars[j] = (f"{p_var}_{j}")
                    sub_lines.append(f"{sub_vars[j]} = {self.formatSubrange(subrange)}")
                sub_lines.append(f"{p_var}_arr = [{','.join(sub_vars)}];")
                sub_lines.append(f"{p_var} = {p_var}_arr[rint({len(sub_vars)})];")
                res.append("\n".join(sub_lines))


        return res

    def formatSubrange(self, r):
        if r["start"] == r["stop"]:
            return f"{r['start']};"

        return f"range({r['start']},{r['stop']},{r['step']});"

    def range_is_sequence(self, r):
        for subrange in r:
            if (subrange["start"] != subrange["stop"]):
                return False
        return True

    def formatAlgorithm(self):
        res = []

        res = res + self.formatRanges()

        res = res + self.formatAnswers()

        return "\n".join(res)

    def replaceAVariables(self, line):
        ans_vars = list(self.ans_lines.keys())
        matches = []
        replacements = {}
        for match in re.finditer(r"(\$A(\d{1,2}))(?![\d\w])", line):
            replacements[match.group(1)] = ans_vars[int(match.group(2))-1]
            matches.append(match.group(1))
        # I sort the A1...26 variables by size to make sure I don't replace variable A11 with the content for variable A1
        for a_val in set(sorted(matches, key= lambda a: len(a), reverse=True)):
            line = line.replace(a_val, replacements[a_val])
        return line


    def replaceANSCode(self, line, id):
        expr = p.parseExpr(line, id)
        line = p.toString(expr)
        line = self.replaceAVariables(line)
        return line



def insertChar(char, index, line):
    return line[:index] + char + line[index:]
