"""Various utility functions required for sanity.

Author:
    Sam Gibson <samolivergibson@gmail.com>
"""

TAB_WIDTH = 4
"""int: The width (in spaces) of a printed tab character."""

def print_depth(msg, depth=0):
    """Print a message at a given tab depth."""
    depth_str = " " * TAB_WIDTH * depth
    print(depth_str + msg)