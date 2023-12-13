import pygame
import sys
import time
import psutil


# this class represents a button with an image on it
class ImageButton(pygame.sprite.Sprite):
    def __init__(self, image, x, y, action, game):
        # call the parent class constructor
        super().__init__(game.sprites)
        # load the image from a file
        self.image = pygame.image.load(image)
        # get the rect of the image
        self.rect = self.image.get_rect()
        # set the position of the rect
        self.rect.topleft = (x, y)
        # store the action and the game reference
        self.action = action
        self.game = game

    def update(self, events, dt):
        # check if the game state is running
        if self.game.state != 'RUNNING':
            return
        # loop through the events
        for event in events:
            # check if the mouse button was pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                # get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                # check if the mouse position is inside the rect
                if self.rect.collidepoint(mouse_pos):
                    # call the action
                    self.action(self.game)


# this class represents a button with text on it
class TextButton(pygame.sprite.Sprite):
    def __init__(self, text, x, y, width, height, color, font, action, game):
        # call the parent class constructor
        super().__init__(game.sprites)
        # store the text, color, font, action, and game reference
        self.text = text
        self.color = color
        self.font = font
        self.action = action
        self.game = game
        # create a surface for the button
        self.image = pygame.Surface((width, height))
        # get the rect of the surface
        self.rect = self.image.get_rect()
        # set the position of the rect
        self.rect.topleft = (x, y)
        # fill the surface with the color
        self.fill_surf(self.color)

    def fill_surf(self, color):
        # fill the surface with the color
        self.image.fill(pygame.Color(color))
        # render the text on the surface
        text_surf = self.font.render(self.text, True, pygame.Color('white'))
        # get the rect of the text
        text_rect = text_surf.get_rect()
        # center the text on the button
        text_rect.center = self.rect.center
        # blit the text on the button
        self.image.blit(text_surf, text_rect)

    def update(self, events, dt):
        # check if the game state is running
        if self.game.state != 'RUNNING':
            # fill the surface with dark grey
            self.fill_surf('darkgrey')
            return
        # fill the surface with the original color
        self.fill_surf(self.color)
        # loop through the events
        for event in events:
            # check if the mouse button was pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                # get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                # check if the mouse position is inside the rect
                if self.rect.collidepoint(mouse_pos):
                    # call the action
                    self.action(self.game)


# this class represents a walking rect that moves randomly
class WalkingRect(pygame.sprite.Sprite):
    def __init__(self, pos, color, game):
        # call the parent class constructor
        super().__init__(game.sprites, game.actors)
        # create a surface for the rect
        self.image = pygame.Surface((32, 32))
        # fill the surface with the color
        self.image.fill(pygame.Color(color))
        # get the rect of the surface
        self.rect = self.image.get_rect(center=pos)
        # create a vector for the position
        self.pos = pygame.Vector2(pos)
        # create a random vector for the direction
        self.direction = pygame.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 1])).normalize()

    def update(self, events, dt):
        # move the position by the direction scaled by the delta time
        self.pos += self.direction * dt / 10
        # update the rect center
        self.rect.center = self.pos
        # randomly change the direction
        if random.randint(0, 100) < 10:
            self.direction = pygame.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 1])).normalize()


# this class represents the game state and logic
class Game:
    def __init__(self, font):
        self.font = font
        # the game state can be RUNNING or SELECT_POSITION
        self.state = 'RUNNING'
        # a sprite group for all sprites
        self.sprites = pygame.sprite.Group()
        # a sprite group for all actors
        self.actors = pygame.sprite.Group()
        # a callback function for the select position action
        self.callback = None

    def update(self, events, dt):
        # loop through the events
        for event in events:
            # check if the mouse button was pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                # check if the game state is select position
                if self.state == 'SELECT_POSITION' and self.callback:
                    # call the callback with the mouse position
                    self.callback(event.pos)
                    # change the game state back to running
                    self.state = 'RUNNING'
        # update all the sprites
        self.sprites.update(events, dt)

    def draw(self, screen):
        # fill the screen with black or grey depending on the game state
        screen.fill(pygame.Color('black' if self.state == 'RUNNING' else 'grey'))
        # draw all the sprites
        self.sprites.draw(screen)
        # draw some info text for the player
        if self.state == 'SELECT_POSITION':
            screen.blit(self.font.render('Select a position', True, pygame.Color('black')), (150, 400))

    # a function to ask the player to select a position
    def select_position(self, callback):
        self.state = 'SELECT_POSITION'
        self.callback = callback


# the action for the green button
# when invoked, ask the game for the player
# to select a position, and spawn a green
# guy at that position
def green_action(game_obj):
    def create_green(pos):
        WalkingRect(pos, 'green', game_obj)

    game_obj.select_position(create_green)


# the same but spawn a red guy instead
def red_action(game_obj):
    def create_red(pos):
        WalkingRect(pos, 'darkred', game_obj)

    game_obj.select_position(create_red)


def main():
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    screen_rect = screen.get_rect()
    font = pygame.font.SysFont(None, 26)
    clock = pygame.time.Clock()
    game = Game(font)
    # create some buttons with different actions
    ImageButton('solve.png', 10, 600, solve_action, game)
    ImageButton('end.png', 350, 600, EndGame, game)
    TextButton('CREATE GREEN', 10, 10, 150, 40, 'green', font, green_action, game)
    TextButton('CREATE RED', 10, 50, 150, 40, 'darkred', red_action, game)
    TextButton('KILL', 10, 90, 150, 40, 'red', font, lambda game_obj: [x.kill() for x in game_obj.actors], game)
    # the main