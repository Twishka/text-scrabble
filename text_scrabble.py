import random
import sqlite3
from config import WIDTH, HEIGHT, LETTERS

board = []
score = {'Player 1': 0, 'Player 2': 0}
used_words = []
all_letters = []


def new_game():

    print('''
     __________________________________________________
    |                                                  |
    | Hello! This is Scrabble for command line.        |
    | To play, you need to type words and choose start |
    | coordinates and direction for them.              |
    | Use 'right' or 'down' for directions.            |
    | If you want to quit, type '-quit'.               |
    | If you want to exchange letters, type '-switch'. |
    | If you don't know the rules, google them.        |
    | Good luck!                                       |
    |__________________________________________________|
    ''')

    # Making start board

    print('')
    for x in range(HEIGHT):
        row = []
        for y in range(WIDTH):
            row.append('-')
        board.append(row)
    print_board()

    # Generating letter bank

    player_letters = []
    for key in LETTERS.keys():
        l = [key] * LETTERS[key]
        all_letters.extend(l)

    # Giving letters to player

    for i in range(7):
        letter = all_letters.pop(random.randrange(len(all_letters)))
        player_letters.append(letter)

    new_word(first=True, player_letters=player_letters)


def new_word(first, player_letters):
    while True:

        # Getting word from player

        print('Your letters:', player_letters)
        word = input('Word: ').upper()

        # Switching letters

        if word == '-SWITCH':
            del_letters = input('Which ones? Divide with spaces: ').upper()
            delete = del_letters.split(' ')
            for i in delete:
                try:
                    player_letters.remove(i)
                except ValueError:
                    print('Letter {} not in your letters'.format(i))
            for i in range(7 - len(player_letters)):
                letter = all_letters.pop(random.randrange(len(all_letters)))
                player_letters.append(letter)
            # TODO: handle exception when there are no more letters in the box
            continue

        # Quitting game

        if word == '-QUIT':
            print('Thank you for playing!')
            quit()

        # Checking that the word is in dictionary

        if search_dictionary(word) == False:
            print('This word is not in the dictionary')
            continue

        # Checking that the word hasn't been used before

        if word in used_words:
            print('This word has already been used')
            continue

        row = int(input('Row: ')) - 1
        column = int(input('Column: ')) - 1
        direction = input('Direction (right/down): ')
        while direction not in ['right', 'down']:
            print('Please choose "right" or "down"')
            direction = input('Direction: ')

        # TODO: handle exception when the word is out of board

        # Checking that first word crosses center square

        if first:
            if not (column == 7 and (row <= 7 <= (row + len(word))) and direction == 'down') and not \
                    (row == 7 and (column <= 7 <= (column + len(word))) and direction == 'right'):
                print('The first word has to cross the middle cell')
                continue

        # Drawing a word

        new_letters = []
        crosses = 0
        for i in range(len(word)):
            if direction == 'down':
                n_row = row + i
                n_column = column
            elif direction == 'right':
                n_row = row
                n_column = column + i
            if board[n_row][n_column] == '-':
                board[n_row][n_column] = word[i]
                new_letters.append((word[i], n_row, n_column))

            # Checking that the crossed letter matches

            elif board[n_row][n_column] != word[i]:
                print("The crossed letter doesn't match")
                for letter in new_letters:
                    board[letter[1]][letter[2]] = '-'
                break
            else:
                crosses += 1

        # Checking that the word crosses another word if not first

        if not first and crosses == 0:
            print('You have to cross an existing word')
            for letter in new_letters:
                board[letter[1]][letter[2]] = '-'
            continue
        if not first:
            get_words(new_letters)


        # Checking that player only used his letters

        if not all(x in player_letters for x in (x[0] for x in new_letters)):
            print('You can only use your letters')
            delete_new_letters(new_letters)
            continue

        for x in new_letters:
            player_letters.remove(x[0])
        first = False
        used_words.append(word)
        print_board()

        # Give player new letters:

        for i in range(7 - len(player_letters)):
            letter = all_letters.pop(random.randrange(len(all_letters)))
            player_letters.append(letter)


# Board template

def print_board():
    print('')
    print('      1   2   3   4   5   6   7   8   9   10  11  12  13  14  15')
    print('    _____________________________________________________________', end='')
    c = 1
    for row in board:
        print('\n   |                                                             |')
        if c < 10:
            print(c, ' |', end=' ')
        else:
            print(c, '|', end=' ')
        c += 1
        for item in row:
            print(' {}'.format(item), end='  ')
        print('|', end='')
    print('\n   |_____________________________________________________________|\n')


# Looking for words formed with old letters

def get_words(new_letters):
    for letter in new_letters:
        cur_row = letter[1]
        cur_column = letter[2]

        # Check for vertical words

        # Move up
        word = []
        while board[cur_row][cur_column] != '-':
            cur_letter = board[cur_row][cur_column]
            word.append(cur_letter)
            cur_row -= 1
        word.reverse()

        # Move down
        cur_row = letter[1]
        while board[cur_row][cur_column] != '-':
            if cur_row != letter[1] or cur_column != letter[2]:
                cur_letter = board[cur_row][cur_column]
                word.append(cur_letter)
            cur_row += 1
        if len(word) > 1:
            word = ''.join(word)
            if not search_dictionary(word):
                print('All connected letters should form words')
                delete_new_letters(new_letters)
            elif word not in used_words:
                    used_words.append(word)


        # Check for horizontal words

        # Move left
        cur_row = letter[1]
        word = []
        while board[cur_row][cur_column] != '-':
            cur_letter = board[cur_row][cur_column]
            word.append(cur_letter)
            cur_column -= 1
        word.reverse()

        # Move right
        cur_column = letter[2]
        while board[cur_row][cur_column] != '-':
            if cur_row != letter[1] or cur_column != letter[2]:
                cur_letter = board[cur_row][cur_column]
                word.append(cur_letter)
            cur_column += 1
        if len(word) > 1:
            word = ''.join(word)

            if not search_dictionary(word):
                print('All connected letters should form words')
                delete_new_letters(new_letters)
            elif word not in used_words:
                used_words.append(word)

        # TODO: check that player can't form used words by crossing other words

def delete_new_letters(new_letters):
    for letter in new_letters:
        board[letter[1]][letter[2]] = '-'


def search_dictionary(word):
    sqlite_file = 'wordlist.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute("select word from words where word = '{}'".format(word))
    if c.fetchone():
        conn.close()
        return True
    else:
        conn.close()
        return False

new_game()