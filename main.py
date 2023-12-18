from quiz import Quiz, get_resource_directory

if __name__ == "__main__":
    RES_DIR = get_resource_directory()
    quiz = Quiz(RES_DIR)
    quiz.start_quiz()
