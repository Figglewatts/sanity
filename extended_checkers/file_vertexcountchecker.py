"""File vertex count checker. Loads an OBJ file and checks the vertex count.

Parameters:
    min_verts (int): The minimum number of vertices to be acceptable.
        Set to -1 to disable.
    max_verts (int): The maximum number of vertices to be acceptable.
        Set to -1 to disable.
"""

import pywavefront
from os.path import splitext

DEFAULT_MIN_VERTS = -1
DEFAULT_MAX_VERTS = -1
ACCEPTABLE_EXTENSION = ".obj"

def check(path, params):
    min_verts = params.get("min_verts", DEFAULT_MIN_VERTS)
    max_verts = params.get("max_verts", DEFAULT_MAX_VERTS)
    
    _, ext = splitext(path)
    if ext.lower() != ACCEPTABLE_EXTENSION:
        return False, f"file '{path}' was not an OBJ file"
    
    scene = pywavefront.Wavefront(path, create_materials=True)
    vert_count = len(scene.vertices)
    
    if min_verts != -1:
        if vert_count < min_verts:
            return False, f"file '{path}' vertex count '{vert_count}' less than min count '{min_verts}'"

    if max_verts != -1:
        if vert_count > max_verts:
            return False, f"file '{path}' vertex count '{vert_count}' exceeded max count '{min_verts}'"

    return True, ""
