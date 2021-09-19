Map = lambda f,li : [f(x) for x in li]
Filter = lambda f,li: [x for x in li if f(x)]

class Train:

    def __init__(self,input_manual=False):
        # top left, top right, bottom left, bottom right, vertical, horizontal,None
        self.track_types = ["TL","TR","BL","BR","VV","HH","NN"]
        self.left_accepting = {"HH","TL","BL"}
        self.right_accepting = {"HH","TR","BR"}
        

        #IMAGES
        s = pygame.image.load("Straight.png")
        t = pygame.image.load("Turning.png")
        rot = pygame.transform.rotate
        self.track_images = {"TL":t,"TR":rot(t,270),"BR":rot(t,180),"BL":rot(t,90),"HH":s,"VV":rot(s,90)}
        inp = lambda x:int(input(x))
        #GAME
        if input_manual:
            self.size = inp("size?")
            self.starting_square = inp("Starting Square?")
            self.ending_square = inp("Ending Square?")
            self.col_numbers = [inp("Column {}?".format(1+i)) for i in range(self.size)]
            self.row_numbers = [inp("row {}?".format(1+i)) for i in range(self.size)]
        else:
            self.size = 10
            self.starting_square = 9
            self.ending_square = 8
            self.col_numbers = [3,5,6,3,2,3,3,5,5,5]
            self.row_numbers = [2,2,2,2,8,5,5,6,4,4]

        self.grid = [["NN" for j in range(self.size)] for i in range(self.size)]
        
        #DISPLAY
        self.pixel_size = 71
        self.base_size =self.size*self.pixel_size
        self.pixel = lambda x,y: (x*self.pixel_size,self.base_size-(y+1)*self.pixel_size)
        self.scale = 1
        self.buffer = 100*self.scale
        self.total_size = int(self.base_size*self.scale + 2*self.buffer)
        self.gd = pygame.display.set_mode((self.total_size,self.total_size))

        self.initialise_map()

    def make_track(self,x,y,tracks_left,is_tracking=False,so_far=""):

        # NO TRACKS LEFT
        if not tracks_left:
            #MUST CONTAIN STARTING SQUARE
            if x==0 and y<=self.starting_square or is_tracking:
                return []
            
            return [so_far + "".join(["NN" for i in range(self.size-y)])]

        combos = []

        #GONE TOO FAR
        if y==self.size:
            return []

        #ON LEFT SIDE, WITH STARTING SQUARE
        if x==0 and y==self.starting_square:

            #MAKE THE TRACK GO INTO THE START
            if is_tracking:
                return self.make_track(x,y+1,tracks_left-1,False,so_far+"BL")

            #HORIZONTAL TRACK
            combos+= self.make_track(x,y+1,tracks_left-1,False,so_far+"HH")

            #LEFT TRACK UPWARDS
            combos+= self.make_track(x,y+1,tracks_left-1,True,so_far+"TL")

            return combos

        #CONTINUING A TRACK
        if is_tracking:

            #VERTICAL TRACK CONTINUING
            combos+=self.make_track(x,y+1,tracks_left-1,True,so_far+"VV")

            if x>0:
                #TURNING LEFT
                combos+=self.make_track(x,y+1,tracks_left-1,False,so_far+"BL")

            if x<self.size-1:
                #TURNING RIGHT
                combos+=self.make_track(x,y+1,tracks_left-1,False,so_far+"BR")

        else:
            if x>0:
                #IN FROM THE LEFT
                combos+=self.make_track(x,y+1,tracks_left-1,True,so_far+"TL")

                if x<self.size-1:
                    #HORIZONTAL TRACK
                    combos+=self.make_track(x,y+1,tracks_left-1,False,so_far+"HH")

            if x<self.size-1:
                #IN FROM THE RIGHT
                combos+=self.make_track(x,y+1,tracks_left-1,True,so_far+"TR")
                    
                    
                    
                    
            #DO NOTHING
            combos+=self.make_track(x,y+1,tracks_left,False,so_far+"NN")
        return combos

    @staticmethod
    def to_list(string):
        if not string:
            return []
        return [string[:2]] +Train.to_list(string[2:])

    def initialise_map(self):
        while True:
            self.draw()
            pygame.event.get()
            l,m,r = pygame.mouse.get_pressed()
            if r:
                return
            if l:
                x,y = pygame.mouse.get_pos()
                box_size = self.pixel_size*self.scale
                i,j = int((x-self.buffer)/box_size),int((self.total_size-self.buffer-y)/box_size)

                if 0<=i<self.size and 0<=j<self.size:
                    next_val = self.track_types[(self.track_types.index(self.grid[i][j])+1)%7]
                    self.grid[i][j] = next_val
                    time.sleep(1/10)
                
        
    def draw(self,grid = None):
        if not grid:
            grid = self.grid

        gd = pygame.Surface((self.base_size,self.base_size))
        gd.fill(white)
        for i in range(self.size):
            for j in range(self.size):
                val = grid[i][j]
                if val!="NN":
                    gd.blit(self.track_images[val],self.pixel(i,j))
                pygame.draw.rect(gd,black,(*self.pixel(i,j),self.pixel_size,self.pixel_size),1)

        #scale up
        new_gd = pygame.transform.rotozoom(gd,0,self.scale)
        self.gd.fill(white)
        self.gd.blit(new_gd,(self.buffer,self.buffer))
        pygame.draw.rect(self.gd,black,(self.buffer,self.buffer,*new_gd.get_size()),15)
        pygame.display.update()
        pygame.event.get()

    def run(self):

        match = lambda x: (lambda track: all([track[i]==self.grid[x][i] or self.grid[x][i]=="NN" for i in range(self.size)]))
        get_grid = lambda combo: [self.cols[x][i][:] for x,i in enumerate(combo)] +[self.grid[j][:] for j in range(x+1,self.size)]
        valid_trail = lambda grid : self.trail(grid,0,self.starting_square)==sum(self.col_numbers)
        
        
        self.cols = [Filter(match(x),Map(Train.to_list,self.make_track(x,0,self.col_numbers[x],x==self.ending_square))) for x in range(self.size)]
        print(" ".join([str(len(x)) for x in self.cols]))
        
        combos = [[i] for i in range(len(self.cols[0]))]
        
        for x in range(1,self.size):
            print("x:{}, len:{}".format(x,len(combos)))

            combos = Filter(lambda combo:self.valid_rows(get_grid(combo),lambda x,y: x<=y),
                            [combo+[i] for combo in combos for i,track in enumerate(self.cols[x]) if self.is_consistent(self.cols[x-1][combo[-1]],track)])
        
        
        
        print("before:",len(combos))
        combos = [x for x in combos if valid_trail(get_grid(x)) and self.valid_rows(get_grid(x))]
        print("after:",len(combos))
        self.draw(get_grid(combos[0]))
        for i in range(6):
            pygame.display.update()
            pygame.event.get()
        
        
    def is_consistent(self,train_a,train_b):
        
        for track_a,track_b in zip(train_a,train_b):
            one = track_a in self.right_accepting
            two = track_b in self.left_accepting
            if ( one and not two) or (two and not one):
                return False
        return True

    
    def trail(self,grid,x,y,horizontal=True,vector=1,number=0):
        if x==self.ending_square and y==0:
            return number+1
        
        if grid[x][y]=="HH":
            return self.trail(grid,x+vector,y,True,vector,number+1)

        if grid[x][y]=="VV":
            return self.trail(grid,x,y+vector,False,vector,number+1)

        if horizontal:
            
            if grid[x][y][0]=="B":
                return self.trail(grid, x, y-1, False,-1,number+1)
            
            return self.trail(grid, x, y+1, False,1,number+1)

        if grid[x][y][1]=="L":
            return self.trail(grid,x-1,y,True,-1,number+1)
        
        return self.trail(grid,x+1,y,True,1,number+1)

    def valid_rows(self,grid,eq=(lambda x,y:x==y)):
##        all_res = True
##        for j in range(self.size):
##            res = 0
##            for i in range(self.size):
##                try:
##                    res += 1 if grid[i][j]!="NN" else 0
##                except:
##                    print(i,j)
##            all_res = all_res and eq(res,self.row_numbers[j])
##        return all_res
        return all([eq(sum([grid[i][j]!="NN" for i in range(len(grid))]),self.row_numbers[j]) for j in range(len(grid[0]))])

import pygame,time
black = (0,0,0)
white = (255,255,255)
pygame.init()

Train().run()
