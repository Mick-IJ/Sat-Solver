from itertools import chain
from collections import Counter
from random import choice, sample
from copy import deepcopy
from timeit import default_timer as timer
import sys
sys.setrecursionlimit(5000)

rules_filename = 'sudoku-rules.txt'
backtrack_counter = 0
split_counter = 0
putnam_counter = 0


def get_rules_result_format():
    file = open(rules_filename, 'r')
    text = file.readlines()

    rules = list()
    for row in text[1:]:
        rules.append(list(map(int, row.strip(' 0\n').split(' '))))

    result = dict()
    for x in list(set(chain.from_iterable(rules))):
        if x > 0:
            result[x] = 'unknown'

    return rules, result


def get_sudokus(filename, n_rows, samplesize):
    file = open(f'{filename}.txt', 'r')
    text = file.readlines()

    puzzles = list()
    start_list = list()
    for i in range(1, n_rows+1):
        for j in range(1, n_rows+1):
            start_list.append(int(str(i)+str(j)))

    for sudoku in sample(text, samplesize):
        sudoku_clauses = list()
        for i in range(n_rows*n_rows):
            if sudoku[i] != '.':
                sudoku_clauses.append([int(str(start_list[i])+str(sudoku[i]))])
        puzzles.append(sudoku_clauses)

    return puzzles


def format_result(result_dict):
    result = []

    for key in result_dict:
        if result_dict[key]:
            result.append(key)

    return result


def adjust_counters(i):
    global backtrack_counter, split_counter, putnam_counter
    i += 1
    backtrack_counter = 0
    split_counter = 0
    t = timer()
    putnam_counter = 0
    return putnam_counter, backtrack_counter, split_counter, t, i


def check_tautology(clause):

    for variable in clause:
        if -variable in clause:
            return True

    return False


def check_pure_literals(rules):
    variable_dict = dict(Counter(chain.from_iterable(rules)))
    pure_literals = list()

    for key in variable_dict.keys():
        if -key not in variable_dict.keys():
            pure_literals.append(key)

    return [pure_literals]


def check_tautology_unit(rules, first_it=False):
    to_remove = list()
    unit_clauses = list()

    for clause in rules:
        if first_it and check_tautology(clause):
            to_remove.append(clause)

        if len(clause) == 1:
            unit_clauses.append(clause)

        elif len(clause) == 0:
            return rules, unit_clauses, 'Backtrack'

    for clause in to_remove:
        rules.remove(clause)

    return rules, unit_clauses, 'Loop'


def set_clause(rules, result, variables_to_set):
    # t = timer()

    for variable in variables_to_set:
        state = True if variable > 0 else False
        result[abs(variable)] = state

        new_rules = list()
        for clause in rules:
            if -variable in clause:
                clause.remove(-variable)
                new_rules.append(clause)
            elif (variable not in clause) and (-variable not in clause):
                new_rules.append(clause)

        rules = new_rules

    # print(len(variables_to_set), round(timer() - t, 2))
    return rules, result


def simplify_rules(rules, result, first_it=False):
    variables_to_set = list()

    rules, unit_clauses, action = check_tautology_unit(rules, first_it)
    if action == 'Backtrack':
        return rules, result, 'Backtrack'

    variables_to_set.extend(check_pure_literals(rules))
    variables_to_set.extend(unit_clauses)

    variables_to_set = list(chain.from_iterable(variables_to_set))
    for variable in variables_to_set:
        if -variable in variables_to_set:
            if not first_it:
                return rules, result, 'Backtrack'
            if first_it:
                return rules, result, 'Unsolvable'

    if len(variables_to_set) > 0:
        new_rules, new_result = set_clause(rules, result, variables_to_set)
        return new_rules, new_result, 'Loop'
    elif len(variables_to_set) == 0 and len(rules) == 0:
        return rules, result, 'Satisfied'
    else:
        return rules, result, 'Split'


def backtrack(history):
    global backtrack_counter
    backtrack_counter += 1

    variable, rules, result = history[-1]

    if variable == 'Initial':
        history = []
        putnam(rules, result, history, first_it=True)
    else:
        history = history[:-1]
        rules, result = set_clause(rules, result, [-variable])
        putnam(rules, result, history)


def split(rules, result, history):
    global split_counter
    split_counter += 1

    # IMPLEMENT HEURISTIC HERE
    variable = choice(list(set(chain.from_iterable(rules))))

    rules, result = set_clause(rules, result, [variable])
    history.append((variable, deepcopy(rules), deepcopy(result)))

    putnam(rules, result, history)


def putnam(rules, result, history, first_it=False):
    global putnam_counter
    putnam_counter += 1

    while True:
        rules, result, action = simplify_rules(rules, result, first_it)
        if action != 'Loop':
            break

    if first_it:
        history.append(('Initial', deepcopy(rules), deepcopy(result)))

    if action == 'Split':
        split(rules, result, history)
    elif action == 'Backtrack':
        backtrack(history)
    elif action == 'Unsolvable':
        print('UNSOLVABLE')
    else:  # action == 'Satisfied'
        print('SATISFIED')
        return format_result(result)


def sat_solver(filename, n_rows, sample_size):
    global backtrack_counter, split_counter, base_rules, result_template, putnam_counter

    base_rules, result_template = get_rules_result_format()
    sudokus = get_sudokus(filename, n_rows, sample_size)

    i = 1
    for sudoku in sudokus:
        print('\n\nSUDOKU', i)
        putnam_counter, backtrack_counter, split_counter, t, i = adjust_counters(i)

        rules = deepcopy(base_rules)
        rules.extend(sudoku)
        result = deepcopy(result_template)

        putnam(rules, result, history=list(), first_it=True)

        print('\ntime:\t', round(timer() - t, 2),
              '\nbacktracks:\t', backtrack_counter, '\nsplits:\t', split_counter,
              '\nputnam its:\t', putnam_counter)


# putnam([[-1, 2], [1, 2], [-2]], {1: 'uk',2: 'uk',3: 'uk', 4: 'uk'},
#       history=list(), first_it=True)
sat_solver('1000 sudokus', 9, 20)
