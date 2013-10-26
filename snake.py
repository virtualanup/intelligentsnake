#snake game version 3.0
#by virtualanup

import pygame,random
from pygame.locals import *
from sys import exit
import math

#direction of snake
left=-1,0
right=1,0
up=0,-1
down=0,1
directions=[up,down,right,left]

class Snake:
    def __init__(self,body , direction, color,speed):
        self.speed=speed
        self.body=body #initially located here
        self.color=color
        self.direction=self.newdirection=direction
        self.IsDead=False
    def UpdateDirection(self,game):
        self.direction=self.newdirection #the next direction is stored in newdirection....logic is updated here
    def Update(self,game):
        if self.IsDead:
            fadestep=5
            self.color=(max(self.color[0]-fadestep,0),max(self.color[1]-fadestep,0),max(self.color[2]-fadestep,0))
            if self.color[0]==0 and self.color[1]==0 and self.color[2]==0:
                self.color=(0,0,0)
                game.players.remove(self)
        else:
            #updates the snake...
            head=self.body[0]#head of snake
            head=(head[0]+self.direction[0],head[1]+self.direction[1])
            #wrap the snake around the window
            headx=game.hortiles if head[0]<0 else 0 if head[0]>game.hortiles else head[0]
            heady=game.verttiles if head[1]<0 else 0 if head[1]>game.verttiles else head[1]
            head=(headx,heady)
            #update the body and see if the snake is dead
            alivelist=[snake for snake in reversed(game.players) if not snake.IsDead]
            for snake in alivelist:
                if head in snake.body:
                    if head == snake.body[0]:
                        snake.IsDead=True
                    self.IsDead=True
                    return
            if head in game.obstacles:
                self.IsDead=True
                return
            elif head == game.foodpos:
                #the snake ate the food
                game.foodpos=0,0
                self.body.append((self.body[0]))
            #the snake hasnot collided....move along
            self.body=[head]+[self.body[i-1] for i in range(1,len(self.body))]
    def Draw(self,screen,game):
        head=self.body[0]
        pygame.draw.rect(screen,( (self.color[0]+30)%250 ,(self.color[1]+30)%250,(self.color[2]+30)%250),(head[0]*game.tilesize,head[1]*game.tilesize,game.tilesize,game.tilesize),0)
        for part in self.body[1:]:
            pygame.draw.rect(screen,self.color,(part[0]*game.tilesize,part[1]*game.tilesize,game.tilesize,game.tilesize),0)
    def processkey(self,key):
        pass #nothing to do here

class HumanSnake(Snake):
    def __init__(self,body=[(0,0)] , direction=(1,0),upkey=K_UP,downkey=K_DOWN,rightkey=K_RIGHT,leftkey=K_LEFT,color=(0,255,0)):
        super().__init__(body,direction,color,1)#speed is always 1
        #assign the keys to control the human snake
        self.upkey=upkey
        self.downkey=downkey
        self.rightkey=rightkey
        self.leftkey=leftkey
        
    def processkey(self,key):
        #we check the old direction not the new direction.
        if key==self.upkey:
            if self.direction != down:
                self.newdirection=up
        elif key==self.downkey:
            if self.direction != up:
                self.newdirection=down
        elif key==self.rightkey:
            if self.direction != left:
                self.newdirection=right
        elif key==self.leftkey:
            if self.direction != right:
                self.newdirection=left

