import random
import os
import re

IDENTIFIERS = {
    "BLANK": "  ",
    "PLAYER": "🧑",
    "ITEM": "📦",
    "DESTINATION": "🏠"
}

DIRECTION_ELUM = {
    "W": (-1, 0),
    "A": (0, -1),
    "S": (1, 0),
    "D": (0, 1),
}

class Database:
    def __init__(self, directory):
        self.directory = directory

        if not os.path.isfile(self.directory):
            open(self.directory, "x")

    def write(self, score):
        with open(self.directory, "w") as file:
            file.write(str(score))

    def get(self) -> int:
        with open(self.directory, "r") as file:
            score = file.read()
            if score:
                return int(score)
            return 0

db = Database("high_score.txt")

class Game:
    def __init__(self):
        self.SIZE = 6
        
        self.build()

        self.level = 1

        self.highest_score = db.get()
        
    def output_board(self):
        print("PACKAGES DELIVERED", self.level, "(HS:", self.highest_score, ")")
        rows = []
        for i in self.board:
            row = ""
            row += "|"
            for j in i:
                row += j
            row += "|"
            rows.append(row)
        border = "=" * len(rows[0])
        print(border)
        print("\n".join(rows))
        print(border)
        
    def find(self, obj) -> tuple | None:
        x = -1
        y = -1
        for i in self.board:
            y = -1
            x += 1
            for j in i:
                y += 1
                if j == obj.identifier:
                    return (x, y)
        return None
        
    def set(self, pos, identifier):
        x = pos[0]
        y = pos[1]
        self.board[x][y] = identifier

    def get(self, pos) -> tuple | None:
        x = pos[0]
        y = pos[1]

        try:
            return self.board[x][y]
        except:
            return None

    # Generates a new level
    def regen(self, restart = False):
        if not restart:
            self.level += 1

            # Checking if new high score has been reached
            if self.level > self.highest_score:
                db.write(self.level)
        else:
            self.level = 0

        self.highest_score = db.get()
        self.build()

    def random_point(self) -> tuple:
        while True:
            x = random.randint(1, self.SIZE - 2)
            y = random.randint(1, self.SIZE - 2)

            if self.get((x, y)) == IDENTIFIERS.get("BLANK"):
                return (x, y)
        
    def build(self):
        self.board = []
        for i in range(self.SIZE):
            row = []
            for i in range(self.SIZE):
                row.append(IDENTIFIERS.get("BLANK"))
            self.board.append(row)

        for key, value in IDENTIFIERS.items():
            if key == "BLANK": continue
            pos = self.random_point()
            self.set(pos, value)

game = Game()

# Base class for player & item
class Base():
    def __init__(self, identifier):
        self.identifier = identifier

    def calc_coords(self, pos, direction) -> tuple:
        # Pushes the objects to the otherside of the board if hits edge
        if pos[1] == game.SIZE - 1 and direction == DIRECTION_ELUM.get("D"):
            return (pos[0], 0)
        elif pos[0] == game.SIZE - 1 and direction == DIRECTION_ELUM.get("S"):
            return (0, pos[1])
        
        x = pos[0] + direction[0]
        y = pos[1] + direction[1]
        return (x, y)
        
    # Returns if the move was successful
    def move(self, direction):
        pos = game.find(self)
        
        coords = self.calc_coords(pos, direction)
        if coords != pos:
            x = coords[0]
            y = coords[1]
            game.board[x][y] = self.identifier
            game.board[pos[0]][pos[1]] = IDENTIFIERS.get("BLANK")
            return True
        return False

    def respawn(self):
        pos = game.random_point()
        game.set(pos, self.identifier)

# Class for item
class Item(Base):
    def __init__(self):
        super().__init__(IDENTIFIERS.get("ITEM"))

    def push(self, direction) -> bool:
        pos = game.find(self)
        coords = self.calc_coords(pos, direction)
        obj = game.get(coords)

        if obj == IDENTIFIERS.get("DESTINATION"):
            game.regen()
        else:
            success = self.move(direction)
            return success
        
        return False
        
item = Item()

# Class for player
class Player(Base):
    def __init__(self):
        super().__init__(IDENTIFIERS.get("PLAYER"))
        
    def wasd(self):
        dir = input("Direction ('restart' to start over): ")
        directions = list(filter(len, re.findall("w|a|s|d", dir)))

        if dir.lower() == "restart":
            game.regen(True)
            return

        if dir.lower() == "w":
            self.movement(DIRECTION_ELUM.get("W"))
        elif dir.lower() == "a":
            self.movement(DIRECTION_ELUM.get("A"))
        elif dir.lower() == "s":
            self.movement(DIRECTION_ELUM.get("S"))
        elif dir.lower() == "d":
            self.movement(DIRECTION_ELUM.get("D"))

    def movement(self, direction):
        pos = game.find(self)
        coords = self.calc_coords(pos, direction)
        obj = game.get(coords)

        if obj == IDENTIFIERS.get("DESTINATION"):
            pass
        elif obj == item.identifier:
            condition = item.push(direction)

            if condition:
                self.move(direction)
        else:
            self.move(direction)
        
player = Player()

# Main control app
class App:
    def __init__(self):
        while True:
            self.main()
            
    def main(self):
        game.output_board()
        player.wasd()
        
App()
