import pygame
import threading
import random
import time
from collections import deque

game_end = threading.Event()

class GameBoard:
    def __init__(self, length):
        pygame.init()
        # set up the game board
        self.screen = pygame.display.set_mode((1000, 1000))
        self.screen_size = 1000
        self.length = length
        self.player_x, self.player_y = int(length/2), int(length/2)
        self.game_board = [[0 for _ in range(length)] for _ in range(length)]
        self.game_board[self.player_x][self.player_y] = 1
        self.bullets = []
        self.player_hit_box = None

        self.switch_time = time.time()

        # synchronize with game_event
        self.game_event = GameEvent(length, self.game_board, self.bullets)

        self.clock = pygame.time.Clock()

    def handle_key_event(self, event):
        if event.key == pygame.K_LEFT:
            # 鍵盤左鍵被按下
            # print("Left arrow key pressed")
            self.game_board[self.player_x][self.player_y] = 0
            self.player_x -= 1
            if self.player_x < 1:
                self.player_x = 1
            
        elif event.key == pygame.K_RIGHT:
            # 鍵盤右鍵被按下
            # print("Right arrow key pressed")
            self.game_board[self.player_x][self.player_y] = 0
            self.player_x += 1
            if self.player_x > self.length - 2:
                self.player_x = self.length - 2

        elif event.key == pygame.K_UP:
            # 鍵盤上鍵被按下
            # print("Up arrow key pressed")
            self.game_board[self.player_x][self.player_y] = 0
            self.player_y -= 1
            if self.player_y < 1:
                self.player_y = 1
        
        elif event.key == pygame.K_DOWN:
            # 鍵盤下鍵被按下
            # print("Down arrow key pressed")
            self.game_board[self.player_x][self.player_y] = 0
            self.player_y += 1
            if self.player_y > self.length - 2:
                self.player_y = self.length - 2
            
        self.game_board[self.player_x][self.player_y] = 1

    def draw_text(self, text, pos_x=50, pos_y=50, color=(0, 0, 0)):
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (pos_x, pos_y))

    def arrow(self, pos_x, pos_y, direction):
        ORANGE = (255, 102, 0)
        X = pos_x
        Y = pos_y

        if direction == "up":
            pygame.draw.polygon(self.screen, ORANGE, [(X+49, Y+9), (X+9, Y+49), (X+89, Y+49)])
            pygame.draw.rect(self.screen, ORANGE, (X+29, Y+49, 40, 40))
 
        elif direction == "down":
            pygame.draw.polygon(self.screen, ORANGE, [(X+49, Y+89), (X+9, Y+49), (X+89, Y+49)])
            pygame.draw.rect(self.screen, ORANGE, (X+29, Y+9, 40, 40))

        elif direction == "left":
            pygame.draw.polygon(self.screen, ORANGE, [(X+9, Y+49), (X+49, Y+9), (X+49, Y+89)])
            pygame.draw.rect(self.screen, ORANGE, (X+49, Y+29, 40, 40))

        elif direction == "right":
            pygame.draw.polygon(self.screen, ORANGE, [(X+89, Y+49), (X+49, Y+9), (X+49, Y+89)])
            pygame.draw.rect(self.screen, ORANGE, (X+9, Y+29, 40, 40))

    def draw_bullet(self):
        for bullet in self.bullets:
            if not self.game_event.switch_mode.is_set():
                if self.game_event.current_event in ["RollingStone", "IronCannon"]:
                    pygame.draw.circle(self.screen, bullet.color, (bullet.x, bullet.y), 40)
                    if bullet.hit_box.colliderect(self.player_hit_box):
                        print("player has been hit by bullet")
                        self.game_event.switch_mode.set()
                        self.switch_time = time.time()
                        time.sleep(0.5)
                        break

                    bullet.move()
                    if bullet.x <= 130 or bullet.x >= self.screen_size - 130 or bullet.y <= 130 or bullet.y >= self.screen_size - 130:
                        self.bullets.remove(bullet)
                
                elif self.game_event.current_event in ["LaserWeapon", "PillarHell"]:
                    pygame.draw.rect(self.screen, bullet.color, bullet.laser_shape)
                    if bullet.hit_box.colliderect(self.player_hit_box):
                        print("player has been hit by bullet")
                        self.game_event.switch_mode.set()
                        self.switch_time = time.time()
                        time.sleep(0.5)
                        break

                    bullet.move()
                    if bullet.x <= 140: bullet.x = 140
                    elif bullet.y <= 140: bullet.y = 140
                    elif bullet.x >= self.screen_size - 140: bullet.x = self.screen_size - 140
                    elif bullet.y >= self.screen_size - 140: bullet.y = self.screen_size - 140
                        
                    if time.time() - bullet.start_time > 0.5:
                        self.bullets.remove(bullet)

    def draw_board(self):
        pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, 1000, 1000))
        # 0: empty, 1: player, 2: arrow

        for i in range(self.length):
            for j in range(self.length):
                pos = (100 + i * 98, 100 + j * 98)

                if self.game_board[i][j] == 1: # 玩家圖標
                    self.player_hit_box = pygame.Rect(pos[0] + 40, pos[1] + 40, 20, 20)
                    pygame.draw.circle(self.screen, (255, 0, 0), (pos[0] + 51, pos[1] + 51), 30)

                pygame.draw.rect(self.screen, (0, 0, 0), (pos[0], pos[1], 100, 100), 2)
                pygame.draw.rect(self.screen, (0, 0, 0), (198, 198, 98 * (self.length - 2) + 2, 98 * (self.length - 2) + 2), 10)
    
    def draw_arrow(self):
        for i in range(self.length):
            for j in range(self.length):
                pos = (100 + i * 98, 100 + j * 98)
                if time.time() - self.switch_time > 2:
                    if self.game_board[i][j] == 2:
                        if i == 0: self.arrow(*pos, "right")
                        elif j == 0: self.arrow(*pos, "down")
                        elif i == self.length - 1: self.arrow(*pos, "left")
                        elif j == self.length - 1: self.arrow(*pos, "up")
    def draw(self):
        self.draw_board()
        self.draw_bullet()
        self.draw_arrow()
        self.draw_text(f"Wave: {self.game_event.score}", 50, 50)

