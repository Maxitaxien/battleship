from abc import ABC
from time import sleep

# 2
"""
This is an example of what a working battleship game could look like.
The following implementation is meant for inspiration and not necessary for the
completion of the battleship class on INFO135 lab 12.
Note that the level of complexity on completing a finished game is above
what is expected on assignments, lab tasks and the exam - the main point to
pay attention to here is the use OO to divide different functionality of the game into different classes.

Also, feel free to try the game! :)
"""
class BattleshipGame:
    def __init__(self, player1, player2):
        '''
        Creates a game which we can run
        :param player1: the player who begins
        :param player2: the second player
        '''
        # each player has their own grid
        self.grid1 = Grid()
        self.grid2 = Grid()
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1

        self.gridsize = self.grid1.gridsize

    def place_all_ships(self):
        '''
        Places all ships for both players
        '''
        for p in [self.player1, self.player2]:
            # For a faster game, remove some of the ships
            # c = Carrier(p)
            # b = Battleship(p)
            # s = Submarine(p)
            d = Destroyer(p)
            ships = [d]

            # place all ships
            for s in ships:
                print(f"Currently placing {s} for player {p}.")
                # place on the grid
                g = self.grid1 if p == self.player1 else self.grid2
                g.place_ship(s.size, s.symbol)
            print("\n" * 20)  # print some empty lines so that players do not see previous player's placements
        print(f"{self.player1}: You have five seconds to get ready!")
        sleep(5)


    def shoot(self, row, col, grid):
        '''
        Shoots and updates grid accordingly
        :param row: row to target
        :param col: col to target
        :param grid: grid to update
        '''
        print(f"Taking a shot at ({Grid.idx_letter[row]}, {col + 1})...")
        grid.resolve_shot(row, col)



    def play(self):
        '''
        Creates and places ships for each player,
        then runs main game loop
        '''
        self.place_all_ships()

        print(f"Starting game: {self.player1} vs. {self.player2}")
        turn = 1

        while True:
            print(f"Turn {int(turn // 1)}, it's {self.current_player}'s turn! ")
            print("Your current board:")
            my_board = self.grid1 if self.current_player == self.player1 else self.grid2
            my_board.display_grid()

            opposing_grid = self.grid1 if self.current_player == self.player2 else self.grid2

            view_hits = input("Would you like to display the status of hits on your opponent? (Y/N):")
            if view_hits == "Y":
                opposing_grid.display_hits()

            r = input("Enter row (A-J) to strike:").upper()
            r = Grid.letter_idx.get(r, -1)
            while 0 > r > self.gridsize - 1:
                print("Invalid row entry, please try again.")
                r = input("Enter row [A-J] to strike:").upper()

            c = input("Enter col (1-10) to strike:")
            c = int(c) - 1
            while 0 > c > self.gridsize - 1:
                print("Invalid column entry, please try again.")
                c = input("Enter col [1-10] to strike:")

            print("\n" * 10)  # print empty lines to reset view for next player
            self.shoot(r, c, opposing_grid)

            # check if game is terminated - that is, if all ship amounts are empty
            if sum(opposing_grid.ship_amounts.values()) == 0:
                print(f"Game over on turn {int(turn // 1)}!")
                print(f"Player {self.current_player} wins!")
                break

            if self.current_player == self.player1:
                self.current_player = self.player2
            else:
                self.current_player = self.player1

            turn += 0.5
            print("You have five seconds to switch players.")
            sleep(5) # give a bit of time to switch players
