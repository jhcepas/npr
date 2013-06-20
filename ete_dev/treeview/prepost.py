from ete2 import Tree
import sys
import time
class NodeInfo(dict):
    def __init__(self):
        dict.__init__(self,
                      {"x": 0.0,
                       "y": 0.0,
                       "fullw": 0.0,
                       "fullh": 0.0,
                       "nodew": 0.0,
                       "nodeh": 0.0,
                       "radius": 0.0,
                       "rotation": 0.0,
                       "widths": [0, 0, 0, 0, 0, 0],
                       "height": [0, 0, 0, 0, 0, 0],
                       "centerx": 0.0, 
                       "centery": 0.0, 
                       "angle_start": 0.0,
                       "angle_end": 0.0})


def prepostorder(tree):
    x = 0
    to_visit = [tree]
    posorder = False
    while to_visit:
        node = to_visit.pop(-1)
        try:
            flag, node = node
        except ValueError:
            # PREORDER
            if _leaf(node):
                # LEAVES
                #node.status = True
                yield 1#(node.name, x, "LEAF")    
            else:
                #node.status = True
                yield 1#(node.name, x, "PREORDER")
                #x += node.dist
                #  ADD CHILDREN
                to_visit.extend(reversed(node.children + [[1, node]]))
        else:
            #POSTORDER
            yield 1#(node.name, x, "POSTORDER")    
            #x -= node.dist
        
            
_leaf = lambda x: len(x.children) == 0

t = Tree()
t1 = time.time()
t.populate(50000)
print time.time()-t1, "ITER"
sys.stdout.flush()
t1 = time.time()
for x in prepostorder(t):
    pass
#a = [x for x in prepostorder(t)]
print time.time()-t1
raw_input("DONE")
#t =  Tree("(((a,b)e1,c)e2, d) ;", format=1)
#print t
#a = prepostorder(t)
#while a:
#    print a.next()


            
