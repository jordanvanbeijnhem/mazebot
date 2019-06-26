import json
import math
import requests

login = {'login': 'jordanvanbeijnhem'}
base_url = 'https://api.noopschallenge.com'


def calculate_distance_between_positions(position_a, position_b):
    a = (position_b[0] - position_a[0]) ** 2
    b = (position_b[1] - position_a[1]) ** 2
    return math.sqrt(a + b)


def get_closest_position_to_ending(possible_positions, ending_position):
    closest_index = 0
    closest_distance = 0
    i = 0
    for position in possible_positions:
        distance = calculate_distance_between_positions(
            position, ending_position)
        if i == 0 or distance < closest_distance:
            closest_distance = distance
            closest_index = i
        i += 1
    return possible_positions[closest_index]


def validate_position(current_position, last_position, already_traversed_positions, maze_map):
    return (current_position != last_position and not
            current_position in already_traversed_positions and
            current_position[0] >= 0 and
            current_position[1] >= 0 and
            current_position[0] < len(maze_map[0]) and
            current_position[1] < len(maze_map) and not
            maze_map[current_position[1]][current_position[0]] == 'X')


def get_possible_positions(current_position, last_position, already_traversed_positions, maze_map):
    possible_positions = []

    north_position = [current_position[0], current_position[1] - 1]
    east_position = [current_position[0] + 1, current_position[1]]
    south_position = [current_position[0], current_position[1] + 1]
    west_position = [current_position[0] - 1, current_position[1]]

    if validate_position(north_position, last_position, already_traversed_positions, maze_map):
        possible_positions.append(north_position)
    if validate_position(east_position, last_position, already_traversed_positions, maze_map):
        possible_positions.append(east_position)
    if validate_position(south_position, last_position, already_traversed_positions, maze_map):
        possible_positions.append(south_position)
    if validate_position(west_position, last_position, already_traversed_positions, maze_map):
        possible_positions.append(west_position)

    if len(possible_positions) == 0:
        possible_positions.append(last_position)

    return possible_positions


def print_maze(maze):
    for row in maze:
        for value in row:
            print(value, end='')
        print()


def post_json(path, data):
    r = requests.post(base_url + path, data)
    return r.json()


def get_json(path):
    r = requests.get(base_url + path)
    return r.json()


def convert_path_to_solution(path):
    solution = ''
    for i in range(1, len(path)):
        current_position = path[i]
        previous_position = path[i - 1]

        north_position = [current_position[0], current_position[1] - 1]
        east_position = [current_position[0] + 1, current_position[1]]
        south_position = [current_position[0], current_position[1] + 1]
        west_position = [current_position[0] - 1, current_position[1]]

        if north_position == previous_position:
            solution += 'S'
        elif east_position == previous_position:
            solution += 'W'
        elif south_position == previous_position:
            solution += 'N'
        elif west_position == previous_position:
            solution += 'E'

    return solution


def solve_maze(maze):
    path = []
    already_traversed_positions = []
    starting_position = maze['startingPosition']
    ending_position = maze['endingPosition']
    current_position = starting_position

    while True:
        path.append(current_position)
        already_traversed_positions.append(current_position)

        if maze['map'][current_position[1]][current_position[0]] == 'B':
            break
        else:
            next_position = []
            possible_positions = get_possible_positions(
                current_position, path[len(path) - 2], already_traversed_positions, maze['map'])

            if len(possible_positions) > 1:
                next_position = get_closest_position_to_ending(
                    possible_positions, ending_position)
            else:
                next_position = possible_positions[0]

            if len(path) > 1 and path[len(path) - 2] == next_position:
                path = path[:len(path)-2]
                current_position = next_position
            else:
                current_position = next_position
    return convert_path_to_solution(path)


if __name__ == '__main__':
    maze_path = post_json('/mazebot/race/start',
                          json.dumps(login))['nextMaze']
    while True:
        next_maze = get_json(maze_path)
        print(next_maze['name'])
        print_maze(next_maze['map'])

        solution = solve_maze(next_maze)
        print('solution: ' + solution)
        solution_result = post_json(
            maze_path, json.dumps({'directions': solution}))
        if solution_result['result'] == 'success':
            print('solution correct :)')
            print('solution calculated in: ' + str(solution_result['elapsed']) + 's')
            maze_path = solution_result['nextMaze']
            next_maze = get_json(maze_path)
        elif solution_result['result'] == 'finished':
            print(solution_result['message'])
            print(base_url + solution_result['certificate'])
            break
        else:
            print('solution incorrect :(')
            break
        print()
