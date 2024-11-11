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
                
    def Delete(self, value, pos):
        print("current:", self.value)
        if value < self.value:
            self.left.Delete(value, pos)
        elif value >= self.value and pos != self.pos:
            self.right.Delete(value, pos)
        else:
            if self.left is None:
                if self.direction == "R":
                    self.parent.right = self.right
                elif self.direction == "L":
                    self.parent.left = self.right
                self = self.right
                try:
                    print("self val:", self.value)
                except:
                    pass
                
            elif self.right is None:
                if self.direction == "R":
                    self.parent.right = self.left
                elif self.direction == "L":
                    self.parent.left = self.left
                self = self.left
            else:
                self.value, self.pos = self.left.InOrderSuccessor()
                self.left.Delete(self.value, self.pos)
        
        return self
    
    def InOrderSuccessor(self):
        maximum = self.value
        while self.right is not None:
            maximum = self.right.value
            return self.right.InOrderSuccessor()
        return (maximum, self.pos)
        
root = TreeNode(198, (10, 5), None, None)
root.Insert(192, (12,6))
root.Insert(206, (12,5))
root.Insert(186, (12, 7))
root.Insert(178, (10, 7))
root.Insert(184, (10, 6))
root.Insert(198, (10, 5))
root.Insert(1176, (12, 8))
root.Insert(1168, (10,8))
root.InorderTraversal()
root.Delete(178, (10,7))
root.InorderTraversal()