class Grid:
    '''
    Grid explanation:
    o: empty/unexplored tile
    -: opponent shot and missed
    +: opponent shot and hit
    x: part of a sunken ship
    '''
    # map indices to letters
    idx_letter = {0:"A", 1:"B", 2:"C", 3:"D", 4:"E",
                  5:"F",6: "G", 7:"H", 8:"I", 9:"J"}

    # map letters to indices
    letter_idx = {"A":0, "B":1, "C":2, "D":3, "E":4,
                  "F":5,"G":6, "H":7, "I":8, "J":9}

    def __init__(self):
        self.gridsize = 10  # hardcoded - could also be variable
        self.g = [["o" for _ in range(self.gridsize)] for _ in range(self.gridsize)]
        # to track if the whole ship is gone
        self.ship_amounts = {}

    def verify_placement(self, row, col, orientation, ship_size):
        '''
        Check if the ship is within bounds and does not crash with another ship
        :param row: starting row of left corner of ship
        :param col: starting col of left corner of ship
        :param orientation: whether the ship is vertical or horizontal
        :param ship_size: the size of the ship
        :return: boolean indicating if the ship placement is valid
        '''
        # check if ship extends outside or collides with other ship
        if orientation == "H":
            for c in range(ship_size):
                if c + col > self.gridsize - 1: # out of bounds check
                    return False
                if self.g[row][c + col] != 'o': # collision check
                    return False
        elif orientation == "V":
            for r in range(ship_size):
                if row - r < 0:
                    return False
                if self.g[row - r][col] != 'o':
                    return False

        # all checks passed :)
        return True

    def display_grid(self):
        '''
        Display the grid from the current players point of view
        '''
        letters = list(self.letter_idx.keys())
        print("  ", end="")
        for num in range(1, 11):
            print(num, end=" ")
        print()
        for i in range(len(self.g)):
            print(letters[i].lower(), end= " ")
            print(" ".join(self.g[i]))

    def display_hits(self):
        '''
        Displays the grid showing only opponents shots and misses
        (To not give away position of ships)
        '''
        letters = list(self.letter_idx.keys())
        letter_counter = 0

        print("  ", end="")
        for num in range(1, 11):
            print(num, end=" ")
        print()
        for row in self.g:
            print(letters[letter_counter].lower(), end=" ")
            for entry in row:
                if entry in 'ox+-':
                    print(entry, end=" ")
                else:
                    print('o', end=" ")
            letter_counter += 1
            print()

    def update_grid(self, row, col, symbol):
        self.g[row][col] = symbol

    def resolve_shot(self, row, col):
        entry = self.g[row][col]
        if entry in 'CBSD':
            print("It's a hit!")
            self.g[row][col] = "+"
            self.ship_amounts[entry] -= 1
            if self.ship_amounts[entry] == 0:
                self.sink_ship(entry)
        else:
            print("It's a miss.")
            self.g[row][col] = '-'

    def sink_ship(self, ship_symbol):
        '''
        Searches through grid and sets all entries of ship symbol to 'x' to mark as
        sunk

        Perhaps a little inefficient, but doesn't matter much with grid size = 10
        :param ship_symbol: the ship that is sunk
        '''
        print("A ship has been sunk!")
        for r in range(self.gridsize):
            for c in range(self.gridsize):
                if self.g[r][c] == ship_symbol:
                    self.g[r][c] = 'x'

    def place_ship(self, ship_size, ship_symbol):
        '''
        Takes ship place as input, validates and places ship.
        :param ship_size: length of ship
        :param ship_symbol: symbol that shows which ship a spot belongs to
        '''
        orient = input("Enter orientation of ship, H or V (horizontal or vertical):").upper()
        while orient not in ["H", "V"]:
            orient = input("Invalid orientation, please input H or V (horizontal or vertical):").upper()

        print("The ship will be placed starting from a (row, col) position as the lower left corner.")
        print("The ship will extend", "upwards" if orient == "V" else "to the right", ship_size, "squares.")

        # try asking for row and col until a valid ship placement is given
        placing = True
        while placing:
            row = input("Enter row from [A-J]:").upper()
            while row not in list(self.letter_idx.keys()):
                row = input("Invalid row, please input a letter from A - J:")

            col = input("Enter column from [1-10]:")
            while col not in [str(i) for i in range(1, 11)]:
                col = input("Invalid col, please input a number from 1 - 11")

            # creating numerical version of row for easier computation
            row = self.letter_idx[row]

            # grid indexing is zero-based
            col = int(col) - 1

            if self.verify_placement(row, col, orient, ship_size):
                print("Ship successfully placed.")
                placing = False # exits the loop if placed successfully

                # update the grid
                if orient == "H":
                    for c in range(ship_size):
                        self.update_grid(row, c + col, ship_symbol)
                else:
                    for r in range(ship_size):
                        self.update_grid(row - r, col, ship_symbol)
                # add an entry to track if the ship is gone
                self.ship_amounts[ship_symbol] = ship_size

                # show grid
                self.display_grid()
            else:
                self.display_grid()
                print("Error: Invalid placement. Please try again.")
                print()




class Ship(ABC):
    def __init__(self, size, belongs_to, symbol):
        self.size = size
        self.belongs_to = belongs_to
        self.symbol = symbol


class Carrier(Ship):
    def __init__(self, belongs_to):
        super().__init__(5, belongs_to, "C")

    def __str__(self):
        return "Carrier"

class Battleship(Ship):
    def __init__(self, belongs_to):
        super().__init__(4, belongs_to, "B")

    def __str__(self):
        return "Battleship"

class Submarine(Ship):
    def __init__(self, belongs_to):
        super().__init__(3, belongs_to, "S")

    def __str__(self):
        return "Submarine"
class Destroyer(Ship):
    def __init__(self, belongs_to):
        super().__init__(2, belongs_to, "D")

    def __str__(self):
        return "Destroyer"

def main():
    g = BattleshipGame("p1", "p2")
    g.play()


if __name__ == '__main__':
    main()