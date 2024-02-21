import pygame
import math
import random
import time
import sys
import copy

# Global Vars
green = (1, 133, 36)
light_green = (0, 255, 68)
gray = (165, 184, 170)
light_gray = (176, 191, 180)
red = (207, 115, 29)
fruit_tile = mushroom_tile = shroom_timer = None
tiles = []
shroom_tiles = []
fruit_spawn = game_cont = mushroom_spawn = mushroom_sequence = False
screen = None

# Images
apple = pygame.transform.scale(pygame.image.load("data/apple.png"),(40,40))
apple_shadow = pygame.transform.scale(pygame.image.load("data/apple_shadow.png"),(40,40))
mushroom = pygame.transform.scale(pygame.image.load("data/mushroom.png"),(40,40))
mushroom_shadow = pygame.transform.scale(pygame.image.load("data/mushroom_shadow.png"),(40,40))


class Tile:
    def __init__(self, pos_x, pos_y, color, screen):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.color = color
        self.screen = screen
        self.size = 50

    def display(self):
        pygame.draw.rect(self.screen, self.color, pygame.Rect((self.pos_x, self.pos_y), (self.size, self.size)))


class Snake:
    def __init__(self, screen, pos_x, pos_y, color):
        self.screen = screen
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.static_pos = (pos_y,pos_x)
        self.tail_pos = (pos_x-50,pos_y)
        self.length = 3
        self.body_parts = [(pos_x-50,pos_y),(pos_x-100,pos_y)]
        self.orientation = (1, 0)
        self.color = color
        self.speed = 10
        self.direction = (1, 0)
        self.add = False
        self.change_dir = 3
        img = pygame.transform.scale(pygame.image.load("data/snake_head.png"),(50,50))
        self.head_up = img
        self.head_down = pygame.transform.rotate(img,180)
        self.head_left = pygame.transform.rotate(img,90)
        self.head_right = pygame.transform.rotate(img,270)

    def automove(self,screen):
        new_x = self.speed * self.direction[0] + self.pos_x
        new_y = self.speed * self.direction[1] + self.pos_y

        if new_x >= 800 or new_x < 0 or new_y >= 800 or new_y < 0:
            game_over(screen,self)
            return

        self.pos_x = new_x
        self.pos_y = new_y

        # Tail
        c = self.body_parts[-2]
        tail = self.body_parts[-1]
        dir_x = dir_y = 0

        if c[0] - tail[0] > 0:
            dir_x = 1
        elif c[0] - tail[0] < 0:
            dir_x = -1
        if c[1] - tail[1] > 0:
            dir_y = 1
        elif c[1] - tail[1] < 0:
            dir_y = -1

        self.tail_pos = (self.tail_pos[0]+dir_x*self.speed,self.tail_pos[1]+dir_y*self.speed)

        if new_x % 50 == 0 and new_y % 50 == 0:
            self.static_pos = (new_x+50*self.orientation[0],new_y+50*self.orientation[1])
            if self.direction != self.orientation:
                self.change_dir = 1
                self.direction = self.orientation

            check_eat(self)
            self.update_body()
            if self.check_collision():
                self.display()
                pygame.display.flip()
                self.update_body()
                self.display()
                pygame.display.flip()
                self.update_body()
                self.display()
                pygame.display.flip()
                game_over(self.screen,self)


    def check_collision(self):
        for body in self.body_parts:
            if body == self.static_pos:
                return True
        return False

    def change_orientation(self, dir):
        if dir == self.direction:
            return
        elif dir == (self.direction[0] * -1, self.direction[1] * -1):
            return

        self.orientation = dir

    def display(self):

        bp = self.body_parts

        for i in range(len(self.body_parts)):
            b = self.body_parts[i]

            if i < len(self.body_parts)-1:

                if i == 0: # straight in x and y
                    if b[0] == self.static_pos[0] and b[1] != self.static_pos[1] and bp[i+1][0] == b[0] and bp[i+1][1] != b[1]:
                        pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1], 34, 50))
                    elif b[0] != self.static_pos[0] and b[1] == self.static_pos[1] and bp[i+1][0] != b[0] and bp[i+1][1] == b[1]:
                        pygame.draw.rect(self.screen, self.color, (b[0], b[1]+8, 50, 34))
                    else:
                        m = b
                        h = (self.pos_x,self.pos_y)
                        t = bp[i+1]
                        if t[0] > m[0] or h[0] > m[0]: #right
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1]+8, 42, 34))
                        elif t[0] < m[0] or h[0] < m[0]: # left
                            pygame.draw.rect(self.screen, self.color, (b[0], b[1]+8, 42, 34))
                        else:
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1]+8, 34, 34))
                        if h[1] < m[1] or t[1] < m[1]: # up
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1], 34, 42))
                        elif h[1] > m[1] or t[1] > m[1]: # down
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1]+8, 34, 42))
                        else:
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1]+8, 34, 34))
                else: # x, y straight
                    if b[0] == bp[i-1][0] and b[1] != bp[i-1][1] and bp[i+1][0] == b[0] and bp[i+1][1] != b[1]:
                        pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1], 34, 50))
                    elif b[0] != bp[i-1][0] and b[1] == bp[i-1][1] and bp[i+1][0] != b[0] and bp[i+1][1] == b[1]:
                        pygame.draw.rect(self.screen, self.color, (b[0], b[1]+8, 50, 34))
                    else:
                        m = b
                        h = bp[i-1]
                        t = bp[i+1]
                        # Up-left or right
                        if t[0] > m[0] or h[0] > m[0]: #right
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1]+8, 42, 34))
                        else: # left
                            pygame.draw.rect(self.screen, self.color, (b[0], b[1]+8, 42, 34))

                        if h[1] < m[1] or t[1] < m[1]: # up
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1], 34, 42))
                        else: # down
                            pygame.draw.rect(self.screen, self.color, (b[0]+8, b[1]+8, 34, 42))

            else:
                m = b
                t = bp[i-1]
                if m[0] == t[0]:
                    pygame.draw.rect(self.screen, red, (self.tail_pos[0]+8, self.tail_pos[1], 34, 50))
                else:
                    pygame.draw.rect(self.screen, red, (self.tail_pos[0], self.tail_pos[1]+8, 50, 34))

        if self.direction == (0,1) or self.direction == (0,-1):
            if self.direction == (0,-1):
                pygame.draw.rect(self.screen, self.color, (self.pos_x+8, self.pos_y+10, 34, 30))
                self.screen.blit(self.head_up,(self.pos_x,self.pos_y-25))
            else:
                if self.change_dir > 2:
                    pygame.draw.rect(self.screen, self.color, (self.pos_x+8, self.pos_y-5, 34, 30))
                    self.screen.blit(self.head_down,(self.pos_x,self.pos_y+25))
                else:
                    self.change_dir += 1
                    self.screen.blit(self.head_down,(self.pos_x,self.pos_y+25))
        else:
            if self.direction == (-1,0):
                pygame.draw.rect(self.screen, self.color, (self.pos_x+10, self.pos_y+8, 30, 34))
                self.screen.blit(self.head_left,(self.pos_x-25,self.pos_y))
            else:
                if self.change_dir > 2:
                    pygame.draw.rect(self.screen, self.color, (self.pos_x-5, self.pos_y+8, 30, 34))
                    self.screen.blit(self.head_right,(self.pos_x+25,self.pos_y))
                else:
                    self.screen.blit(self.head_right,(self.pos_x+25,self.pos_y))
                    self.change_dir += 1

        # self.screen.blit(self.head_img,(self.pos_x,self.pos_y))

    def update_body(self):
        if self.length == 1 and not self.add:
            return
        elif self.length == 1 and self.add:
            self.body_parts.append((self.pos_x,self.pos_y))
            self.length += 1
            self.add = False
            self.tail_pos = ((self.pos_x,self.pos_y))
            return

        temp = None
        add = None
        for i in range(len(self.body_parts)):
            if i == 0:
                temp = add = self.body_parts[0]
                self.body_parts[0] = (self.pos_x, self.pos_y)
                continue

            add = self.body_parts[i]
            self.body_parts[i] = temp
            temp = add

        if self.add:
            self.body_parts.append(add)
            self.length += 1
            self.tail_pos = add
            self.add = False

    def add_body(self):
        self.add = True


