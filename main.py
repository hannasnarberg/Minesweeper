import random
import time


class Game:
    """
    Attributes:
    done: whether the game is done or not
    high_score_file: text file for storing high scores
    """
    def __init__(self, high_score_file):
        """
        Creates a new game
        :param high_score_file: text file for storing high scores.
        :return: nothing.
        """
        self.done = False
        self.high_score_file = high_score_file

    def execute_main_menu(self, choice):
        """
        Executes the menu option
        :param choice: an integer representing the menu choice.
        :return: nothing.
        """
        if choice == 1:
            self.play()
        elif choice == 2:
            show_instructions()
        elif choice == 3:
            self.show_high_score()
        else:
            self.quit()

    def play(self):
        """
        Sets up minefield.
        Loops until game is finished.
        Handles what happens after you win or loose the game.
        :return: nothing.
        """
        dimension_size = get_bounded_int_input(3, 30, "Select the width of the mine field"
                                                      " square you want (3 - 30): ")
        width = dimension_size
        height = dimension_size
        mine_amount = get_bounded_int_input(1, dimension_size**2 - 1, "How many mines do you want? (Maximum "
                                                                      "of " + str(dimension_size**2 - 1) + "):")
        game_field = MineField(height, width, mine_amount)
        done = False
        starting_time = time.time()
        while not done:
            print(game_field)
            coordinates = get_coordinates(dimension_size)
            y = coordinates[0]
            x = coordinates[1]
            if not game_field.matrix[y][x].visible:
                choice = get_letter_input(["f", "c"], "Do you want to flag/unflag (f) or clear (c) this cell?: ")
                if choice == "f":
                    game_field.flag_or_unflag(coordinates)
                    if game_field.check_all_mines_flagged():
                        done = self.game_won(game_field, starting_time, mine_amount, dimension_size)
                else:
                    if game_field.clear(coordinates):
                        if game_field.check_if_all_cleared():
                            done = self.game_won(game_field, starting_time, mine_amount, dimension_size)
                    else:
                        print("Oh no! You cleared a mine. Game over.")
                        game_field.clear_all()
                        flagged_mine_amount = game_field.count_flagged_mines()
                        print("You placed " + str(flagged_mine_amount) + " flags in the right place")
                        print(game_field)
                        done = True
            else:
                print("This cell is already cleared, please choose another")

    def game_won(self, game_field, starting_time, mine_amount, dimension_size):
        """
        Handles the game being won
        :param game_field: the game field
        :param starting_time: the starting time of the game
        :param mine_amount: the amount of mines on the mine field
        :param dimension_size: the dimension size of the mine field
        :return: True
        """
        finish_time = time.time()
        score = calculate_score(finish_time - starting_time, mine_amount, dimension_size ** 2)
        print("Congratulations! You won!")
        game_field.clear_all()
        print(game_field)
        self.write_high_score_to_file(score)
        self.show_high_score()
        return True

    def read_high_score_from_file(self, high_score_list):
        """
        Reads high scores from high score file and appends them to a high score list.
        :return: A list containing high scores
        """
        with open(self.high_score_file, "r") as file:
            for line in file:
                score_row = line.rstrip().split(";")
                if len(score_row) != 2:
                    raise IOError
                high_score_list.append(score_row)
            if len(high_score_list) > 10:
                raise IOError
        return high_score_list

    def write_high_score_to_file(self, score):
        """
        Writes score to high score file, if high score among the best.
        Handles any errors that could appear when the high score file is being read.
        :param score: The player's score of the game.
        :return: Nothing.
        """
        high_score_list = []
        try:
            high_score_list = self.read_high_score_from_file(high_score_list)
        except FileNotFoundError:
            pass
        except IOError:
            print("High score file corrupt, deleting all high scores")
            high_score_list = []
        high_score_list.sort(key=lambda x: float(x[1]), reverse=True)
        updated_high_score_list = update_high_score(score, high_score_list)
        with open(self.high_score_file, "w") as file:
            for element in updated_high_score_list:
                file.write(element[0] + ";" + element[1] + "\n")

    def show_high_score(self):
        """
        Prints the high score list.
        Handles any errors that could appear when the high score file is being read.
        :return: nothing.
        """
        high_score_list = []
        try:
            high_score_list = self.read_high_score_from_file(high_score_list)
        except FileNotFoundError:
            print("Sorry, no high scores could be found. Please play to set a high score")
        except IOError:
            print("High score file corrupt. If you start a game and win, a new high score file will be created.")
        else:
            print("\n" + "High Scores:")
            counter = 1
            for element in high_score_list:
                print(str(counter) + ". " + element[0] + " : " + str(round(float(element[1]))) + " points")
                counter += 1
            print()

    def quit(self):
        """
        Quits the program from the main menu
        :return: nothing
        """
        self.done = True