class GameEvent: 
    def __init__(self, length, game_board, bullets, interval=0.8):
        self.length = length
        self.shoot_obj = ShootObject()
        self.event_queue = deque(["RollingStone", "IronCannon", "LaserWeapon"])
        self.current_event = None

        self.shoot_space = [[(0, i), (length-1, i)] for i in range(1, length-1)]
        self.shoot_space.extend([[(i, 0), (i, length-1)] for i in range(1, length-1)])
        self.current_shoot_poses = []
        self.game_board = game_board
        self.bullets = bullets

        self.switch_mode = threading.Event()
        self.interval = interval
        self.score = 0
        self.total_score = 1
        self.survive_counter = {"RollingStone": 0, "IronCannon": 0, "LaserWeapon": 0, "PillarHell": 0}
                    
    def set_shooter(self):
        """
        set shooter pos
        """
        if not self.switch_mode.is_set():
            weight = [1, 3, 4, 5, 5] # weight of shooter count
            shooter_count = random.choices(range(1, self.length-2), weights=weight)[0]
            self.current_shoot_poses = random.sample(self.shoot_space, shooter_count)

            for i in range(shooter_count):
                self.current_shoot_poses[i] = self.current_shoot_poses[i][random.randint(0, 1)]
            
            for _ in range(2):
                for i in range(shooter_count):
                    self.game_board[self.current_shoot_poses[i][0]][self.current_shoot_poses[i][1]] = 2
                
                time.sleep(self.interval * 0.2)

                for i in range(shooter_count):
                    self.game_board[self.current_shoot_poses[i][0]][self.current_shoot_poses[i][1]] = 0
                
                time.sleep(self.interval * 0.2) 
        
            self.score += 1
            time.sleep(self.interval * 0.2)
        
    def shoot(self): 
        """
        add bullets to bullets list
        """
        if not self.switch_mode.is_set():
            self.set_shooter()
            deltas = []

            if self.current_event == "RollingStone":  speed = random.randint(10, 20)
            elif self.current_event == "IronCannon":  speed = random.randint(30, 50)
            elif self.current_event == "LaserWeapon": speed = random.randint(200, 200)
            elif self.current_event == "PillarHell":  speed = random.randint(20, 30)
            
            for shooter in self.current_shoot_poses:
                if shooter[0] == 0: deltas.append((speed, 0))                   # right
                elif shooter[1] == 0: deltas.append((0, speed))                 # down
                elif shooter[0] == self.length - 1: deltas.append((-speed, 0))  # left
                elif shooter[1] == self.length - 1: deltas.append((0, -speed))  # up

            draw_poses = []
            for pos in self.current_shoot_poses:
                draw_poses.append((100 + pos[0] * 98 + 50, 100 + pos[1] * 98 + 50))

            bullets_to_add = self.shoot_obj.__getattribute__(self.current_event)(draw_poses, deltas).bullets
            for bullet in bullets_to_add:
                if hasattr(bullet, 'start_time'):
                    if bullet.start_time is None:
                        bullet.start_time = time.time()

            self.bullets.extend(bullets_to_add)
        
    def set_mode(self): 
        """
        THREAD: process current mode, shoot bullets
        """
        while len(self.event_queue) > 0:
            self.bullets.clear() # clear prev bullets
            self.switch_mode.clear()
            self.current_event = self.event_queue.popleft()
            print(f"Current mode: {self.current_event}")
            while not self.switch_mode.is_set():
                self.shoot()
                
            self.survive_counter[self.current_event] += self.score
            self.score = 0
            time.sleep(3)

        game_end.set()
        
        for val, key in enumerate(self.survive_counter):
            mode_score = self.survive_counter[key]
            self.total_score *= mode_score if mode_score > 0 else 1
            