class ComputerSnake(Snake):
    def __init__(self,body=[(0,0)] , direction=(1,0),color=(255,0,0),speed=1):
        super().__init__(body,direction,color,speed)
    def pathlen(self,frompos,topos,game):
        #this is the heruistic algorithm for the snake. 
        #topos=(min(topos[0],abs(topos[0]-game.verttiles)) , min(topos[1],abs(topos[1]-game.hortiles)))
        return int( ((frompos[0]-topos[0])**2 + (frompos[1]-topos[1])**2 )**0.5)
    def getfoodpos(self,mypos,game):
        foodpos=game.foodpos
        if( abs(foodpos[0]-mypos[0]) > abs(foodpos[0]-game.hortiles-mypos[0])):
            foodpos=(foodpos[0]-game.hortiles,foodpos[1])
        elif( abs(foodpos[0]-mypos[0]) > abs(foodpos[0]+game.hortiles-mypos[0])):
            foodpos=(foodpos[0]+game.hortiles,foodpos[1])
        if( abs(foodpos[1]-mypos[1]) > abs(foodpos[1]-game.verttiles-mypos[1])):
            foodpos=(foodpos[0],foodpos[1]-game.verttiles)
        elif( abs(foodpos[1]-mypos[1]) > abs(foodpos[1]+game.verttiles-mypos[1])):
            foodpos=(foodpos[0],foodpos[1]+game.verttiles)
        return foodpos
    def add(self,a,b):
        return a[0]+b[0],a[1]+b[1]
    def UpdateDirection(self,game):
        
        #this is the brain of the snake player
        olddir=self.direction
        position=self.body[0]
        foodpos=self.getfoodpos(position,game)
        #new direction can't be up if current direction is down...and so on
        complement=[(up,down),(down,up),(right,left),(left,right)]
        invaliddir=[x for (x,y) in complement if y==olddir]
        validdir=[dir for dir in directions if not dir in invaliddir]
        
        #validdir=[dir for dir in validdir if not (self.add(position,dir) in obstacles or self.add(position,dir) in game.playerpos)
        
        #keep changing the direction until we get a nice move(i mean move where we don't die)
        newpos=self.add(position,olddir)
        if newpos in game.obstacles or newpos in game.playerpos:
            for dir in validdir:
                newpos=self.add(position,dir)
                if not ( newpos in game.obstacles or newpos in game.playerpos or newpos in game.newplayerheads):
                    olddir=dir
                    break
        shortest=self.pathlen(self.add(position,olddir) , foodpos,game)#length in shortest path
        for dir in validdir:
            newpos=self.add(position,dir)
            newlen=self.pathlen(newpos , foodpos,game)#length in shortest path
            if newlen < shortest:
                if not ( newpos in game.obstacles or newpos in game.playerpos):
                    olddir=dir
                    shortest=newlen
        game.newplayerheads.append(self.add(olddir,position))
        self.direction=olddir

class IntelligentComputerSnake(ComputerSnake):
    directions=[]
    #the heueistic is quite simple. We just calculate the distance of the head from the food
    def heuristic(self,pos,game):
        return abs(pos[0]-game.foodpos[0])+abs(pos[1]-game.foodpos[1])
        #return ((pos[0]-game.foodpos[0])**2 + (pos[1]-game.foodpos[1])**2 )**0.5
    def UpdateDirection(self,game):
        if( (len(self.directions) == 0 ) or (random.randrange(1,15)==2)):#1 out of 5 possibility to update the direction
            self.RefreshPath(game)
        if(len(self.directions)>0):
            self.direction=self.directions.pop() #pop one direction out
        else:
            #failure to get a suitable path. But instead of continuing to same direction, we call
            #the update function of less-intelligent parent snake that will just try to avoid obstacles for now
            super(IntelligentComputerSnake, self).UpdateDirection(game)
        return
        
    def RefreshPath(self,game):
        head=self.body[0]
        position=head;
        g_scores={position:0} #dictionary containing the g scores
        f_scores={position:self.heuristic(position,game)} #initial f score
        camefrom={} #this dictionary gives the node from which any node came from
        closedset=[]
        openset=[position]
        camefrom[position]=position
        while(len(openset)>0):
            #select the position having the lowest f score
            current=openset[0]
            for pos in openset:
                if(f_scores[pos] < f_scores[current]):
                    current=pos
            if(current == game.foodpos):
                self.directions=[]
                while camefrom[current] !=head:
                    newcurrent=camefrom[current]
                    self.directions.append( (current[0]-newcurrent[0],current[1]-newcurrent[1]) )
                    current=newcurrent
                self.directions.append( (current[0]-head[0],current[1]-head[1]) )
                return #found the path
            openset.remove(current)
            closedset.append(current)
            for dir in directions:
                newpos=(dir[0]+current[0],dir[1]+current[1])
                if(newpos[0]>=0 and newpos[0]<=game.hortiles and newpos[1]>=0 and newpos[1]<=game.verttiles):
                    if not(newpos in game.obstacles or newpos in game.playerpos or newpos in game.newplayerheads):
                        tent_g_score=g_scores[current]+1
                        if(newpos in closedset):
                            if(tent_g_score >= g_scores[newpos]):
                                continue
                        tt=tent_g_score+3;
                        tt=tt*100
                        tt=tt%255
                        pygame.draw.rect(game.screen,(tt,tt,tt),(newpos[0]*game.tilesize,newpos[1]*game.tilesize,game.tilesize,game.tilesize),0)
                        
                        if((not newpos in openset) or (tent_g_score < g_scores[newpos])):
                            camefrom[newpos]=current
                            g_scores[newpos]=tent_g_score
                            f_scores[newpos]=self.heuristic(newpos,game)
                            if not newpos in openset:
                                openset.append(newpos)
        return #failure to construct the path