def spawn_fruit(screen,snake):
    redo = False
    fruit = random.randint(0, 15 * 15)
    global fruit_tile
    fruit_tile = tiles[fruit]
    for body in snake.body_parts:
        if (fruit_tile.pos_x,fruit_tile.pos_y) == body:
            redo = True
            break
    if redo:
        spawn_fruit(screen,snake)


def display_fruit(screen):
    #pygame.draw.rect(screen, green, (fruit_tile.pos_x, fruit_tile.pos_y, 50, 50))
    screen.blit(apple_shadow,(fruit_tile.pos_x+7, fruit_tile.pos_y+8))
    screen.blit(apple,(fruit_tile.pos_x+5, fruit_tile.pos_y+5))

    if mushroom_spawn:
        screen.blit(mushroom_shadow,(mushroom_tile.pos_x+7, mushroom_tile.pos_y+8))
        screen.blit(mushroom,(mushroom_tile.pos_x+5, mushroom_tile.pos_y+5))


def spawn_mushroom(screen,snake):
    redo = False
    mush = random.randint(0, 15 * 15)
    global mushroom_tile
    mushroom_tile = tiles[mush]

    for body in snake.body_parts:
        if (mushroom_tile.pos_x,fruit_tile.pos_y) == body or mushroom_tile == fruit_tile:
            redo = True
            break
    if redo:
        spawn_mushroom(screen,snake)
    else:
        global mushroom_spawn
        mushroom_spawn = True


