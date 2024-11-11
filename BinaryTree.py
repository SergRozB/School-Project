class TreeNode():
    # Binary tree to more efficiently search for cells
    def __init__(self, value, pos, parent, direction):
        self.left = None
        self.right = None
        self.value = value
        self.pos = pos
        self.parent = parent
        self.direction = direction

    def Insert(self, value, pos):
        if value < self.value:
            if self.left is None:
                self.left = TreeNode(value, pos, self, "L")
            else:
                self.left.Insert(value, pos)
        else:
            if self.right is None:
                self.right = TreeNode(value, pos, self, "R")
            else:
                self.right.Insert(value, pos)

    def InorderTraversal(self):
        if self.left:
            self.left.InorderTraversal()
        if self.left != None and self.right != None:
            print(self.value, self.pos, "|| CHILDREN:, left:", self.left.value, self.left.pos, "| right:", self.right.value, self.right.pos)
        if self.left != None and self.right == None:
            print(self.value, self.pos, "|| CHILDREN:, left:", self.left.value, self.left.pos)
        if self.left == None and self.right != None:
            print(self.value, self.pos, "|| CHILDREN:, right:", self.right.value, self.right.pos)
        elif self.left == None and self.right == None:
            print(self.value, self.pos)
        if self.right:
            self.right.InorderTraversal()

    def FindLowest(self):
        # Finds the lowest value from the current node, which 
        # may not necessarily be the lowest unless called from
        # the root node
        if self.left is not None:
            return self.left.FindLowest()
        elif self.left is None:
            return [self.value, self.pos]
        
    def FindHighest(self):
        # Finds the highest value from the current node, which 
        # may not necessarily be the highest unless called from
        # the root node
        if self.right is not None:
            return self.right.FindHighest()
        elif self.right is None:
            return self
    
    def Search(self, value, pos):
        # Finds given node
        print("pos in search:", self.pos)
        if self.pos == pos:
            return self
        if value < self.value:
            return self.left.Search(value, pos)
        else:
            return self.right.Search(value, pos)
                
    def Delete(self, value, pos, root):
        if value < self.value:
            self.left.Delete(value, pos, root)
        elif value >= self.value and pos != self.pos:
            self.right.Delete(value, pos, root)
        else:
            direction = self.direction
            parent = self.parent
            if self.left is None:
                if self.right != None:
                    self.value, self.pos, self.left, self.right = self.right.value, self.right.pos, self.right.left, self.right.right
                    if self.left != None:
                        self.left.parent = self
                    if self.right != None:
                        self.right.parent = self
                else:
                    self = self.right
                    if direction == "L":
                        parent.left = self
                    else:
                        parent.right = self
                return None
                
            elif self.right is None:
                self.value, self.pos, self.left, self.right = self.left.value, self.left.pos, self.left.left, self.left.right
                self.left.parent = self
                self.right.parent = self
                if direction == "L":
                    parent.left = self
                else:
                    parent.right = self
                return None
            else:
                self.value, self.pos = self.left.InOrderSuccessor()
                self.left.Delete(self.value, self.pos, root)
                return None
        
        #return self
    
    def InOrderSuccessor(self):
        maximum = self.value
        while self.right is not None:
            maximum = self.right.value
            return self.right.InOrderSuccessor()
        return (maximum, self.pos)
        