class SnakeGame:
    tilesize=20
    hortiles=40
    verttiles=40
    def __init__(self):
        #create the window and do other stuff
        pygame.init()
        self.screen = pygame.display.set_mode(((self.hortiles+1)*self.tilesize,(self.verttiles+1)*self.tilesize+25))
        pygame.display.set_caption('Python Snake')
        
        #load the font
        self.font = pygame.font.Font(None, 30)
        self.obstacles=[]
        self.obscolor=(0,0,255)
        self.foodcolor=(0,255,255)
        self.foodpos=(0,0)
        self.playercount=0

    def GenerateFood(self):
        if(self.foodpos == (0,0)):
            self.foodpos=random.randrange(1,self.hortiles),random.randrange(1,self.verttiles)
            while (self.foodpos in self.playerpos or self.foodpos in self.obstacles):
                self.foodpos=random.randrange(1,self.hortiles),random.randrange(1,self.verttiles)

    def SetObstacles(self,level):
        for i in range(1,level+1):
            lo=random.randrange(1,self.hortiles),random.randrange(1,self.verttiles) #last obstacle
            self.obstacles.append(lo)
            for j in range(1,random.randint(1,int(level/2))):
                if(random.randint(1,2) == 1):
                    lo=(lo[0]+1,lo[1])
                else:
                    lo=(lo[0],lo[1]+1)
                if( 0<lo[0]<=self.hortiles and 0<lo[1]<=self.verttiles ):
                    self.obstacles.append(lo)
    def setplayers(self,players):
        self.playercount+=len(players)
        self.players=players
    
    def printstatus(self):
        if(len(self.players) >0):
            text = self.font.render(str(len(self.players))+" players playing", 1,(255,255,255))
        else:
            text=self.font.render("All players dead....press c or i for new computer snake or h for new human snake",1,(255,0,0))
        textpos = text.get_rect(centerx=self.screen.get_width()/2,y=(self.verttiles+1)*self.tilesize)
        self.screen.blit(text, textpos)
    
    def UpdatePlayerInfo(self):
        #update where the players are in the board just before updating the logic
        self.playerpos=[]
        for player in self.players:
            self.playerpos+=player.body
        self.newplayerheads=[]
    def start(self):
        clock = pygame.time.Clock()
        count=0
        while True:
            clock.tick(200)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit();exit()
                elif event.type == pygame.KEYDOWN:
                    for player in self.players:
                        player.processkey(event.key)
                    if event.key == K_h:
                        self.players.append(HumanSnake())
                        self.playercount+=1
                    if event.key == K_i:
                        self.players.append(IntelligentComputerSnake(color=(random.randrange(100,200),random.randrange(100,200),random.randrange(100,200))))
                        self.playercount+=1
                    elif event.key == K_c:
                        self.players.append(ComputerSnake(color=(random.randrange(100,200),random.randrange(100,200),random.randrange(100,200))))
                        self.playercount+=1
            count+=1
            self.screen.fill((0,0,0))
            #game logic is updated in the code below
            self.UpdatePlayerInfo()
            
            for player in [a for a in self.players if not a.IsDead]:
                player.UpdateDirection(self) #update game logic (only for alive players)
            for player in [a for a in self.players if  count%a.speed == 0]:
                player.Update(self)
            self.GenerateFood() #generate food if necessary
            #print all the content in the screen
            for player in self.players:
                player.Draw(self.screen,self)
            for obstacle in self.obstacles:
                pygame.draw.rect(self.screen,self.obscolor,(obstacle[0]*self.tilesize,obstacle[1]*self.tilesize,self.tilesize,self.tilesize),0)
            pygame.draw.rect(self.screen,self.foodcolor,(self.foodpos[0]*self.tilesize,self.foodpos[1]*self.tilesize,self.tilesize,self.tilesize),0)
            self.printstatus()
            pygame.display.update()
#start the game
if(__name__ == "__main__"):
    snake=SnakeGame()
    snake.SetObstacles(15) #level of obstacles
    snake.setplayers([  
    #HumanSnake([(12,14)],color=(0,255,0)),
    HumanSnake([(22,34)],color=(255,0,0),upkey=K_w,downkey=K_s,rightkey=K_d,leftkey=K_a),
    #ComputerSnake(color=(255,0,0)),
    IntelligentComputerSnake([(18,18)]*2,down,color=(255,255,0))
    ])
    snake.start()
