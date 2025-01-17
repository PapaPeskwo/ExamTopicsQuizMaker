from io import TextIOWrapper
from _classes import CardList, os, re
import random
from datetime import datetime 
import textwrap
import os


def choose_resources_directory():
    """
    Lists all directories starting with 'res_' and the names of HTML files inside each.
    Allows the user to choose based on these file names.
    """
    res_dirs = [d for d in os.listdir() if os.path.isdir(d) and d.startswith("res_")]
    if not res_dirs:
        raise Exception("No resource directories found starting with 'res_'")

    options = []
    for dir in res_dirs:
        html_files = [file for file in os.listdir(dir) if file.endswith('.html')]
        for file in html_files:
            file_name_without_extension = os.path.splitext(file)[0]
            options.append((dir, file_name_without_extension))

    for i, option in enumerate(options):
        print(f"{i + 1}: {option[1]} (in {option[0]})")
    
    choice = 0
    while choice < 1 or choice > len(options):
        try:
            choice = int(input("Choose a resource (number): "))
        except ValueError:
            pass
    
    chosen_dir, _ = options[choice - 1]
    return chosen_dir


def get_resource_directory():
    return choose_resources_directory()


class Quiz:
    def __init__(self, resources_dir = None) -> None:
        if resources_dir is None:
            resources_dir = choose_resources_directory()
        self.__cardlist = CardList(resources_dir)
        self.__cardlist = CardList(resources_dir)
        self.__log_dirname = "wrong_answers"  # the name of the directory where the .txt files with wrong answers will be stored
        
        self.__init_questions_per_quiz()        
        self.__init_show_answer_immediately() 

        self.__create_wrong_answers_directory()
        
        self.__init_questions_order()
        self.quiz_cards = self.__generate_quiz()


    def __init_questions_order(self):
        """
        Asks the user if they want the questions in order and stores the response.
        """
        self.__questions_in_order = input("Do you want the questions to be in order [y/N]? ").lower() == 'y'


    def __init_questions_per_quiz(self):
        """
            Initialize the variable that shows how many questions should be shown in a quiz run
        """
        try:
            self.__questions_per_quiz = int(input("How many questions do you want to have? (Max: " + str(len(self.__cardlist.cards_list)) + ") "))

            while self.__questions_per_quiz > len(self.__cardlist.cards_list):
                self.__questions_per_quiz = int(input("Please pick a NUMBER. (Max: " + str(len(self.__cardlist.cards_list)) + ")"))
        except:
            print("Defaulted to max number of questions.")
            self.__questions_per_quiz = len(self.__cardlist.cards_list)

        use_specific_range = input("Do you want the questions to be from a specific range [y/N]? ").lower() == 'y'
        if use_specific_range:
            self.__range_selection = input("Do you want the {} questions to be from the \n[1] beginning\n[2] end\nPlease select 1 or 2: ".format(self.__questions_per_quiz))
        else:
            self.__range_selection = None


    def __init_show_answer_immediately(self):
        """
            Initializes the variable that decides if you want the correct answer shown after you respond
        """
        self.__show_answer_immediately = \
            input("Do you want to have the answer shown immediately after you respond?\n(If not, you will be shown a score at the end and a file will be generated with the wrong answers anyway.)[Y/n] ")

        if self.__show_answer_immediately == "":  # if only Enter was pressed
            self.__show_answer_immediately = "y"  # default to y

        self.__show_answer_immediately = self.__show_answer_immediately.lower()
        while self.__show_answer_immediately != "n" and self.__show_answer_immediately != "y":
            self.__show_answer_immediately = \
                input("Please pick between 'y'(yes) or 'n'(no): ")
            self.__show_answer_immediately = self.__show_answer_immediately.lower()


    def __generate_quiz(self) -> list:
        """
        Generate a list of card objects that are limited by the size of how
        many questions the player wants to have, and either in order or randomized.
        """
        if self.__range_selection == "1":
            # Select from the beginning
            selected_cards = self.__cardlist.cards_list[:self.__questions_per_quiz]
        elif self.__range_selection == "2":
            # Select from the end
            selected_cards = self.__cardlist.cards_list[-self.__questions_per_quiz:]
        else:
            # No specific range, use the whole list
            selected_cards = self.__cardlist.cards_list[:self.__questions_per_quiz]

        if not self.__questions_in_order:
            random.shuffle(selected_cards)

        return selected_cards


    def __clear(self):
        """
            Clear the terminal window
        """
        print("")  # get a new empty line
        # for windows
        if os.name == 'nt':
            _ = os.system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = os.system('clear')    


    def __create_wrong_answers_directory(self):
        try:
            os.mkdir(self.__log_dirname)
        except:
            print("Wrong answers directory already exists. Continuing..")
            
    def __init_answers_file(self) -> TextIOWrapper:
        """
            Initialize the filename with the current datetime, while omitting spaces and colon
        """
        filename = re.sub(" ", "_", str(datetime.now())).split(".")[0]  # remove the miliseconds as they were delimited by '.'
        filename = re.sub(":", "-", filename)  # remove ':' as they are a special char on Windows.. 
        filename += ".txt"
        filename = os.path.join(self.__log_dirname, filename)
        wrong_answers_file = open(filename, "w")  # file where the wrong answers will be written to

        return wrong_answers_file


    def __write_to_file(self, wrong_answers_file, card, your_answer):
        
        wrapper = textwrap.TextWrapper()  # wrap text so it looks better

        wrong_answers_file.write(card.question_number + " " + wrapper.fill(text= card.question) + "\n")
        wrong_answers_file.write("-" * 40 + "\n")
        for ans in card.answers:
            try:
                # ans = str(ans.encode('utf-8'))  # some answers give a UnicodeEncodeError: 'charmap' codec can't encode character '\u05d2' in position 192: character maps to <undefined>
                wrong_answers_file.write(wrapper.fill(text= ans) + "\n")  # one answer had a weird encoding
            except:
                wrong_answers_file.write(str(ans) + "\n")

        wrong_answers_file.write("Your answer: " + your_answer.upper() + "\n")
        wrong_answers_file.write("Correct answer: " + card.correct_answer + "\n")
        wrong_answers_file.write("-" * 40 + "\n\n")


    def start_quiz(self):
        """ 
            The main logic function for the quiz to run
        """
        self.__clear()

        correct_answers = 0  # initialize correct answers

        wrong_answers_file = self.__init_answers_file()
        wrapper = textwrap.TextWrapper()  # wrap text so it looks better
        
        print("Your quiz starts now. Please enter one single character, coresponding to the answers (A,B,C or D). Answers are NOT case sensitive, so response 'b' is good if 'B' is the correct answer.\n")
        input("Press Enter to continue..")

        for index, card in enumerate(self.quiz_cards):
            print("")
            print(str(index + 1) + "/" + str(self.__questions_per_quiz))
            print(card.question_number + " " + wrapper.fill(text= card.question))
            print("-" * 40)
            for ans in card.answers:
                print(wrapper.fill(text= ans))
            print("-" * 40)
            your_answer = ""
            while your_answer.upper() not in ['A', 'B', 'C', 'D']:
                your_answer = input("Your answer: ")

            if your_answer.upper() == card.correct_answer:
                correct_answers += 1
            else:
                # write to the wrong answer to the file
                self.__write_to_file(wrong_answers_file, card, your_answer)
                            
            if self.__show_answer_immediately == "y":
                print("Correct answer: ", card.correct_answer)
                input("Press Enter to continue..")

        wrong_answers_file.close()  # writing is done so we close the file
        
        print("=^=" * 40)
        print("The quiz is DONE! Good job!")
        print("Your score: " + str(correct_answers) + "/" + str(self.__questions_per_quiz))
        score_in_percent = (correct_answers / self.__questions_per_quiz) * 100
        print("Your score in percent: {:.2f}%".format(score_in_percent))
