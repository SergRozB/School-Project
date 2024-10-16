class TreeNode():
    # Binary tree to more efficiently search for cells
    def __init__(self, value, pos):
        self.left = None
        self.right = None
        self.value = value
        self.pos = pos

    def Insert(self, value, pos):
        if value < self.value:
            if self.left is None:
                self.left = TreeNode(value, pos)
            else:
                self.left.Insert(value, pos)
        else:
            if self.right is None:
                self.right = TreeNode(value, pos)
            else:
                self.right.Insert(value, pos)

    def InorderTraversal(self):
        if self.left:
            self.left.InorderTraversal()
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