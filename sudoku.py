import numpy as np
from random import randint
import os
from itertools import permutations


def main():
    # load file into string
    if os.path.exists("sudoku.csv"):
        with open("sudoku.csv") as file:
            content = file.readlines()
            # TODO: make random once done with testing
            puzzle_index = content[6]
            puzzle_str = puzzle_index.split(',')[0]
            solution_str = puzzle_index.split(',')[1]
            solution_str = solution_str.split('\n')[0]

    else:
        print("Couldn't find sudoku files")
        return

    # all the possible addition lines in the puzzle
    # horizontal lines (x9), vertical lines (x9), boxes
    horizontal = [[(9 * j) + i for i in range(9)] for j in range(9)]
    vertical = [[(9 * i) + j for i in range(9)] for j in range(9)] 
    boxes = [[(9 * j) + (3 * k) + (27 * l) + i for j in range(3) for i in range(3)] for l in range(3) for k in range(3)]  
    lines = [horizontal, vertical, boxes] 

    # loop until finished puzzle
    offset = 0
    count = 0
    print("Initial board state:")
    print_board(puzzle_str)
    while True:
        # find the first line/box with the least number of gaps
        least_gappy_lines = find_least_gaps(puzzle_str, lines, offset)
        if not least_gappy_lines:
            print("Offset overflowed.")
            break

        board_updates = 0
        # for each of those lines, find which numbers need to fill those gaps
        for line in least_gappy_lines:
            missing_numbers = get_missing_numbers(puzzle_str, line, lines)
            # simulate the possible arrangements of those numbers in the puzzle, store in a list of potential puzzles
            possible_puzzles = get_possible_arrangements(puzzle_str, lines, line, missing_numbers)
            # eliminate arrangements that are not allowed
            remaining_puzzles = [puzzle for puzzle in possible_puzzles if check_arrangement(puzzle, lines)]

            # if only one arrangement allowed, add it to the puzzle
            if len(remaining_puzzles) == 1:
                puzzle_str = remaining_puzzles[0]
                print(f"Single valid line found; completing line {line}:")
                board_updates += 1
            else:
                # check which of the numbers are constant throughout all valid puzzles, and put into puzzle_str
                new_puzzle_str, update_count = update_board_partially(puzzle_str, remaining_puzzles, lines, line, missing_numbers)
                if new_puzzle_str != puzzle_str:
                    puzzle_str = new_puzzle_str
                    print(f"Partially valid line found; updating line {line} with {update_count} numbers")

                    
        # no lines left in least_gappy_lines, or no definitive solutions for the lines left, or puzzle is solved
        # check if there are lines left in least_gappy_lines, ie. some of the lines dont have definitive solved states
        if check_unresolved_states(puzzle_str, least_gappy_lines, lines) and board_updates == 0:
            offset += 1
        else:
            offset = 0

        count += 1
            
        # check if puzzle has been solved
        if puzzle_solved(puzzle_str):
            print("SOLUTION FOUND!")
            print("Iterations taken:", count)
            print_board(puzzle_str)
            check_answer(puzzle_str, solution_str)
            break
        
        print("Iteration =", count)
        print("Board updates this iteration =", board_updates)
        print("Board at end of iteration:")
        print_board(puzzle_str)

        if count == 15:
            print("Unable to complete the solve. Current board state:")
            print_board(puzzle_str)
            break

   
    
    

    


    




def find_least_gaps(puzzle_str, lines, offset):
    spaces = []
    for orientation in lines:
        for line in orientation:
            space_count = 0
            for item in line:
                if puzzle_str[item] == '0':
                    space_count += 1
            spaces.append(space_count)
    # eliminate if line has no gaps
    for i, length in enumerate(spaces):
        if length == 0:
            spaces[i] = 10
    # eliminate if offsetting, ie. getting second least number of gaps
    for _ in range(offset):
        least_spaces = min(spaces)
        for i, length in enumerate(spaces):
            if length == least_spaces:
                spaces[i] = 10
    if min(spaces) == 10:
        # offset overflow state
        return None
    least_gappy_lines = [i for i in range(len(spaces)) if spaces[i] == min(spaces)]
    return least_gappy_lines
            

def get_missing_numbers(puzzle_str, line, lines):
    # make list of 1 - 9 and remove any numbers already in line, leaving the missing numbers
    list = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    remaining_list = list.copy()
    puzzle_line = [puzzle_str[i] for i in lines[line // 9][line % 9]]
    for i in list:
        if i in puzzle_line:
            remaining_list.remove(i)
    return remaining_list
    


def get_possible_arrangements(puzzle_str, lines, line, missing_numbers):
    # return list of possible puzzle states, containing all arrangements of the missing numbers
    puzzle_states = []
    # get positions of where missing numbers need to go ('0' is the position)
    puzzle_index_line = lines[line // 9][line % 9]
    # get permutations of missing numbers as a list of lists
    arrangements = [list(i) for i in permutations(missing_numbers)]
    
    for arrangement in arrangements:
        possible_puzzle_list = [i for i in puzzle_str]
        j = 0
        for k in puzzle_index_line:
            
            if possible_puzzle_list[k] == '0':
                possible_puzzle_list[k] = str(arrangement[j])
                j += 1
        possible_puzzle_str = ''.join(possible_puzzle_list)
        puzzle_states.append(possible_puzzle_str)
    return puzzle_states




def print_board(puzzle_str):
    puzzle_list = [int(i) for i in puzzle_str]
    for i in range(9):
        print(puzzle_list[(9 * i):(9 * (i+1))])
    print('')
    print('')
        


def check_arrangement(puzzle_str, lines):
    # output true if the puzzle is valid, false if not
    # check each orientation
    for orientation in lines:
        for line in orientation:
            reference_line = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
            test_line = [puzzle_str[item] for item in line]
            for i in reference_line:
                if test_line.count(i) > 1:
                    return False
    return True



def check_unresolved_states(puzzle_str, least_gappy_lines, lines):
    for line_index in least_gappy_lines:
            puzzle_line = [puzzle_str[i] for i in lines[line_index // 9][line_index % 9]]
            if '0' in puzzle_line:
                return True
    return False


def update_board_partially(puzzle_str, remaining_puzzles, lines, line, missing_numbers):
    puzzle_list = [str(i) for i in puzzle_str]
    updates = 0
    # go through each element of the line being altered and if all boards are the same for one number, put that one into puzzle_str
    puzzle_line = lines[line // 9][line % 9] # list of indexes of the numbers on the line being updated
    for i in missing_numbers:
        number = str(i)
        position_list = []
        for test_puzzle in remaining_puzzles:
            test_puzzle_line = [test_puzzle[k] for k in puzzle_line]
            position_in_test_line = test_puzzle_line.index(number)
            position_list.append(puzzle_line[position_in_test_line])
        if len(set(position_list)) == 1:
            puzzle_list[position_list[0]] = number
            updates += 1
    puzzle_str = ''.join(puzzle_list)
    return puzzle_str, updates



def check_answer(puzzle, solution):
    if puzzle == solution:
        print("Puzzle solved correctly")
    else:
        print("Error found in solution; correct solution was:")
        print(solution)
        print_board(solution)


def puzzle_solved(puzzle):
    for i in puzzle:
        if i == '0':
            return False
    return True


if __name__ == "__main__":
    main()