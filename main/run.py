from main import *

# Location of your json file
input_file = ""

# Location of the directory where you want to store your results
target_dir= "../data/output"

if __name__ == "__main__":
    # Code to run if you want to run all the questions:
    convertAllQuestions(input_file, target_dir)

    # Code to run if you want to test a specific question, input is name of question
    # Results will be in target_dir/test and in target_dir/test.zip
    # Decomment line below:
    # testQuestion("EXAMPLE_01", input_file, target_dir)

