fac = lambda x: 1 if not x else x*fac(x-1)
map_f = lambda f,li: [f(x) for x in li]
filter_f = lambda f,li:[x for x in li if f(x)]
unique = lambda li: list({x:0 for x in li}.keys())
flatten = lambda li: [x for q in li for x in q]
first = lambda x:x[0]
second =  lambda x:x[1]
white = (255,255,255)
black = (0,0,0)
def filter_on(fs,li):
    if not fs:
        return li
    return filter_f(fs[0],filter_on(fs[1:],li))

def histogram(li):
    d = {}
    for x in li:
        d[x] = (d[x] if x in d else 0) +1
    return d
class graph:
    def __init__(self,pos):
        self.pos = pos
        self.vertices = []

    @staticmethod
    def any_cycles(c_pairs):
        nodes = {}
        def node(pos):
            if pos not in nodes:
                nodes[pos] = graph(pos)
            return nodes[pos]

        for start,end in c_pairs:
            s,e = node(start),node(end)
            s.vertices.append(e)
            e.vertices.append(s)

        nodes_visited = {pos:0 for pos in nodes.keys()}
        def find_cycle(current_node,visited=[]):

            nodes_visited[current_node.pos] = 1
            last_pos = visited[-1] if visited else (-3,-3)
            #print(current_node.pos, visited)
            if current_node.pos in visited:
                #print("cycle:", visited,current_node.pos)
                return True
            return any([find_cycle(n,visited+[current_node.pos]) for n in current_node.vertices if n.pos!=last_pos])
            
        while not all(nodes_visited.values()):
            #print("zero in ", nodes_visited.values())
            next_node = nodes[min(nodes_visited.items(),key=second)[0]]
            if find_cycle(next_node):
                return True
            else:
                #print("end",nodes_visited[next_node.pos],next_node.pos)
                v = nodes_visited.values()
                #print(v,0 in v,all(v))
        return False
        
class TrainTracks:
    def __init__(self,size=10):
        self.size = size
        self.display_size = 1000
        self.gd = pygame.display.set_mode((self.display_size,self.display_size))
        self.starting_position = 9
        self.ending_position = 8
        self.col_numbers = [3,5,6,3,2,3,3,5,5,5]
        self.row_numbers = [2,2,2,2,8,5,5,6,4,4]
        
    def make_tracks(self,x,total_tracks,last_was_a_track=False,y=0,left=[],middle=[],right=[]):
        combos = []
        
        #if we are the starting square then something different needs to happen
        if x==0 and y==self.starting_position:
            #if the last was a track, then make it turn into the starting square
            if last_was_a_track:
                return self.make_tracks(x,total_tracks,False,y+1,left+[((x-1,y),(x,y))],middle,right)

            #if we have no tracks left to turn in, then this is not a solution.
            if not total_tracks:
                return []

            #if we have more than one total track, then we can turn in from the left.
            if total_tracks>1:
                combos += self.make_tracks(x,total_tracks-2,True,y+1,left +[((x-1,y),(x,y))],middle + [((x,y),(x,y+1))],right)

            #we can also go straight through.
            combos += self.make_tracks(x,total_tracks-1,False,y+1,left+[((x-1,y),(x,y))],middle,right+[((x,y),(x+1,y))])
            return combos
        
        #if we dont have any tracks left to use then return what we got
        if not total_tracks and not last_was_a_track:
            return [(left,middle,right)] if not (x==0 and y<self.starting_position) else []
        
        #if we have run out of space then return nothing
        if y==self.size:
            return []
        
##        #if we have run into a restricted square then avoid or abort
##        if y in avoid:
##            if lastWasATrack:
##                return []
##            return self.make_tracks(x,total_tracks,False,y+1,left,middle,right)

        #if the last track was a upward track we can either continue the upward trend,turn right or turn left:
        if last_was_a_track:
            #continue upward
            if (y<self.size) and total_tracks>=1:
                combos += self.make_tracks(x,total_tracks-1,True,y+1,left,middle + [((x,y),(x,y+1))],right)

            #go left
            if (x>0):
                combos += self.make_tracks(x,total_tracks,False,y+1,left+[((x-1,y),(x,y))],middle,right)

            #go right
            if (x<self.size-1):
                combos += self.make_tracks(x,total_tracks,False,y+1,left,middle,right+[((x,y),(x+1,y))])

        else:
            #make a new upward track either from the left or the right. a single upward track takes up 2 squares.
            if total_tracks>1:
                if (x>0):
                    combos += self.make_tracks(x,total_tracks-2,True,y+1,left +[((x-1,y),(x,y))],middle + [((x,y),(x,y+1))],right)
                if (x<self.size-1):
                    combos += self.make_tracks(x,total_tracks-2,True,y+1,left,middle + [((x,y),(x,y+1))],right+[((x,y),(x+1,y))])

            #make a track running across from left to right.
            if (0<x<self.size-1):
                combos += self.make_tracks(x,total_tracks-1,False,y+1,left+[((x-1,y),(x,y))],middle,right+[((x,y),(x+1,y))])

            #or simply miss out on this turn
            combos += self.make_tracks(x,total_tracks,False,y+1,left,middle,right)
        return combos

    def all_track_combinations(self):
        make = lambda x: self.make_tracks(x,self.col_numbers[x])if x!=self.ending_position else self.make_tracks(x,self.col_numbers[x]-1,True,middle=[((x,-1),(x,0))])
        return map_f(make, range(self.size))

    def find_all_consistent_combinations(self):
        self.combinations = self.all_track_combinations()
        self.comb_lens = map_f(len,self.combinations)
        for (i,x) in enumerate(self.comb_lens):
            print("row {}, combinations:{}".format(i,x))
        combinable = lambda mid,right: sorted(right[0])==sorted(mid[2])
        def find(x=0,so_far=[]):
            if x==self.size-1:
                return [so_far]
            return flatten([find(x+1,so_far+[i]) for i in range(self.comb_lens[x]) if x==0 or combinable(self.combinations[x][so_far[-1]],self.combinations[x][i])])
        return filter(self.check_rows(),find())
        
    def check_rows(self,pattern,loose=False):
        hist = histogram(map(second,unique([(x_,y) for i,x in enumerate(pattern) for (x_,y) in flatten(flatten(self.combinations[i][x])) if y>=0 and x_>=0])))
        pairs = [(hist[i],self.row_numbers[i]) for i in range(self.size) if i in hist]
        return all([x<=y if loose else x==y for x,y in pairs])
        
