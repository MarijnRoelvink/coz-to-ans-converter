import template as t
from helpers import *

class XMLGenerator:
    def __init__(self, dir):
        self.dir = dir

    # [{
    # 'sub_questions':
    #   [{'id': '$6418960',
    #   'type': 0,
    #   'question_text': 'De kracht in staaf bb (in kN).',
    #   'ans_var': '$ans_6418960'}],
    # 'name': 'VAKW_011a',
    # 'id': '$3315749',
    # 'alg_text': '$P1=range(12,150,6);\n$P2=range(4,12,4);\n$F  =$P1\n$bb =$P2\n$ans_6418960 = (eq($P2, 4))*2/5*$P1+(eq($P2, 8))*$P1/2+(eq($P2, 12))*2/3*$P1',
    # 'main_text': '<h4>Gegeven:</h4>\n<p>Een vakwerk.</p>\n<h4>Parameters:</h4>\n<ul>\n\t<li>F = $F (kN)</li>\n\t<li>bb = $bb (staafnr.,zie "Gevraagd")</li>\n</ul>'
    # }]

    def generateXML(self, questions):
        tree = t.get_main_template()
        root = tree.getroot()

        for q in questions:
            main_question = self.fill_main_question(q)
            for sub in q["sub_questions"]:
                sub_question = self.fill_sub_question(sub)
                main_question.find("parts").append(sub_question.getroot())
            root.find("questions").append(main_question)
        tree.write(f"{self.dir}/manifest.xml")
        shutil.make_archive(f"{self.dir}", 'zip', self.dir)

    def fill_main_question(self, question):
        main_question = t.get_main_question_template()
        main_question.attrib["uid"] = question["id"]
        t.settext(main_question, "text", question["main_text"])
        t.settext(main_question, "name", question["name"])
        t.settext(main_question, "algorithm", question["alg_text"])
        t.settext(main_question, "weighting",
                  ",".join(["1" for s in question["sub_questions"]]))

        return main_question

    def fill_sub_question(self, sub):
        if(is_mult(sub["type"])):
            sub_question = t.get_mc_question_template()
            t.settext(sub_question, "answer", sub['ans_var'])
            t.add_choices(sub_question, sub["choices"])
        else:
            sub_question = t.get_numeric_question_template()
            t.settext(sub_question, "answer/num", sub['ans_var'])
        t.settext(sub_question, "name", "")
        t.settext(sub_question, "text", "")
        return sub_question