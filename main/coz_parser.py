import cleaner as c
import algorithm as a
from helpers import *
import re
import base64


class COZParser:
    def __init__(self, dir, dataset_name, data):
        self.dir = dir
        self.dataset_name = dataset_name
        self.data = data
        self.questions = self.data['VRG']

    def testQuestion(self, q_name):
        question = [q for q in self.questions if getKey(q['fields'], "Naam") == q_name]
        self.questions = question
        return self.parseQuestions()

    def makeAllQuestions(self):
        self.questions = self.data['VRG']
        return self.parseQuestions()

    def parseQuestions(self):
        makedir(f"{self.dir}/web_folders")
        res = []
        with open(f"../data/check/check_{self.dataset_name}.txt", "w") as f:
            for item in self.questions:
                curr_res = self.parseQuestion(item)
                self.writeLog(curr_res, f)

                # Only add item to the array if it has a name
                if (curr_res["name"] != ""):
                    res.append(curr_res)
        return res

    def writeLog(self, curr_res, f):
        f.write(f'Name: {curr_res["name"]}\n')
        f.write(f"Algorithm: \n{curr_res['alg_text']}\n")
        f.write(f"Main text: \n{curr_res['main_text']}\n")
        f.write(f"Subquestions:\n")
        for sub in curr_res["sub_questions"]:
            f.write(f"\t{question_types[sub['type']]}, ")
            if(is_mult(sub['type'])):
                f.write(f"Answer: {sub['ans_var']}, Choices: {sub['choices']}\n")
            else:
                f.write(f"Answer: {sub['ans_var']}\n")
        f.write('\n *****************************\n')

    def parseQuestion(self, item):
        fields = item['fields']

        curr_res = {"sub_questions": [], "name": getKey(fields, "Naam")}

        ranges = getRanges(fields)
        params = c.clean_parametertekst(getKey(fields, 'Parametertekst'))
        alg = a.Algorithm(ranges, params)
        sub_text = "\n<br>\n<h4>Gevraagd:</h4>"

        for i, sub in enumerate(getSubquestions(fields, self.data)):
            if ("fields" in sub):
                type = sub["fields"]['Vraagsoort']
                text = sub['fields']['Vraagtekst']
                sub_res = {"id": sub['itemid'],
                           "type": type,
                           "ans_var": ""}

                text = c.clean_DVR_tekst(text)
                sub_text = f"{sub_text}\n{text}\n{c.create_sub_tag(i)}"

                if (is_mult(type)):
                    choices, answer = self.parseMCAnswer(sub, alg)
                    sub_res["choices"] = choices
                    sub_res["ans_var"] = answer
                if (is_numeric(type)):
                    sub_res["ans_var"] = self.parseNumericAnswer(sub, alg)

                curr_res["sub_questions"].append(sub_res)
            else:
                curr_res["sub_questions"].append(
                    {"id": sub['itemid'], "type": 0,
                     "ans_var": f"FLAG[No subquestion found for id: {sub['itemid']}]"})

        alg_text = alg.formatAlgorithm()
        figure_tag = self.createImgFromQuestion(item)
        param_text = alg.formatParamText()
        main_text = c.clean_gegevenstekst(getKey(fields, "Gegevenstekst")) + figure_tag + param_text + sub_text

        curr_res["id"] = item["itemid"]
        curr_res["alg_text"] = alg_text
        curr_res["main_text"] = main_text

        return curr_res

    # 1. Parses the answer formula of the numeric subquestion
    # 2. Adds the answer line (e.g. $ans_9943564 = 5) to the algorithm object
    # 3. Returns the answer variable ($ans_9943564) that needs go in the <answer> tag
    def parseNumericAnswer(self, sub, alg):
        # Parse the answer variable name and clean the answer formula
        answer = re.sub(r"\$", r"$ans_", sub['itemid'])
        ans_formula = c.clean_formula_answer(sub['fields']['Formule'])
        alg.addAnsLine(answer, ans_formula)
        return answer

    # 1. Parses the answer formula of the MC subquestion
    # 2. Checks how many choices the question has
    # 3. Returns the number of choices and the correct choice
    def parseMCAnswer(self, sub, alg):
        # Parse the answer variable name and clean the answer formula
        answer = re.sub(r"\$", r"$ans_", sub['itemid'])
        ans_formula = c.clean_formula_answer(sub['fields']['Formule'])
        diff_choice_match = re.match(r"(\d+):(\d+)", ans_formula)

        # Check if the answer is a simple number, this means it's a 4 choice question
        if (is_number(ans_formula)):
            choices = 4
            corr_number = ans_formula
        # Check if there is a number preceding it with a :, this means that it has a different number of choices
        elif (diff_choice_match != None):
            choices = diff_choice_match.group(1)
            corr_number = diff_choice_match.group(2)
        # Check if answer is a variable
        else:
            choices = 0
            corr_number =  f"FLAG[Unsupported by ANS: Multiple Choice type with parametrized answer: {answer}]"
            alg.addAnsLine(answer, ans_formula)

        return int(choices), corr_number

    def createImages(self, data):
        for img in data['MED']:
            self.createImage(img)

    # Input: question object from json file
    # Output: tag for question in Möbius format
    def createImgFromQuestion(self, question):
        figure = getKey(question['fields'], "Figuur")
        if (figure != ""):
            img = list(filter(lambda x: x['itemid'] == figure, self.data['MED']))[0]
            self.createImage(img)
            figure = re.sub(r'\$', '', figure)
            figure_tag = c.create_image_tag(figure)
            return figure_tag

        return ""

    # input: img object from json file
    def createImage(self, img):
        imgdata = img['fields']['Gegevensblok']
        imgdata = base64.b64decode(imgdata.split(",")[1])

        id = re.sub(r'\$', '', img['itemid'])
        img_name = f"img_{id}.png"
        with open(f"{self.dir}/web_folders/{img_name}", "wb") as fh:
            fh.write(imgdata)
