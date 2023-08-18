import SnakeGame
from time import sleep

import curses

def frame(fx):
    """Clear the screen, execute fx, refresh screen -> create a frame"""
    def inner(self):
        self.screen.clear()
        fx(self)
        self. screen.refresh()
    return inner

class Window:
    def __init__(self) -> None:
        self.set_keybindings()
        self.screen = curses.initscr()
        self.screen_config()
        self.dim = self.get_screen_dimensions()
        self.colors()

    def set_keybindings(self):
        self.keys = {

        }

    def get_screen_dimensions(self) -> tuple:
        y, x =  self.screen.getmaxyx()
        return (x, y)
    
    def colors(self) -> tuple:
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)


    def screen_config(self):
        self.screen.keypad(1) # Allows arrow keys
        self.screen.nodelay(1) # No delay when asking for input
        curses.curs_set(0) # No cursor
        curses.start_color()

    def get_user_input(self):
        input = self.screen.getch()
        if input in self.keys:
            self.command = self.keys[input]          

    def restore_terminal_default_config(self):
        curses.nocbreak()   # Turn off cbreak mode
        curses.echo()       # Turn echo back on
        curses.curs_set(1)  # Turn cursor back on
        self.screen.keypad(0) # Turn off keypad keys


class GameWindow(Window):
    def __init__(self) -> None:
        super().__init__()
        # self.new_game()
        common_snake_body_symbol = "0"
        self.symbols = {
            "empty": ".",
            "snakebody": common_snake_body_symbol,
            "snakeneck": common_snake_body_symbol,
            "snaketailtip": common_snake_body_symbol,
            "snakehead": "a",
            "food": "*",  
            "obstacle": "#",          
        }
        self.score = 0

    def new_game(self, map_dimensions: tuple=(21, 21)):
        self.map_matrix_dimensions = map_dimensions
        self.map_real_dimensions = (map_dimensions[0]*2 - 1, map_dimensions[1])        
        self.game = SnakeGame.GameLogic(map_dimensions)

    def set_keybindings(self):
        self.keys = {
            curses.KEY_UP: "up", 
            curses.KEY_DOWN: "down",
            curses.KEY_LEFT: "left",
            curses.KEY_RIGHT: "right",
        }

    def print_map(self):
        """Old method, prints the map without curses"""
        [print(" ".join(row)) for row in self.symbolmap]     

    def analyse_state(self, state: dict):
        self.raw_state= state
        self.currentmap = state["map"]
        self.symbolmap = [[self.symbols[i] for i in row] for row in self.currentmap]
        self.game_status = state["type"]
        self.score = state["food eaten"]

    def game_loop(self):
        while True:
            self.command = "straight"
            
            self.get_user_input()

            state = self.game.interface(self.command)
            self.analyse_state(state)

            self.draw_map()
            if self.game_status == "game over":
                break
            curses.napms(100)            
        
        self.draw_game_over() # TODO: replace with a proper game over screen
        curses.napms(2000)

    def map_left_top_corner(self) -> tuple:
        centerx = self.get_screen_dimensions()[0] // 2
        centery = self.get_screen_dimensions()[1] // 2
        mapx = self.map_real_dimensions[0] // 2
        mapy = self.map_real_dimensions[1] // 2
        return (centerx - mapx, centery - mapy)
    
    def map_borders(self) -> tuple:
        """returns (x1, x2, y1, y2)"""
        x1, y1 = self.map_left_top_corner()
        return (x1, x1 + self.map_real_dimensions[0], y1, y1 + self.map_real_dimensions[1]) 
    

    @frame
    def draw_map(self):
        # self.screen.box() # to test the borders of the screen
        addx, addy = self.map_left_top_corner() # To center the map
        for y, row in enumerate(self.symbolmap):
            for x, char in enumerate(row):
                if char in [self.symbols[i] for i in ["snakehead", "snakebody", "snakeneck", "snaketailtip"]]:
                    self.screen.addch(addy + y,addx + x*2, char) #, curses.color_pair(1))
                elif char in [self.symbols[i] for i in ["food"]]:
                    self.screen.addch(addy + y,addx + x*2, char, curses.color_pair(2))
                else:
                    self.screen.addch(addy + y,addx + x*2, char, curses.A_DIM) # x*2 so that x axis isn't crowded
                latest_x = addx + x*2

        scoretext = f"score: {self.score}"
        self.screen.addstr(self.map_borders()[2]-1, addx, f"{scoretext:>{self.map_real_dimensions[0]}}")

    @frame
    def draw_game_over(self):
        self.screen.addstr(3, 10, "Game Over")
        self.screen.addstr(4, 10, f"Score: {self.score}")
        
class Menu(Window):
    def __init__(self) -> None:
        super().__init__(),

    def set_item_action_bindings(self):
        self.menu_items = {

        }
    
    def set_keybindings(self):
        self.keys = {
            curses.KEY_UP: "up", 
            curses.KEY_DOWN: "down",
            curses.KEY_ENTER: "select"
        }

if __name__ == "__main__":
    app = GameWindow()
    app.new_game()
    app.game_loop()