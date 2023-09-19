from xml_generator import XMLGenerator
from coz_parser import COZParser
from helpers import *
import rapidjson


def load_data(file_name):
    with open(file_name, "r") as f:
        data = rapidjson.load(f, parse_mode=rapidjson.PM_COMMENTS | rapidjson.PM_TRAILING_COMMAS)
    data = data['CDB']

    return data


def convertAllQuestions(data_dir="../data/export-ct1031.json", target_dir= "../data/output"):
    runProgram("main", "", data_dir, target_dir, "/main")


def testQuestion(q_name, data_dir="../data/export-ct1031.json", target_dir= "../data/output"):
    runProgram("test", q_name, data_dir, target_dir, "/test")



def runProgram(type, q_name, data_dir, target_dir, suffix):
    data = load_data(data_dir)
    dataset_name = data_dir.split("/")[-1].replace(".json", "")
    parser = COZParser(target_dir+suffix, dataset_name, data)
    if(type == "test"):
        res = parser.testQuestion(q_name)
    else:
        res = parser.makeAllQuestions()
    generator = XMLGenerator(target_dir+suffix)
    generator.generateXML(res)
    generateProblemList(res, target_dir)