class MineField:
    """
    Attributes:
    height: Height of minefield
    width: Width of minefield
    mine_amount: Number of mines in matrix
    matrix: The matrix representation of the mine field.
    """

    def __init__(self, height, width, mine_amount):
        """
        Creates a mine field, a matrix represented by list of lists.
        Creates empty cells and places them in the matrix.
        Randomly changes some cells to contain mines.
        Changes the empty cells to contain a number representing the amount of neighboring mines.
        :param height: Height of minefield
        :param width: Width of minefield
        :param mine_amount: Number of mines in matrix
        """
        self.height = height
        self.width = width
        self.mine_amount = mine_amount
        self.matrix = []

        # Initialize empty cells in matrix
        for i in range(height):
            inner_list_matrix = []
            for j in range(width):
                inner_list_matrix.append(Cell("0", False, False))
            self.matrix.append(inner_list_matrix)

        # Change some random cells into mines
        for mine in range(mine_amount):
            mine_x = random.randrange(width)
            mine_y = random.randrange(height)
            while self.matrix[mine_y][mine_x].content == "M":
                mine_x = random.randrange(width)
                mine_y = random.randrange(height)
            self.matrix[mine_y][mine_x].content = "M"

        # Change content of cells to indicate number of neighboring mines
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[y])):
                if self.matrix[y][x].content != "M":
                    self.matrix[y][x].content = str(self.count_nearby_mines((y, x)))

    def __str__(self):
        """
        Displays the mine field. If cell is not visible, show "*", if the cell is flagged, show "f",
        otherwise the cell content.
        :return: string representation of mine field
        """
        matrix_string = "\n   "
        for x in range(len(self.matrix[0])):
            if x in range(0, 9):
                matrix_string += str(x + 1) + "  "  # Add single digit X coordinates to string representation
            else:
                matrix_string += str(x + 1) + " "   # Add double digit X coordinates to string representation
        matrix_string += "\n"
        for y in range(len(self.matrix)):
            if y in range(0, 9):
                matrix_string += " " + str(y + 1)   # Add single digit Y coordinates to string representation
            else:
                matrix_string += str(y + 1)         # Add double digit Y coordinates to string representation
            for cell in self.matrix[y]:
                if cell.flag and not cell.visible:
                    matrix_string += " f "
                elif cell.visible:
                    matrix_string += " " + cell.content + " "
                else:
                    matrix_string += " * "
            matrix_string += "\n"
        return matrix_string

    def count_nearby_mines(self, coordinates):
        """
        Counts how many nearby mines a cell has.
        :param coordinates: coordinates of the cell
        :return: integer representing number of nearby mines
        """
        y = coordinates[0]
        x = coordinates[1]
        nearby_mines = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i != 0 or j != 0:
                    if 0 <= (x + i) < self.width:
                        if 0 <= (y + j) < self.height:
                            if self.matrix[y + j][x + i].content == "M":
                                nearby_mines += 1
        return nearby_mines

    def clear_nearby_empty_cells(self, coordinates):
        """
        Checks if a cell is empty, and if empty, it makes the cell, as well as its neighboring empty cells,
        visible to the user, recursively.  It also makes the boarder of the empty area visible to the user.
        :param coordinates: the coordinates of the cell being checked.
        :return: nothing
        """
        y = coordinates[0]
        x = coordinates[1]
        if self.matrix[y][x].visible:
            return
        self.matrix[y][x].visible = True
        if self.matrix[y][x].content == "0":
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if i != 0 or j != 0:
                        if 0 <= (x + i) < self.width:
                            if 0 <= (y + j) < self.height:
                                self.clear_nearby_empty_cells((y + j, x + i))

    def flag_or_unflag(self, coordinates):
        """
        Flags the cell at the coordinates, and if already flagged, it unflags the cell.
        :param: coordinates: coordinates of the cell
        :return: nothing
        """
        y = coordinates[0]
        x = coordinates[1]
        self.matrix[y][x].flag = not self.matrix[y][x].flag

    def clear(self, coordinates):
        """
        Makes the cell at the coordinates visible to the user and if the cell content is empty it calls a function
        to make nearby empty cells empty too.
        :param: coordinates: coordinates of the cell
        :return: A boolean value. False if cell is a mine, True if not a mine.
        """
        y = coordinates[0]
        x = coordinates[1]
        if self.matrix[y][x].content != "M":
            if self.matrix[y][x].content == "0":
                self.clear_nearby_empty_cells(coordinates)
            else:
                self.matrix[y][x].visible = True
            return True
        else:
            return False

    def check_if_all_cleared(self):
        """
        Checks if all cells that do not contain a mine have been cleared.
        :return: A boolean value. True if all they have all been cleared, False if not.
        """
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[y])):
                if self.matrix[y][x].content != "M" and not self.matrix[y][x].visible:
                    return False
        return True

    def clear_all(self):
        """
        Makes all of the cell's content visible to the user.
        :return: nothing
        """
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[y])):
                self.matrix[y][x].visible = True

    def check_all_mines_flagged(self):
        """
        Checks if the flagged cells contain mines and if all mines are flagged.
        :return: A boolean value. True, if the flagged cells contain mines only and if all mines are flagged,
        otherwise False
        """
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[y])):
                if self.matrix[y][x].flag and self.matrix[y][x].content != "M":
                    return False
                if not self.matrix[y][x].flag and self.matrix[y][x].content == "M":
                    return False
        return True

    def count_flagged_mines(self):
        """
        Counts how many mines are flagged
        :return: An integer representing the amount of mines that are flagged.
        """
        flagged_mine_amount = 0
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[y])):
                if self.matrix[y][x].flag and self.matrix[y][x].content == "M":
                    flagged_mine_amount += 1
        return flagged_mine_amount


