import re
from tkinter import Tk, font

root = Tk()
font_reg = "|".join([f + ";" for f in font.families()])


# Removes markup language: \par, {, }
def removeMarkup(text):
    res = text
    res = layoutTagsToHTML(r"\\sub(.+?)\\nosupersub", "sub", res)
    res = layoutTagsToHTML(r"\\super(.+?)\\nosupersub", "sup", res)
    res = re.sub(r"\\[\w\d]*", "", res)
    res = re.sub(r"{|}*", "", res)
    res = re.sub(r"Arial;|Terminal;|Symbol;|Courier New;|MS Sans Serif;|Tahoma;|Segoe UI;|Times New Roman;|Book Antiqua;|Lucida Sans Unicode;|Default;", "", res)
    res = re.sub(font_reg, "", res)
    res = re.sub(r"\* Msftedit [\d.]*;", "", res)
    res = re.sub(r"\* Riched20 [\d.]*", "", res)
    res = re.sub(r"TTEB6t00;", "", res)
    return res

# Changes layout tags that indicate for example super- or subscripts
# to html tags that can be parsed by Möbius and Ans
def layoutTagsToHTML(regex, tag, text):
    match = re.search(regex, text)
    while match != None:
        content = match.group(1)
        content = removeMarkup(content).strip()
        text = text.replace(match.group(0), f"<{tag}>{content}</{tag}>")
        match = re.search(regex, text)
    return text



# Gets the variable name from a parametertekst line
def getParVar(text):
    var = re.findall(r"(.+?)=", text)
    if (len(var) > 0):
        return var[0].replace(" ", "")
    return ""

def clean_infotekst(text):
    text = re.sub(r"\{\\object\\objemb\{(.|\n)*?\}\}\}", " FLAG[visio object]", text)
    res = removeMarkup(text)

    lines = res.split("\n")
    # Remove trailing whitespaces and empty lines
    lines = [l.strip() for l in lines]
    lines = list(filter(lambda l: len(l) > 0, lines))
    res = "\n".join(lines)
    return res


def clean_DVR_tekst(text):
    text = clean_infotekst(text)
    # Remove trailing whitespaces and split text between newlines and ; characters
    res = [l.strip() for l in re.split(";|\n", text)]

    # Remove empty lines and lines that start with * msedit...
    res = list(filter(lambda l: len(l) > 0 and re.match(r"\*", l) == None, res))

    return "\n".join(res)


def clean_gegevenstekst(text):
    res = clean_infotekst(text)
    return f"<h4>Gegeven:</h4>\n<p>{res}</p>"

# Removes spaces and gives text uniform caps
def clean_formula_answer(text):
    text = text.upper()
    text = text.strip()

    return text

def clean_parametertekst(text):
    res = removeMarkup(text)
    res = re.sub(r":\d+:\d+", "", res)
    res = re.sub(r"(\w)<\^", r"\1", res)

    # Remove trailing whitespaces and split text between newlines and ; characters
    res = [l.strip() for l in re.split(";|\n", res)]

    # Remove empty lines and lines that start with * msedit...
    res = list(filter(lambda l: len(l) > 0 and re.match(r"\*", l) == None, res))

    return res

def create_image_tag(figure_id):
    return f'\n<img alt="" src="web_folders/img_{figure_id}.png" style="float: right; width: 400px; height: 400px;">'

def create_sub_tag(i):
    return f"<{i+1}>\n"