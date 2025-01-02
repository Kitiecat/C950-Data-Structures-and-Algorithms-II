


class Node:
    def __init__(self,value):
        self.height = 1
    
        self.left = None
        self.right = None
        self.parent = None
        self.value = value
        pass

class AVLTree:

    # An AVL tree is a BST (Binary Search Tree) that is balanced using a balance factor based algorithm 
    # It follows the same rules as a BST (for any node left < node <= right) but also includes a height value
    # using the height value a balance factor is calculated, any given node must have a balance factor of -1, 0, or 1 
    # when inserting or removing from a AVL tree 
    def __init__(self):
        self.root = Node(None)
        print("Creating tree with root: " + str(self.root))
        pass

    # calculates the correct height for given node

    def UpdateHeight(node): 
        leftHeight = -1
        rightHeight = -1
        if node.left is not None:
            leftHeight = node.left.height
        
        if node.right is not None:
            rightHeight = node.right.height
        
        node.height= max(leftHeight, rightHeight) + 1
    
    # sets a child of a parent node to a given node, using whichChild to know which child to update

    def SetChild(parent, whichChild, child): 
        if whichChild != "left" and whichChild != "right":
            return False
        if whichChild == "left":
            parent.left = child
        else:
            parent.right = child
        if child is not None:
            child.parent = parent
        
        AVLTree.UpdateHeight(parent)
        return True
    
    #replaces the child of a given node
    
    def ReplaceChild(parent: Node, currentChild, newChild):
        if parent.left == currentChild:
            return AVLTree.SetChild(parent, "left", newChild)
        elif parent.right == currentChild:
            return AVLTree.SetChild(parent, "right", newChild)
        return False
    
    #calculates balance factor (height left - height right) null nodes are counted as -1 balance factor

    def GetBalance(node):
        leftHeight = -1
        if node.left is not None:
            print("Height is: " + str(node.left.value) + " " + str(node.left.height))
            leftHeight = node.left.height
        rightHeight = -1
        if node.right is not None:
            print("Height is: " + str(node.right.value) + " " + str(node.right.height))
            rightHeight = node.right.height
        # print(leftHeight-rightHeight)
        return leftHeight - rightHeight
    
    # takes a given node (and the tree its from in the event its child becomes the root node) and rotates it right
    # its left node takes its place in the parent node, it becomes the right child of its current left child, it swap right nodes with the former left child.
    def RotateRight(self, node):
        # print("Rotating right: " + str(node.value) + " " + str(node.left) + str(node.right))
        
        if node.left is None:

            leftRightChild = node
            print("no left child")
        else:
            print(str(node.left))
            leftRightChild = node.left.right
        if node.parent is not None:
            AVLTree.ReplaceChild(node.parent, node, node.left)
        else:
            self.root = node.left
            self.root.parent = None
        AVLTree.SetChild(node.left, "right", node)
        AVLTree.SetChild(node, "left", leftRightChild)
    
    #same as above but swap left for right and right for left
    def RotateLeft(self, node):
        print("Rotating left: " + str(node.value))
        if node.right is not None:
            rightLeftChild = node.right.left
        if node.parent:
            AVLTree.ReplaceChild(node.parent, node.right)
        else:
            self.root = node.right
            self.root.parent = None
        AVLTree.SetChild(node.right, "left", node)
        AVLTree.SetChild(node, "right", rightLeftChild)

    def Rebalance(self, node):
        AVLTree.UpdateHeight(node)
        print ("rebalanacing: " + str(node.value))
        if AVLTree.GetBalance(node) == -2:
            print ("right rotate needed: " + str(node.value) + str(AVLTree.GetBalance(node)))
            printTree(node.parent)
            if AVLTree.GetBalance(node.right) == 1:
                print(str(node.right.value) + str(AVLTree.GetBalance(node.right)))
                print ("rotating twice: " + str(node.right))
                AVLTree.RotateRight(self, node.right)
            return AVLTree.RotateRight(self, node)
        elif AVLTree.GetBalance(node) == 2:
            print ("left rotate needed: " + str(node.value))
            if AVLTree.GetBalance(node.left) == -1:
                print ("rotating twice: " + str(node.left))
                AVLTree.RotateLeft(self,node.left)
            return AVLTree.RotateLeft(self, node)
        return node
    
    def Insert(self,node):
        # print("The root is: " + str(self.root))
        # print(str(node))
        if not self.root.value:
            # print("Got here")
            self.root = node
            node.parent = None
        else:
            print("The root is: " + str(self.root.value))
            cur = self.root
            print("Working from: " + str(cur.value))
            while cur is not None:
                
                if node.value < cur.value:
                    if cur.left is None:
                        # print("got here")
                        AVLTree.SetChild(cur, "left", node)
                        node.parent = cur
                        cur = None
                    else:
                        cur = cur.left
                elif node.value >= cur.value:
                    if cur.right is None:
                        # print("got here 2")
                        cur.right = node
                        node.parent = cur
                        print(node.parent.value)
                        cur = None
                    else:
                        cur = cur.right
        node = node.parent
        while node is not None:
            print(node.value)
            AVLTree.Rebalance(self, node)
            node = node.parent

def printTree(node: Node):
    if node.value is not None:
        if node.parent is not None:
            print(str(node.value) + " parent is " + str(node.parent.value) )
        else:
            print(str(node.value))
    if node is not None:
        if node.left is not None:
            printTree(node.left)
        if node.right is not None:
            printTree(node.right)
    

values = [14,13,26,82,96,100]
# node = Node(1)

tree = AVLTree()

for v in values:
    node = Node(v)
    print ("inserting " + str(node.value))
    tree.Insert(node)
    printTree(tree.root)
    


