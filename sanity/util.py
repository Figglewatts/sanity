TAB_WIDTH = 4

def print_depth(msg, depth=0):
    depth_str = " " * TAB_WIDTH * depth
    print(depth_str + msg)