import lxml.etree as ET
import string

parser = ET.XMLParser(strip_cdata=False)
prefix = "../data/templates"


def xtext(input):
    return ET.CDATA(f"  {input}  ")

def settext(node, element, text):
    node.find(element).text = xtext(text)

def add_choices(node, n):
    alphabet = list(string.ascii_uppercase)
    container = node.find("choices")
    for i in range(n):
        choice = ET.Element("choice")
        choice.text = xtext(alphabet[i])
        container.append( choice )

def get_main_template():
    return ET.parse(f'{prefix}/main.xml', parser)

def get_main_question_template():
    return ET.parse(f'{prefix}/main_question.xml', parser).getroot()

def get_numeric_question_template():
    return ET.parse(f'{prefix}/numeric_question.xml', parser)

def get_mc_question_template():
    return ET.parse(f'{prefix}/mc_question.xml', parser)
