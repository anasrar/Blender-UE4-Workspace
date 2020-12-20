from math import (sin, cos, radians, pi as PI)
import bmesh, mathutils

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

def circle(segments = 3, radius = 1 , loc = 0):
    segments = int(segments)
    bm = bmesh.new()

    # create circle
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        radius=radius,
        segments=clamp(segments, 3, 32)
    )

    # rotate 90 degree on x axis
    bmesh.ops.rotate(
        bm,
        verts=bm.verts,
        cent=(0.0, 0.0, 0.0),
        matrix=mathutils.Matrix.Rotation(radians(90.0), 3, "X")
    )

    # move on y axis
    bmesh.ops.translate(
        bm,
        verts=bm.verts,
        vec=(0, loc, 0)
    )

    # get vertices and edges
    listVertices = [x for x in bm.verts]
    listEdges = [(listVertices.index(x.verts[0]), listVertices.index(x.verts[1])) for x in bm.edges]
    listVertices = [x.co.to_tuple() for x in bm.verts]

    bm.free()
    return [listVertices, listEdges, []]

def rectangle(wide = 1, length = 1, yPos = 0):
    v0 = ((wide/2), yPos, (length/2))
    v1 = ((wide/2), yPos, -(length/2))
    v3 = (-(wide/2), yPos, -(length/2))
    v4 = (-(wide/2), yPos, (length/2))

    listVertices = [v0, v1, v3, v4]
    listEdges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    return [listVertices, listEdges, []]

def block(wide = 1, length = 1, yPosStart = 0, yPosEnd = 1):
    v0 = ((wide/2), yPosStart, (length/2))
    v1 = ((wide/2), yPosStart, -(length/2))
    v2 = (-(wide/2), yPosStart, -(length/2))
    v3 = (-(wide/2), yPosStart, (length/2))

    v4 = ((wide/2), yPosEnd, (length/2))
    v5 = ((wide/2), yPosEnd, -(length/2))
    v6 = (-(wide/2), yPosEnd, -(length/2))
    v7 = (-(wide/2), yPosEnd, (length/2))

    listVertices = [v0, v1, v2, v3, v4, v5, v6, v7]
    listEdges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    return [listVertices, listEdges, []]

def sphere(u_segments = 3, v_segments=3, diameter = 1):
    bm = bmesh.new()

    # create sphere
    bmesh.ops.create_uvsphere(
        bm,
        u_segments = u_segments,
        v_segments = v_segments,
        diameter = diameter,
    )

    # rotate 90 degree on x axis
    bmesh.ops.rotate(
        bm,
        verts=bm.verts,
        cent=(0.0, 0.0, 0.0),
        matrix=mathutils.Matrix.Rotation(radians(90.0), 3, "X")
    )

    # get vertices and edges
    listVertices = [x for x in bm.verts]
    listEdges = [(listVertices.index(x.verts[0]), listVertices.index(x.verts[1])) for x in bm.edges]
    listVertices = [x.co.to_tuple() for x in bm.verts]

    bm.free()
    return [listVertices, listEdges, []]

def controlRotation(segments = 8, radius = 1 , loc = 0, flip = False):
    bm = bmesh.new()

    # create circle
    circle1 = bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        radius=radius * 0.75,
        segments=clamp(segments, 3, 32)
    )

    # create second circle
    circle2 = bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        radius=radius,
        segments=clamp(segments, 3, 32)
    )

    # rotate 90 degree on x axis
    bmesh.ops.rotate(
        bm,
        verts=bm.verts,
        cent=(0.0, 0.0, 0.0),
        matrix=mathutils.Matrix.Rotation(radians(90.0), 3, "X")
    )

    # move on y axis
    bmesh.ops.translate(
        bm,
        verts=circle2["verts"],
        vec=(0, -0.5 if flip else 0.5, 0)
    )

    # move on y axis
    bmesh.ops.translate(
        bm,
        verts=bm.verts,
        vec=(0, loc, 0)
    )

    # get vertices and edges
    listVertices = [x for x in bm.verts]
    listEdges = [(listVertices.index(x.verts[0]), listVertices.index(x.verts[1])) for x in bm.edges]
    listVertices = [x.co.to_tuple() for x in bm.verts]

    bm.free()
    return [listVertices, listEdges, []]

def floor(scaleX = 1, scaleY = 1):
    bm = bmesh.new()

    # square vertex
    v1 = bm.verts.new((10.0, 10.0, 0.0))
    v2 = bm.verts.new((10.0, -10.0, 0.0))
    v3 = bm.verts.new((-10.0, -10.0, 0.0))
    v4 = bm.verts.new((-10.0, 10.0, 0.0))

    # create edge from vertices
    for edge in [(v1, v2), (v2, v3), (v3, v4), (v4, v1), (v1, v3), (v2, v4)]:
        bm.edges.new(edge)

    # create circle
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        radius=5,
        segments=8
    )

    # scale
    bmesh.ops.scale(
        bm,
        verts=bm.verts,
        vec=(scaleX, scaleY, 1)
    )

    # get vertices and edges
    listVertices = [x for x in bm.verts]
    listEdges = [(listVertices.index(x.verts[0]), listVertices.index(x.verts[1])) for x in bm.edges]
    listVertices = [x.co.to_tuple() for x in bm.verts]

    bm.free()
    return [listVertices, listEdges, []]

def root(segments = 5, radius = 50):
    bm = bmesh.new()

    # create circle
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        radius=radius,
        segments=segments
    )

    # rotate 180 degree on z axis
    bmesh.ops.rotate(
        bm,
        verts=bm.verts,
        cent=(0.0, 0.0, 0.0),
        matrix=mathutils.Matrix.Rotation(radians(180), 3, "Z")
    )

    # get vertices and edges
    listVertices = [x for x in bm.verts]
    listEdges = [(listVertices.index(x.verts[0]), listVertices.index(x.verts[1])) for x in bm.edges]
    listVertices = [x.co.to_tuple() for x in bm.verts]

    bm.free()
    return [listVertices, listEdges, []]

def controlRotationFinger(yPos = 3, scaleX = 1, scaleZ = 1):
    bm = bmesh.new()

    # arrow vertex
    v1 = bm.verts.new((1.0, yPos + 0.25, 0.0))
    v2 = bm.verts.new((0.0, yPos, 2.0))
    v3 = bm.verts.new((-1.0, yPos + 0.25, 0.0))
    v4 = bm.verts.new((0.0, yPos, -2.0))

    # create edge from vertices
    for edge in [(v1, v2), (v2, v3), (v3, v4), (v4, v1)]:
        bm.edges.new(edge)

    # scale
    bmesh.ops.scale(
        bm,
        verts=bm.verts,
        vec=(scaleX, 1, scaleZ)
    )

    # get vertices and edges
    listVertices = [x for x in bm.verts]
    listEdges = [(listVertices.index(x.verts[0]), listVertices.index(x.verts[1])) for x in bm.edges]
    listVertices = [x.co.to_tuple() for x in bm.verts]

    bm.free()
    return [listVertices, listEdges, []]

line = [
    [(0, 0, 0), (0, 1, 0)], [(0, 1)], []
]