class Bullet: 
    def __init__(self, x, y, dx, dy, color: tuple):
        # bullet = (x, y, dx, dy, color)
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.hit_box = pygame.Rect(x-30, y-30, 60, 60)

    def __repr__(self) -> str:
        return f"Bullet(x={self.x}, y={self.y}, dx={self.dx}, dy={self.dy}, color={self.color})"
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.hit_box = pygame.Rect(self.x-30, self.y-30, 60, 60)

class Pillar:
    def __init__(self, x, y, dx, dy, color: tuple, exist_time, is_collide):
        # pillar = (x, y, dx, dy, color, exist_time, is_collide)
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.exist_time = exist_time
        self.is_collide = is_collide
        self.hit_box = pygame.Rect(x-20, y-20, 40, 40)

        self.laser_shape = pygame.Rect(x-40, y-40, 80, 80)
        self.start_time = None
    
    def __repr__(self) -> str:
        return f"Pillar(x={self.x}, y={self.y}, dx={self.dx}, dy={self.dy}, color={self.color}, is_collide={self.is_collide})"

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.dx < 0 or self.dy < 0:
            self.hit_box = pygame.Rect(
                self.x - 20, 
                self.y - 20, 
                abs(self.start_x - self.x) + 40, 
                abs(self.start_y - self.y) + 40
            )
            self.laser_shape = (
                self.x - 40, 
                self.y - 40, 
                abs(self.start_x - self.x) + 80, 
                abs(self.start_y - self.y) + 80
            )
        elif self.dx > 0 or self.dy > 0:
            self.hit_box = pygame.Rect(
                self.start_x - 20, 
                self.start_y - 20, 
                abs(self.start_x - self.x) + 40, 
                abs(self.start_y - self.y) + 40
            )
            self.laser_shape = (
                self.start_x - 40, 
                self.start_y - 40, 
                abs(self.start_x - self.x) + 80, 
                abs(self.start_y - self.y) + 80
            )

class ShootObject:
    def __init__(self): ... 
    def __repr__(self) -> str:
        return f"ShootObject(RollingStone, IronCannon, LaserWeapon, PillarHell)"
    
    class RollingStone:
        def __init__(self, poses, deltas, color=(173, 152, 118)):
            self.bullets = [Bullet(pos[0], pos[1], delta[0], delta[1], color) for pos, delta in zip(poses, deltas)]
    
    class IronCannon:
        def __init__(self, poses, deltas, color=(46, 46, 46)):
            self.bullets = [Bullet(pos[0], pos[1], delta[0], delta[1], color) for pos, delta in zip(poses, deltas)]
    
    class LaserWeapon:
        def __init__(self, poses, deltas, exist_time=0.5, color=(222, 222, 130), is_collide=False):
            self.bullets = [Pillar(pos[0], pos[1], delta[0], delta[1], color, exist_time, is_collide) for pos, delta in zip(poses, deltas)]
    
    class PillarHell:
        def __init__(self, poses, deltas, exist_time, color=(100, 100, 100), is_collide=True):
            self.bullets = [Pillar(pos[0], pos[1], delta[0], delta[1], color, exist_time, is_collide) for pos, delta in zip(poses, deltas)]


def run(game_board: GameBoard):
    game_board.draw_board()
    game_board.draw_text(f"Wave: {game_board.game_event.score}", 50, 50)
    pygame.display.update()

    for i in range(5, 0, -1):
        print(f'starting in {i} seconds')
        time.sleep(1)

    threading.Thread(target=game_board.game_event.set_mode, daemon=True).start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or game_end.is_set():
                running = False
            elif event.type == pygame.KEYDOWN:
                game_board.handle_key_event(event)
        
        game_board.draw()
        pygame.display.update()
        game_board.clock.tick(60)

    print('game_end, your score:', game_board.game_event.total_score)
    pygame.quit()
    exit()

def main():
    length = 6+2 # 6*6 moving space + outer frame
    game_board = GameBoard(length)
    run(game_board)
    
if __name__ == '__main__':
    main()