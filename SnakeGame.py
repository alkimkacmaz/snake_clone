from random import choice

class Square:
    def __init__(self, x: int, y: int, value: str = "empty") -> None:
        self.x = x
        self.y = y
        self.value = value

    def __add__(self, another: 'Square'):
        return Square(x= self.x + another.x, y= self.y + another.y)
    
    def coord(self):
        return (self.x, self.y)

class Map:
    def __init__(self, size: tuple) -> None:
        self.size = size # (x, y)
        self.squares = {(x, y): Square(x, y) for y in range(self.size[1]) for x in range(self.size[0])}

    def values(self) -> list:
        result = []
        for y in range(self.size[1]):
            newlist = []
            for x in range(self.size[0]):
                newlist.append(self.squares[(x, y)].value)
            result.append(newlist)
        return result
    
    def update_square_at(self, coord: tuple, value: str):
        self.squares[coord] = value

    def empty_squares(self) -> list:
        return [sq for sq in self.squares.values() if sq.value == "empty"]

    @classmethod
    def add_coord(cls, c1: tuple, c2: tuple):
        return(c1[0] + c2[0], c1[1] + c2[1])
    
    @classmethod
    def subtract_coord(cls, c1: tuple, c2: tuple):
        return(c1[0] - c2[0], c1[1] - c2[1])
        
class Snake:
    def __init__(self, squares: list) -> None:
        self.squares = squares
        self.fed = 0

    def head(self) -> Square:
        return self.squares[0]

    def neck(self) -> Square:
        return self.squares[1]
    
    def tailtip(self) -> Square:
        return self.squares[-1]


    def length(self) -> int:
        return len(self.squares)
    
    def update_square_values(self):
        for sq in self.squares:
            sq.value = "snakebody"
        self.tailtip().value = "snaketailtip" # tailtip is written before the neck, so that a snake with len 2 can't go back
        self.neck().value = "snakeneck"
        self.head().value = "snakehead" # Written last so that a snake w len 1 can fx

    def move(self, newhead: Square, isfed: bool=False):
        self.squares.insert(0, newhead)
        self.update_square_values()
        if isfed:
            self.fed += 1
            return # no need to remove the tail
                   # Since "snakehead" is the new value, no need to manually change the value from "food"
        
        self.squares[-1].value = "empty"
        self.squares.pop()      

class GameLogic:
    def __init__(self, map_dimensions: tuple=(20, 20), snake_length: int=3) -> None:
        # TODO: Implement variable snake length
        # TODO: Implement custom map input
        # TODO: Implement obstacle border if asked for
        # TODO: Implement random snake spawn location

        self.map = Map(map_dimensions)
        self.initialise_snake()
        self.create_food()
        self.status = "normal"        

    def interface_input(self, command):
        """
        Gets input from interface, executes it.
        If no command is given, ticks the game by one move
        """
        self.main_game_tick(command)

    def interface_output(self) -> dict:
        """
        Gives feedback to the interface. 
        """

        return {
            "type": self.status, # Not game_over report, not error/warning report
            "map": self.give_map_values(),
            "food eaten": self.snake.fed,
            "snake length": self.snake.length()

        }
    
    def interface(self, command: str = "straight") -> dict:
        self.interface_input(command)
        return self.interface_output()
    

    def give_map_values(self) -> list:
        return self.map.values()

    def initialise_snake(self):
        self.snake = Snake([self.map.squares[(2, 0)], self.map.squares[(1, 0)], self.map.squares[(0, 0)]]) # TODO: this is really clunky, fix this
        self.snake.update_square_values()

    def initialise_obstacles(self):
        # TODO: implement a proper obstacle initialiser, this is a placeholder
        self.obstacles = {(7, 0): self.map.squares[(7, 0)]}
        for v in self.obstacles.values():
            v.value = "obstacle"

    def create_food(self):
        choice(self.map.empty_squares()).value = "food" 

    def main_game_tick(self, command: str="straight"):        
        if command in ["up", "down", "left", "right", "straight"]:
            self.move_snake(command)

    def value_at_coord(self, coord: tuple):
        return self.map.squares[coord].value   

    def move_snake(self, direction: str):
        actions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
            "straight": Map.subtract_coord(self.snake.head().coord(), self.snake.neck().coord()) # head-neck gives current direction
        }
        newhead_coord = Map.add_coord(self.snake.head().coord(), actions[direction]) 
        newhead_coord = (newhead_coord[0] % self.map.size[0], newhead_coord[1] % self.map.size[1]) # Modulo, so that snake can continue when it reaches the boundary
        
        isfed = False

        if self.value_at_coord(newhead_coord) in ["obstacle", "snakebody"] :
            # if the square is tailtip, it doesn't cause death
            self.status = "game over"
            return

        if self.value_at_coord(newhead_coord) == "snakeneck":
            self.move_snake("straight")
            return # Means tried to move back, illegal move, just go on as normal

        if self.value_at_coord(newhead_coord) == "food":
            isfed = True
            self.create_food()

        self.snake.move(self.map.squares[newhead_coord], isfed)


