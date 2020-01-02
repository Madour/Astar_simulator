# ,----------------------,
# | Author: Modar NASSER |
# | date : january 2020  |
# `----------------------'
from Astar import *
from sfml import sf
import sys, os

# utility function to find assets
def pyInstallerPath(relative_path):
    try: # for release : pyInstaller stores assets in a temporary folder _MEIPASS
        absolute_path = sys._MEIPASS
    except: # for developement
        absolute_path = ""
    return os.path.join(absolute_path, relative_path)


class Simulation:
    MOUSE_LEFT = 0
    MOUSE_RIGHT = 1
    START_POS_STATE = 0
    TARGET_POS_STATE = 1
    WALLS_POS_STATE = 2
    GRID_POS = sf.Vector2(50, 50)
    GRID_STEPS = [5, 10, 20, 50]
    FONT = sf.Font.from_file(pyInstallerPath("assets/font.ttf"))

    def __init__(self, grid_step):
        self.grid_step = grid_step
        self.directions = 4
        # creating a grid
        self.create_grid(self.grid_step)
        self.create_grid_elements()
        self.walls_list = []
        self.deleted_walls = False

        # path line
        self.path = sf.VertexArray(sf.PrimitiveType.LINES_STRIP, 0)
        # path outline, just to make the line look thicker
        self.path_outline1 = sf.VertexArray(sf.PrimitiveType.LINES_STRIP, 0)
        self.path_outline2 = sf.VertexArray(sf.PrimitiveType.LINES_STRIP, 0)

        # GUI
        self.search_button = self.new_button(
            'Search',
            (self.GRID_POS.x + self.grid_box.size.x + 75, self.GRID_POS.y + 25),
            sf.Color(50, 200, 50)
        )
        self.reset_button = self.new_button(
            'Reset',
            (self.GRID_POS.x + self.grid_box.size.x + 75, self.GRID_POS.y + 125),
            sf.Color(200, 50, 50)
        )
        self.dezoom_button = self.new_button(
            '  -',
            (self.GRID_POS.x + self.grid_box.size.x + 72, self.GRID_POS.y + 225),
            sf.Color(160, 160, 160), size="small"
        )
        self.zoom_button = self.new_button(
            '  +',
            (self.GRID_POS.x + self.grid_box.size.x + 72 + 105, self.GRID_POS.y + 225),
            sf.Color(160, 160, 160), size="small"
        )

        self.directions_text = sf.Text('Directions :')
        self.directions_text.font = self.FONT
        self.directions_text.color = sf.Color.BLACK
        self.directions_text.character_size = 25
        self.directions_text.origin = (0, -self.directions_text.character_size/2)
        self.directions_text.position = (self.GRID_POS.x + self.grid_box.size.x + 72, self.GRID_POS.y + 375)

        self.direction4_button = self.new_button(
            '  4',
            (self.GRID_POS.x + self.grid_box.size.x + 72, self.GRID_POS.y + 425),
            sf.Color(160, 160, 160), size="small"
        )
        self.direction8_button = self.new_button(
            '  8',
            (self.GRID_POS.x + self.grid_box.size.x + 72 + 105, self.GRID_POS.y + 425),
            sf.Color(160, 160, 160), size="small"
        )

        self.fps_text = sf.Text('fps:')
        self.fps_text.font = self.FONT
        self.fps_text.color = sf.Color.BLACK
        self.fps_text.character_size = 20
        self.fps_text.origin = (0, -self.fps_text.character_size / 2)
        self.fps_text.position = (0, 0)
        self.fps_history = []               # used to compute average FPS

        self.message = sf.Text('')
        self.message.font = self.FONT
        self.message.color = sf.Color.BLACK
        self.message.character_size = 25
        self.message.origin = (0, -self.message.character_size / 2)
        self.message.position = (350, 10)

        self.author = sf.Text('Modar NASSER (c) 2020')
        self.author.font = self.FONT
        self.author.color = sf.Color.BLACK
        self.author.character_size = 20
        self.author.origin = (self.author.global_bounds.width, self.author.character_size/2)

        self.fps_clock = sf.Clock()         # used to get real fps
        self.astar_clock = sf.Clock()       # used to get how much time the agorithm takes

        self.current_state = self.START_POS_STATE

        self.window = sf.RenderWindow(sf.VideoMode(1422, 800), "A* algorithm simulator")
        self.window.framerate_limit = 100
        self.icon = sf.Image.from_file(pyInstallerPath('assets/icon64.png'))
        self.window.set_icon(64, 64, sf.Image.from_file(pyInstallerPath('assets/icon64.png')).pixels.tobytes())

        self.author.position = (self.window.size.x-5, self.window.size.y-5)

    def run(self):
        while self.window.is_open:
            mouse_pos = sf.Mouse.get_position(self.window)

            for event in self.window.events:
                if event == sf.Event.CLOSED:
                    self.window.close()

                if event == sf.Event.KEY_RELEASED:
                    if event['code'] == sf.Keyboard.ESCAPE:
                        self.window.close()

                    if event['code'] == sf.Keyboard.RETURN:
                        self.find_path()

                    if event['code'] == sf.Keyboard.ADD:
                        self.zoom_grid()

                    if event['code'] == sf.Keyboard.SUBTRACT:
                        self.dezoom_grid()

                if event == sf.Event.MOUSE_BUTTON_RELEASED:
                    mouse_grid_pos = self.get_mouse_grid_pos()
                    if event['button'] == self.MOUSE_LEFT:
                        if mouse_grid_pos is not None:
                            # place start_point
                            if self.current_state == self.START_POS_STATE:
                                if mouse_grid_pos not in [x.position for x in self.walls_list]:
                                    self.start_point.position = mouse_grid_pos
                                    self.current_state += 1
                            # place target_point
                            elif self.current_state == self.TARGET_POS_STATE:
                                if mouse_grid_pos != self.start_point.position:
                                    if mouse_grid_pos not in [x.position for x in self.walls_list]:
                                        self.target_point.position = mouse_grid_pos
                                        self.current_state += 1
                        else:
                            if self.reset_button['shape'].global_bounds.contains(mouse_pos):
                                self.reset()
                            elif self.search_button['shape'].global_bounds.contains(mouse_pos):
                                self.find_path()
                            elif self.zoom_button['shape'].global_bounds.contains(mouse_pos):
                                self.zoom_grid()
                            elif self.dezoom_button['shape'].global_bounds.contains(mouse_pos):
                                self.dezoom_grid()
                            elif self.direction4_button['shape'].global_bounds.contains(mouse_pos):
                                self.directions = 4
                            elif self.direction8_button['shape'].global_bounds.contains(mouse_pos):
                                self.directions = 8

                    if event['button'] == self.MOUSE_RIGHT:
                        if self.current_state == self.TARGET_POS_STATE:
                            self.target_point.position = (-self.grid_step, -self.grid_step)
                            self.current_state -= 1
                        elif self.current_state == self.WALLS_POS_STATE:
                            if not self.deleted_walls:
                                self.wall_shape.position = (-self.grid_step, -self.grid_step)
                                self.current_state -= 1

            if self.grid_box.global_bounds.contains(mouse_pos):
                if self.current_state == self.START_POS_STATE:
                    self.start_point.position = mouse_pos
                elif self.current_state == self.TARGET_POS_STATE:
                    self.target_point.position = mouse_pos
                elif self.current_state == self.WALLS_POS_STATE:
                    self.wall_shape.position = mouse_pos

            # building walls
            if sf.Mouse.is_button_pressed(self.MOUSE_LEFT):
                mouse_grid_pos = self.get_mouse_grid_pos()
                if mouse_grid_pos is not None:
                    if self.current_state == self.WALLS_POS_STATE:
                        if mouse_grid_pos != self.start_point.position and mouse_grid_pos != self.target_point.position:
                            if mouse_grid_pos not in [x.position for x in self.walls_list]:
                                self.wall_shape.position = mouse_grid_pos
                                self.walls_list.append(self.wall_shape)
                                self.wall_shape = self.new_wall()
                                mouse_grid_pos -= self.GRID_POS
                                mouse_grid_pos = sf.Vector2(mouse_grid_pos.x // self.grid_step, mouse_grid_pos.y // self.grid_step)
                                self.grid[int(mouse_grid_pos.y)][int(mouse_grid_pos.x)] = 1
            # destroying walls
            if sf.Mouse.is_button_pressed(self.MOUSE_RIGHT):
                mouse_grid_pos = self.get_mouse_grid_pos()
                if mouse_grid_pos is not None:
                    if self.current_state == self.WALLS_POS_STATE:
                        if mouse_grid_pos in [x.position for x in self.walls_list]:
                            index = [x.position for x in self.walls_list].index(mouse_grid_pos)
                            self.walls_list.pop(index)
                            mouse_grid_pos -= self.GRID_POS
                            mouse_grid_pos = sf.Vector2(mouse_grid_pos.x // self.grid_step, mouse_grid_pos.y // self.grid_step)
                            self.grid[int(mouse_grid_pos.y)][int(mouse_grid_pos.x)] = 0
                            self.deleted_walls = True
            else:
                if self.deleted_walls:
                    self.deleted_walls = False

            self.window.clear(sf.Color.WHITE)
            # drawing grid :
            self.window.draw(self.grid_box)
            self.window.draw(self.horizontal_lines)
            self.window.draw(self.vertical_lines)

            self.window.draw(self.start_point)
            self.window.draw(self.target_point)
            self.window.draw(self.wall_shape)
            for wall in self.walls_list:
                self.window.draw(wall)

            self.window.draw(self.path)
            self.window.draw(self.path_outline1)
            self.window.draw(self.path_outline2)

            # drawing GUI
            self.window.draw(self.reset_button['shape'])
            self.window.draw(self.reset_button['text'])
            self.window.draw(self.search_button['shape'])
            self.window.draw(self.search_button['text'])
            self.window.draw(self.zoom_button['shape'])
            self.window.draw(self.zoom_button['text'])
            self.window.draw(self.dezoom_button['shape'])
            self.window.draw(self.dezoom_button['text'])
            self.window.draw(self.directions_text)
            self.window.draw(self.direction4_button['shape'])
            self.window.draw(self.direction4_button['text'])
            self.window.draw(self.direction8_button['shape'])
            self.window.draw(self.direction8_button['text'])

            self.window.draw(self.message)
            self.window.draw(self.author)

            self.fps_text.string = "fps:" + str(self.get_fps())
            self.window.draw(self.fps_text)
            self.fps_clock.restart()

            self.window.display()

    def reset(self):
        self.walls_list = []
        self.start_point.position = (-self.grid_step, -self.grid_step)
        self.target_point.position = (-self.grid_step, -self.grid_step)
        self.wall_shape.position = (-self.grid_step, -self.grid_step)
        self.current_state = self.START_POS_STATE
        self.path.resize(0)
        self.path_outline1.resize(0)
        self.path_outline2.resize(0)
        self.message.string = ""
        self.grid = []
        for j in range(self.horizontal_lines_nb + 1):
            self.grid.append([])
            for i in range(self.vertical_lines_nb + 1):
                self.grid[j].append(0)

    def find_path(self):
        if self.current_state != self.START_POS_STATE:
            grid_start = self.start_point.position - self.GRID_POS
            grid_start = (int(grid_start.x // self.grid_step), int(grid_start.y // self.grid_step))
            grid_target = self.target_point.position - self.GRID_POS
            grid_target = (int(grid_target.x // self.grid_step), int(grid_target.y // self.grid_step))
            self.astar_clock.restart()
            result = astar(self.grid, grid_start, grid_target, self.directions)
            time = self.astar_clock.elapsed_time.seconds
            if result is not False:
                result = [sf.Vector2(move[0] * self.grid_step, move[1] * self.grid_step) for move in result]
                offset1 = sf.Vector2(1, 0)
                offset2 = sf.Vector2(0, 1)
                self.path.resize(len(result) + 1)
                self.path_outline1.resize(len(result) + 1)
                self.path_outline2.resize(len(result) + 1)
                self.path[0].position = self.start_point.position
                self.path[0].color = sf.Color.BLUE
                self.path_outline1[0].position = self.start_point.position+offset1
                self.path_outline1[0].color = sf.Color.BLUE
                self.path_outline2[0].position = self.start_point.position+offset2
                self.path_outline2[0].color = sf.Color.BLUE
                for i in range(len(result)):
                    self.path[i + 1].position = sf.Vector2(self.path[i].position.x + result[i].x, self.path[i].position.y + result[i].y)
                    self.path[i + 1].color = sf.Color.BLUE
                    self.path_outline1[i + 1].position = sf.Vector2(self.path[i].position.x + result[i].x, self.path[i].position.y + result[i].y) + offset1
                    self.path_outline1[i + 1].color = sf.Color.BLUE
                    self.path_outline2[i + 1].position = sf.Vector2(self.path[i].position.x + result[i].x, self.path[i].position.y + result[i].y) + offset2
                    self.path_outline2[i + 1].color = sf.Color.BLUE
                self.message.string = "Found a path in " + str(round(time * 1000, 3)) + " milliseconds"
            else:
                self.path.resize(0)
                self.path_outline1.resize(0)
                self.path_outline2.resize(0)
                self.message.string = "Can't find a path"
        else:
            self.path.resize(0)
            self.path_outline1.resize(0)
            self.path_outline2.resize(0)
            self.message.string = "Place starting point first"

    def zoom_grid(self):
        if self.grid_step != self.GRID_STEPS[-1]:
            self.reset()
            self.create_grid(self.GRID_STEPS[self.GRID_STEPS.index(self.grid_step) + 1])
            self.create_grid_elements()

    def dezoom_grid(self):
        if self.grid_step != self.GRID_STEPS[0]:
            self.reset()
            self.create_grid(self.GRID_STEPS[self.GRID_STEPS.index(self.grid_step) - 1])
            self.create_grid_elements()

    def create_grid(self, step):
        self.grid_step = step
        self.grid_box = sf.RectangleShape((1000, 700))
        self.grid_box.position = self.GRID_POS
        self.grid_box.outline_color = sf.Color(150, 150, 150)
        self.grid_box.outline_thickness = 2

        self.horizontal_lines_nb = int(self.grid_box.size.y // step)
        self.horizontal_lines = sf.VertexArray(sf.PrimitiveType.LINES, 2 * self.horizontal_lines_nb)
        for y, i in zip(range(self.horizontal_lines_nb), range(0, 2 * self.horizontal_lines_nb, 2)):
            self.horizontal_lines[i].position = self.GRID_POS + (0, step * y)
            self.horizontal_lines[i + 1].position = self.GRID_POS + (self.grid_box.size.x, step * y)
            self.horizontal_lines[i].color = sf.Color(180, 180, 180)
            self.horizontal_lines[i + 1].color = sf.Color(180, 180, 180)

        self.vertical_lines_nb = int(self.grid_box.size.x // step)
        self.vertical_lines = sf.VertexArray(sf.PrimitiveType.LINES, 2 * self.vertical_lines_nb)
        for x, i in zip(range(self.vertical_lines_nb), range(0, 2 * self.vertical_lines_nb, 2)):
            self.vertical_lines[i].position = self.GRID_POS + (step * x, 0)
            self.vertical_lines[i + 1].position = self.GRID_POS + (step * x, self.grid_box.size.y)
            self.vertical_lines[i].color = sf.Color(180, 180, 180)
            self.vertical_lines[i + 1].color = sf.Color(180, 180, 180)

        self.grid = []
        for j in range(self.horizontal_lines_nb + 1):
            self.grid.append([])
            for i in range(self.vertical_lines_nb + 1):
                self.grid[j].append(0)

    def create_grid_elements(self):
        # creating start and target points
        self.start_point = sf.CircleShape(self.grid_step / 2)
        self.start_point.fill_color = sf.Color.RED
        self.start_point.origin = (self.grid_step / 2, self.grid_step / 2)
        self.start_point.position = (-self.grid_step / 2, -self.grid_step / 2)

        self.target_point = sf.CircleShape(self.grid_step / 2)
        self.target_point.fill_color = sf.Color.GREEN
        self.target_point.origin = (self.grid_step / 2, self.grid_step / 2)
        self.target_point.position = (-self.grid_step / 2, -self.grid_step / 2)

        # building a wall
        self.wall_shape = self.new_wall()

    def new_wall(self):
        new_wall_shape = sf.RectangleShape((self.grid_step, self.grid_step))
        new_wall_shape.fill_color = sf.Color(120, 120, 120)
        new_wall_shape.origin = (self.grid_step / 2, self.grid_step / 2)
        new_wall_shape.position = (-self.grid_step / 2, -self.grid_step / 2)
        return new_wall_shape

    def new_button(self, name, position, color, size="standard"):
        btn_shape = sf.RectangleShape()
        if size == "standard":
            btn_shape.size = (200, 75)
        elif size == "small":
            btn_shape.size = (100, 75)
        btn_shape.position = position
        btn_shape.fill_color = color
        btn_text = sf.Text(name)
        btn_text.font = self.FONT
        btn_text.color = sf.Color.BLACK
        btn_text.position = btn_shape.position + sf.Vector2(25, 75 / 2)
        return {'shape': btn_shape, 'text': btn_text}

    def get_mouse_grid_pos(self):
        """
        Rounds mouse position to the closest node of the grid
        """
        mg_pos = sf.Mouse.get_position(self.window)
        mg_pos -= self.GRID_POS
        temp = sf.Vector2(round(mg_pos.x / self.grid_step), round(mg_pos.y / self.grid_step))
        mg_pos = self.GRID_POS + temp * self.grid_step
        if self.grid_box.position.x-self.grid_step/2 < mg_pos.x < self.grid_box.size.x + self.grid_box.position.x+self.grid_step/2:
            if self.grid_box.position.y-self.grid_step/2 < mg_pos.y < self.grid_box.size.y + self.grid_box.position.y+self.grid_step/2:
                return mg_pos
        else:
            return None

    def get_fps(self):
        self.fps_history.insert(0, round(1 / self.fps_clock.elapsed_time.seconds))
        if len(self.fps_history) > 50:
            self.fps_history.pop()
        return round(sum(self.fps_history) / len(self.fps_history))