##        s =self.display_size//self.size
##        for (x,y) in all_points:
##            pygame.draw.circle(self.gd,black,(s*x + s//2,self.display_size-s*y -s//2),s//8,1)
##        for i in range(3):
##            pygame.event.get()
##            pygame.display.update()
##        input("fin")
##        hist = histogram(map(second,all_points))
####        hist = {i:0 for i in range(self.size)}
####        for i,x in enumerate(pattern):
####            l,m,r = self.combinations[i][x]
####            
####            for (x,y),end in flatten([m,r]):
####                if y<0:
####                    continue
####                hist[y]+=1
####                print("start:{},end:{}, {}:{}".format((x,y),end,y,hist[y]))
##        for i in range(self.size):
##            print("row:{} num:{} hist:{}".format(i,self.row_numbers[i],hist[i] if i in hist else "null"))
##        return all([hist[i]==self.row_numbers[i] for i in range(self.size)])
        
    
    def draw(self,coord_pairs):
        self.gd.fill(white)
        sq_sz = self.display_size//self.size
        for i in range(self.size):
            for j in range(self.size):
                pygame.draw.rect(self.gd,black,(i*sq_sz,j*sq_sz,sq_sz,sq_sz),1)

        def c_pos(pos):
            x,y =pos
            if x==-1:
                x = -0.5
            if y==-1:
                y = -0.5
            return int(sq_sz*x +sq_sz//2),int(self.display_size - (y*sq_sz +sq_sz//2))
            
        for start,end in coord_pairs:
            pygame.draw.line(self.gd,black,c_pos(start), c_pos(end),1)
            
        for i in range(5):
            pygame.display.update()
            pygame.event.get()

    def run(self):
        t = time.perf_counter()
        cs =self.all_track_combinations()
        self.combinations = cs
        self.comb_lens = map_f(len,cs)
        
        current_combs = [[i] for i in range(self.comb_lens[0])]
        combinable = lambda mid,right: sorted(right[0])==sorted(mid[2])
        c_pair = lambda comb: [pair for i,x in enumerate(comb) for m_r in cs[i][x][(1 if i else 0):] for pair in m_r]
        
        for row in range(1,self.size):
            skip = False
            print("len:{},n_combs:{}".format(row,len(current_combs)))
            double_filter = lambda x:self.check_rows(x,row<self.size-1)and not graph.any_cycles(c_pair(x))
            current_combs = filter_f(double_filter,[comb+[i] for comb in current_combs for i in range(self.comb_lens[row]) if combinable(cs[row-1][comb[-1]],cs[row][i])])
##            for q,comb in enumerate(current_combs):
##                if skip:break
##                last_row = self.combinations[row-1][comb[-1]]
##                for (nn,(i,this_row)) in enumerate(filter(lambda x: combinable(last_row,x[1]),map(lambda i:(i,self.combinations[row][i]),range(self.comb_lens[row])))):
##                    #this_row = self.combinations[row][i]
##                    if combinable(last_row,this_row):
##                        new_combs.append(comb+[i])
##                        self.draw(c_pair(comb+[i]))
##                        if nn==c_q[row-1]:#q==c_q[row] and input("i:{},q:{},nn={},row:{},c_q[row]:{}".format(i,q,nn,row,c_q[row])):
##                            #input("correct?")=="y":
##                            new_combs = [comb+[i]]
##                            skip=True
##                            break
##            current_combs = new_combs
        final =current_combs
        print("final: {}, {}".format(len(current_combs),len(final)))
        for comb in final:
            if not graph.any_cycles(c_pair(comb)):
                self.draw(c_pair(comb))
                pygame.event.get()
                pygame.display.update()
                print(time.perf_counter()-t)
                input("fin")
            
        
import pygame, time
pygame.init()
t = TrainTracks()
t.run()
