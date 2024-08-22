import curses
import random
import time
import sys
from enum import Enum
import os

class Directions(Enum):
    UP = 2  
    RIGHT = 3
    DOWN = 1
    LEFT = 4

def flatten_array(matrix):
    flattned = []
    for row in matrix:
        flattned += row
    return flattned

def decimal_to_binary(decimal:int):
    out = []
    for s in str(bin(decimal)[2:]):
        out.append(int(s))
    return out

def treegonal_to_decimal(trigonal_array):
    decimal = 0
    for index ,i in enumerate(trigonal_array):
        decimal += i*(2**index)
    return decimal
def select_part_of_array(array , first_1 , first_2 , second_1 , second_2):
    out = []
    for index , i in enumerate(array):
        if index>first_1 and index< first_2:
            out.append(i[second_1:second_2])        
    return out


class environment:
    def __init__(self):
        self.terminal = False
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        self.WIDTH = 40
        self.HEIGTH = 15
        self.margin_X = 0
        self.margin_Y = 0
        self.world = []
        self.bullets = []
        self.player_x = 0
        self.x_spawn = 8
        self.player_y = 0
        self.wall_y1 = 0
        self.wall_y2 = 0
        self.hole_possibility = .5
        self.gap_width = 3
        self.Level = 1
        self.enemy_symbol = "Y"
        self.zigzag_coord = 1
        self.delay_time = .05
        self.enemy_prob = .15
        self.enemy_killed = 0
        self.max_bullets = 3
        self.reset(self.HEIGTH, self.WIDTH)
        self.observable_size = 16
          #we should make observable space which is a part of world.
        #print(self.world[1][])
    def reset(self, H:int,W:int):
        #print("initializing")
        self.terminal = False
        self.reset_vars()
        self.set_margines()
        for i in range(H):
            self.world.append([])
            for j in range(W+1):
                self.world[i].append(".")
        self.make_player(True)
        self.create_first_wall()
        observable_space = select_part_of_array(self.world, 3,12,9,11)
        #print(len(observable_space[0]))
        for i in range(len(observable_space)):
            for j in range(len(observable_space[i])):
                observable_space[i][j] = 1 if observable_space[i][j] in "\-/" else 1 if observable_space[i][j] in "Y" else 0 
        return  (treegonal_to_decimal(decimal_to_binary(self.player_y)+decimal_to_binary(self.max_bullets-len(self.bullets))+flatten_array(observable_space)),self.terminal)

    def step(self, action):
        #print("main started")
        self.move_world_to_left()
        self.create_and_place_wall()
        self.fires_go()
        
        reward = 0
        #print_world(world , margin_X , margin_Y)
        self.stdscr.refresh()
        try:
            key = self.stdscr.getkey()
        except:
            key = ""
        if(key == "q"):
            quit()
        if key == "p":
            self.pause(self.stdscr)
        if(action == 3):
            self.fire()
            reward -= 4
        elif action == 2:
            self.move_player(Directions.UP)
        elif action == 1:
            self.move_player(Directions.DOWN)
        elif action == 0:
            reward += 0.3
        else:
            sys.exit()
        #reward += self.delete_colided_bullets()
        #reward += .3
        try:
            self.terminal, add_reward = self.check_collision()
            reward+= add_reward
        except:
            pass
        observable_space = select_part_of_array(self.world,3,12,9,11)
        for i in range(len(observable_space)):
            for j in range(len(observable_space[i])):
                observable_space[i][j] = 1 if observable_space[i][j] in "\-/" else 1 if observable_space[i][j] in "Y" else 0 
        return  (treegonal_to_decimal(decimal_to_binary(self.player_y)+decimal_to_binary(self.max_bullets-len(self.bullets))+flatten_array(observable_space)),reward,self.terminal)

    def pause(self, stdscr):

        stdscr.addstr(self.margin_Y,self.WIDTH+self.margin_X-6,"Paused!")
        while True:
            try:
                key = stdscr.getkey()
            except:
                key = ""
            if(key == "p"):
                break


    def reset_vars(self):
        self.world.clear()
        self.bullets.clear()
        self.hole_possibility = .5
        self.gap_width = 5
        self.Level = 1
        self.zigzag_coord = 1
        self.delay_time = .05
        self.enemy_prob = .15
        self.enemy_killed = 0


    def print_world(self,world : list,start_X : int , start_Y : int):
        for i in range(len(self.world)):
            for j in range(len(self.world[0])):
                self.stdscr.addstr(i+start_Y,j+start_X,self.world[i][j])
                if random.random() > .15 and self.world[i][j] == ".":
                    self.stdscr.addstr(i+start_Y,j+start_X," ")
                if i == 0 or i == len(self.world) -1:
                    self.stdscr.addstr(i+start_Y,j+start_X,"-")
                if j == 0 or j == len(self.world[0]) - 1 :
                    self.stdscr.addstr(i+start_Y,j+start_X,"|")
        self.stdscr.addstr(start_Y,len(self.world[0])-1+start_X,"+")
        self.stdscr.addstr(start_Y,start_X,"+")
        self.stdscr.addstr(len(self.world)-1+start_Y,len(self.world[0])-1+start_X,"+")
        self.stdscr.addstr(len(self.world)-1+start_Y,start_X,"+")
        self.stdscr.addstr(self.margin_Y,self.margin_X,f'Level {self.Level}')
        self.stdscr.addstr(self.margin_Y,self.margin_X+10,f'Score {self.enemy_killed}')
        self.print_bullets()
        self.print_player(start_X, start_Y)
        #print_bullets()   
        

    class fire_bullet:
        def __init__(self,x:int,y:int):
            self.y = y
            self.x = x
        def Go(self):
            self.x = self.x + 1
        
    def print_bullets(self):

        for i in range(len(self.bullets)):
            self.stdscr.addstr(self.bullets[i].y+self.margin_Y,self.bullets[i].x+self.margin_X,"-")
        self.stdscr.addstr(self.margin_Y+self.HEIGTH-2,2+self.margin_X-1," ")
        for i in range(self.max_bullets-len(self.bullets)):    
            self.stdscr.addstr(self.margin_Y+self.HEIGTH-2,i+2+self.margin_X,">")
        self.stdscr.addstr(self.margin_Y+self.HEIGTH-2,i+3+self.margin_X,"  ")

    def fires_go(self):
        for i in range(len(self.bullets)):
            self.bullets[i].Go()
    def delete_colided_bullets(self):
        reward = 0
        a = len(self.bullets)
        for bullet in self.bullets:
            if(bullet.x == self.WIDTH):
                self.bullets.remove(bullet)
            for i in range(len(self.world)):
                for j in range(len(self.world[0])):
                    if self.world[i][j] in "-/\\"+self.enemy_symbol and (bullet.x == j or bullet.x == j-1) and bullet.y == i:
                        
                        try:
                            self.bullets.remove(bullet)
                        except:
                            pass
                        if self.world[i][j] == self.enemy_symbol:
                            self.enemy_killed = self.enemy_killed+1
                            self.world[i][j] = "."
                            reward += 10
        return reward
    def fire(self):
            if(len(self.bullets) < self.max_bullets):
                bullet = self.fire_bullet(self.x_spawn+1,self.player_y)
                self.bullets.append(bullet)
            #print("fire")
            #print(len(bullets))


    def create_enemy(self,enemy_y : int , enemy_x : int):
        if random.random() < self.enemy_prob:
            self.world[enemy_y][enemy_x] = self.enemy_symbol


    def get_terminal_size(self):
        size = os.get_terminal_size()
        return size.columns , size.lines


    def create_first_wall(self):
        self.wall_y1 = random.randint(1 , self.HEIGTH-8)
        while True:
            self.wall_y2 = random.randint(0 , self.HEIGTH-1)
            if self.wall_y2 > self.wall_y1+self.gap_width-1:
                break

    def check_collision(self):
        for i in range(len(self.world)):
            for j in range(len(self.world[0])):
                if not self.world[i][j] == "." and self.player_x == j and self.player_y == i:
                    #print("collision")
                    #self.stdscr.addstr(self.margin_Y,self.margin_X,"Boom!!!")
                    self.stdscr.refresh()
                    #time.sleep(5)
                    if self.world[i][j] == self.enemy_symbol:
                        self.enemy_killed+=1
                        self.world[i][j] = "."
                        return False,5

                    else:
                        return True,0
                    

                    #quit()

    def move_world_to_left(self):
        for i in range(len(self.world)):
            for j in range(len(self.world[0])-1):    
                self.world[i][j] = self.world[i][j+1]
                if(self.world[i][j+1] == self.enemy_symbol):
                    self.world[i][j+1] = " "

            if i > self.wall_y1 and i < self.wall_y2 and not self.world[i][j] == self.enemy_symbol:
                self.world[i][self.WIDTH-1] = "."
            if i < self.wall_y1 or i > self.wall_y2 :
                self.world[i][self.WIDTH-1] = " "
            
    def create_and_place_wall(self):
        rand1 = random.random() 
        rand2 = random.random()
        if rand1> self.hole_possibility:
            if self.wall_y1 > 1:
                self.wall_y1 = self.wall_y1-1
                self.world[self.wall_y1][self.WIDTH ] = "/"
            else:
                self.world[self.wall_y1][self.WIDTH ] = "-"
        else:
            if self.wall_y1 < self.wall_y2 - self.gap_width:
                self.wall_y1 = self.wall_y1+1
                self.world[self.wall_y1][self.WIDTH ] = "\\"
            else:
                self.world[self.wall_y1][self.WIDTH ] = "-"
        if rand2> self.hole_possibility:
            if self.wall_y2 < self.HEIGTH - 1:
                self.wall_y2 = self.wall_y2+1
                self.world[self.wall_y2][self.WIDTH ]= "\\"
            else:
                self.world[self.wall_y2][self.WIDTH ] = "-"
            
        else:
            if self.wall_y1 < self.wall_y2 - self.gap_width:
                self.wall_y2 = self.wall_y2-1
                self.world[self.wall_y2][self.WIDTH ] = "/"
            else:
                self.world[self.wall_y2][self.WIDTH ]= "-"
        enemy_y = random.randint(self.wall_y1+1 , self.wall_y2)
        self.create_enemy(enemy_y,self.WIDTH)
        
    def set_margines(self):
        screen_w , screen_h = self.get_terminal_size()
        self.margin_X = 0
        self.margin_Y = 0
        if screen_w> self.WIDTH and screen_h > self.HEIGTH:
            self.margin_Y = int((screen_h - self.HEIGTH)/2)
            self.margin_X = int((screen_w - self.WIDTH)/2)
        
    def make_player(self,init:bool):
        # to be corrected

        if init:
            self.player_x = self.x_spawn 
            self.player_y = random.randint(int(self.HEIGTH/3),int(2*self.HEIGTH/3))

    def print_player(self,start_X : int , start_Y : int):
        self.stdscr.addstr(self.player_y+start_Y,self.player_x+start_X,"X")
        #stdscr.addstr(player_y+start_Y-1,player_x+start_X-1,"\\")
        #stdscr.addstr(player_y+start_Y-1,player_x+start_X+1,"/")
        #stdscr.addstr(player_y+start_Y+1,player_x+start_X-1,"/")
        #stdscr.addstr(player_y+start_Y+1,player_x+start_X+1,"\\")

    def move_player(self,direction : Directions):

        # to be corrected
        if direction == Directions.RIGHT and self.player_x < self.WIDTH-1:
            self.player_x = self.player_x + 1
        if direction == Directions.LEFT and self.player_x > 0:
            self.player_x = self.player_x - 1
        if direction == Directions.UP and self.player_y > 0:
            self.player_y = self.player_y - 1
        if direction == Directions.DOWN and self.player_y < self.HEIGTH-1:
            self.player_y = self.player_y + 1
            
    def quit():
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        sys.exit()
        return 0
