import os
import shutil
import re
import pandas as pd


question_types = {
    0: "NUMERIC",
    1: "MULTIPLE_CHOICE",
    2: "ABSOLUTE_NUMERIC",
    3: "FORMULA",
    4: "NUMERICAL_EXPRESSION",
    5: "TEXT_INPUT"
}
def is_mult(type):
    return question_types[type] == "MULTIPLE_CHOICE"

def is_numeric(type):
    type = question_types[type]
    return type == "NUMERIC" or type == "ABSOLUTE_NUMERIC"

def is_abs_numeric(type):
    return question_types[type] == "ABSOLUTE_NUMERIC"

def is_supported(type):
    type = question_types[type]
    if(type == "ABSOLUTE_NUMERIC"):
        return "Absolute numeric question type, check question text"
    if(type == "MULTIPLE_CHOICE"):
        return ""
    if(type == "NUMERIC"):
        return ""
    return f"question type unsupported: {type}"

# Checks whether the given string consists solely of numbers
def is_number(ans_formula):
    return re.fullmatch("\d+(\.\d+){0,1}", ans_formula) != None

def makedir(dir):
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
    os.makedirs(dir)

# Get the corresponding value to the key, or else an equivalent empty value, depending on the type
def getKey(item, key, d_type="STRING"):
    if(key in item and item[key] != None):
        return item[key]

    if d_type == "ARRAY":
        return []
    # Default case: assume it is a string
    return ""

def getRanges(fields):
    res = getKey(fields, 'Parameterranges', d_type="ARRAY")
    if res == None:
        return []
    if None in res:
        return []
    return res

def getSubquestions(fields, data):
    res = []
    for sub in getKey(fields, 'Deelvraagnummers', d_type="ARRAY"):
        subQ = list(filter(lambda x: x['itemid'] == sub, data['DVR']))
        #Check if subquestion has a corresponding item, else just add an empty unit
        if(len(subQ) > 0):
            res.append(subQ[0])
        else:
            res.append({"itemid": sub})
    return res

def generateProblemList(questions, target_dir):
    problems = []
    for q in questions:
        flags = []
        for key in ["alg_text", "main_text"]:
            match = re.search("FLAG\[(.*?)\]", q[key])
            if(match != None):
                flags.append(match.group(1))
        for sub in q["sub_questions"]:
            type_memo = is_supported(sub["type"])
            if(type_memo != ""):
                flags.append(type_memo)
            match = re.search("FLAG\[(.*?)\]", sub["ans_var"])
            if (match != None):
                flags.append(match.group(1))
        if(len(flags) > 0):
            problems.append({"name": q["name"], "problems": ";".join(flags)})

    df = pd.DataFrame({
        "Name": [p["name"] for p in problems],
        "Problems": [p["problems"] for p in problems]
    })
    print(df)

    df.to_excel(f'{target_dir}/problems.xlsx')