class Cell:
    """
    Attributes:
    content: the content of the cell. M for mine, 0 for cell with no nearby mines,
            1-8 for a cell that is not a mine, but next to 1-8 mines.
    visible: whether the cell is visible to the user or not
    flag: whether the cell is flagged or not
    """

    def __init__(self, content, visible, flag):
        """
        Creates a cell
        :param content: the content of the cell. M for mine, 0 for cell with no nearby mines,
        1-8 for a cell that is not a mine, but next to 1-8 mines.
        :param visible: whether the cell is visible to the user or not
        :param flag: whether the cell is flagged or not
        """
        self.content = content
        self.visible = visible
        self.flag = flag


def main_menu():
    """
    Shows the main menu to the user.
    :return: Nothing
    """
    print("Welcome to minesweeper!\n1. Play\n2. Show instructions\n3. Show high scores\n4. Quit")


def show_instructions():
    """
    Displays the instructions to the game.
    :return: Nothing
    """
    print("\nHow to play\n"
          "In this game you will be exploring a field, divided into cells. Some will be containing mines,\n"
          "some will not. The ones that do not contain a mine will be containing a number between 0 and 8,\n"
          "representing how many neighboring mines that cell has. Your goal is to figure out where the mines are.\n"
          "To prove that you know where they are you must either mark all of the cells containing mines (and no\n"
          "other cells) with a flag or clear (open) all cells not containing any mines.\n\n"
          "To clear or flag a specific cell you must first enter its column and row number. \n"
          "Then you will be asked to type in (f) to flag or (c) to clear the cell. An already \n"
          "flagged cell can be unflagged by simply using the flag command on that cell again.\n")


def get_coordinates(max_coordinate):
    """
    Gets input on the x and y coordinates, representing a cell.
    :return: a tuple representing the coordinates of the cell.
    """
    x_coordinate = get_bounded_int_input(1, max_coordinate, "Choose a cell and enter its column number: ") - 1
    y_coordinate = get_bounded_int_input(1, max_coordinate, "Now enter its row number: ") - 1
    return y_coordinate, x_coordinate


def get_bounded_int_input(lower_bound, upper_bound, prompt_string):
    """
    Gets the input of an integer in a specific range.
    :param lower_bound: the lower bound of the integer range
    :param upper_bound: the upper bound of the integer range
    :param prompt_string: instructions for the user input
    :return: an integer within the specified range.
    """
    while True:
        user_input = input(prompt_string)
        try:
            if int(user_input) in range(lower_bound, upper_bound + 1):
                return int(user_input)
            else:
                raise ValueError
        except ValueError:
            print("Your choice has to be an integer between " + str(lower_bound) + " and " + str(upper_bound))


def get_letter_input(accepted_letters_list, prompt_string):
    """
    Gets input in form of a letter among the accepted letters.
    :return: string in the form of a letter
    """
    while True:
        choice = input(prompt_string)
        if choice in accepted_letters_list:
            return choice
        else:
            print("You have to choose among the listed alternatives. Try again, please.")


def calculate_score(game_time, mine_amount, mine_field_size):
    """
    Calculates player score.
    :param game_time: the time it took for the player to play the game
    :param mine_amount: amount of mines in mine_field
    :param mine_field_size: the mine field's size
    :return: a float representing player score
    """
    score = (1000 * mine_amount)/mine_field_size + (50 * mine_field_size)/game_time
    return score


def get_non_empty_string_input(prompt_string):
    """
    Gets input in form of a string that is not empty.
    :param prompt_string: Instructions for the user input
    :return: A string that is not empty
    """
    while True:
        string = input(prompt_string)
        if len(string) > 0:
            return string
        else:
            print("Your name cannot be empty, please try again.")


def update_high_score(score, high_score_list):
    """
    Checks if player score is among the ten best in the high score list and if so, adds player to the list.
    :param score: The player score
    :param high_score_list: The high score list
    :return: Updated high score list
    """
    if len(high_score_list) < 10 or float(high_score_list[-1][1]) < score:
        player_name = get_non_empty_string_input("Congratulations, you made it to the high score list!"
                                                 " Enter name: ")
        new_score_row = [player_name, str(score)]
        high_score_list.append(new_score_row)
        high_score_list.sort(key=lambda x: float(x[1]), reverse=True)
    if len(high_score_list) > 10:
        high_score_list.pop()
    return high_score_list


if __name__ == '__main__':
    game = Game("high_score.txt")
    while not game.done:
        main_menu()
        game.execute_main_menu(get_bounded_int_input(1, 4, "What would you like to do?: "))