def check_eat(snake):
    global mushroom_spawn, mushroom_sequence, shroom_timer, shroom_tiles
    if fruit_tile.pos_x == snake.pos_x and fruit_tile.pos_y == snake.pos_y:
        snake.add_body()
        global fruit_spawn
        fruit_spawn = False
    if mushroom_spawn and mushroom_tile.pos_x == snake.pos_x and mushroom_tile.pos_y == snake.pos_y:
        mushroom_spawn = False
        mushroom_sequence = True
        init_tiles(shroom_tiles)
        shroom_timer = pygame.time.get_ticks()


def init_tiles(ls):
    for i in range(16):
        x = i * 50
        for j in range(16):
            y = j * 50
            if (i % 2 == 0 and j % 2 == 0) or (i % 2 != 0 and j % 2 != 0):
                ls.append(Tile(x, y, gray, screen))
            else:
                ls.append(Tile(x, y, light_gray, screen))


def show_score(screen,snake,choice=1):
    score_font = pygame.font.SysFont('Palatino Linotype', 70)
    score_surface = score_font.render('Score : ' + str(snake.length-3), True, (240,240,240))
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (300, 400)
    else:
        score_rect.midtop = (800/2, 800/1.25)
    screen.blit(score_surface, score_rect)


def game_over(screen,snake):
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('GAME OVER', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (800/2, 800/4)
    screen.fill((10,10,50))
    screen.blit(game_over_surface, game_over_rect)
    show_score(screen, snake)
    pygame.display.flip()
    time.sleep(2)
    sys.exit()

    global game_cont
    game_cont = True


def main(l_dim, w_dim):
    global screen
    # Init window/screen
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("Palatino Linotype", 30)

    background_color = (20, 20, 20)
    screen = pygame.display.set_mode((l_dim, w_dim))
    pygame.display.set_caption("Psychedelic Snake")
    # Play darude sandstorm with lsd
    # make controls weird or smth with mushroom

    # Init environment & graphics
    init_tiles(tiles)
    clock = pygame.time.Clock()

    # Init snake
    snake = Snake(screen, 200, 400, red)

    # Main Loop
    running = True

    global game_cont
    game_cont = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or game_cont:
                running = False

            # Move input for snake
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    snake.change_orientation((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_orientation((1, 0))
                elif event.key == pygame.K_UP:
                    snake.change_orientation((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_orientation((0, 1))

        global mushroom_sequence, fruit_spawn
        if not mushroom_sequence:
            for t in tiles:
                t.display()
        else:
            screen.fill(gray)
            for tile in shroom_tiles:
                rng = random.uniform(-10,10)
                #tile.pos_x = tile.pos_x + 5*rng
                tile.size = tile.size +0.2*rng
                a = tile.color[0]-0.2*rng
                b = tile.color[1]+0.8*rng
                c = tile.color[2]-0.1*rng
                col1 = a if 240 > a > 0 else tile.color[0]
                col2 = b if 240 > b > 0 else tile.color[1]
                col3 = c if 240 > c > 0 else tile.color[2]
                tile.color = (col1,col2,col3)
                tile.display()

        if mushroom_sequence and pygame.time.get_ticks() - shroom_timer > 7000:
            mushroom_sequence = False

        if not fruit_spawn:
            fruit_spawn = True
            spawn_fruit(screen,snake)
            if not mushroom_spawn and not mushroom_sequence and random.randint(1,2) == 1:
                spawn_mushroom(screen,snake)

        display_fruit(screen)

        snake.automove(screen)
        snake.display()
        pygame.display.flip()

        clock.tick(20)


if __name__ == "__main__":
    main(800, 800)
