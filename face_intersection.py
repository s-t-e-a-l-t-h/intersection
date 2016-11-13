import numpy as np
import Plot as Plt
try:
    from edge_intersection import edge_intersection_2d as ei
except:
    print("edge_intersection.py is missing")


# thanks: http://blackpawn.com/texts/pointinpoly/default.html

# A common way to check if a point is in a triangle is to find the vectors connecting the point to each of the
# triangle's three vertices and sum the angles between those vectors. If the sum of the angles is 2*pi then the
# point is inside the triangle, otherwise it is not. It works, but it is very slow. This text explains a faster
# and much easier method.
#
#       /-->x p
# A x--------------------->x B
#      \->x p'
#
#
#
#           x C

# If you take the cross product of [B-A] and [p-A], you'll get a vector pointing out of the screen. On the other
# hand, if you take the cross product of [B-A] and [p'-A] you'll get a vector pointing into the screen. Ah ha!
# In fact if you cross [B-A] with the vector from A to any point above the line AB, the resulting vector points
# out of the screen while using any point below AB yields a vector pointing into the screen. So all we need to do
# to distinguish which side of a line a point lies on is take a cross product.

# The only question remaining is: how do we know what direction the cross product should point in? Because the triangle
# can be oriented in any way in 3d-space, there isn't some set value we can compare with. Instead what we need is
# a reference point - a point that we know is on a certain side of the line. For our triangle, this is just the third
# point C.

#  So, any point p where [B-A] cross [p-A] does not point in the same direction as [B-A] cross [C-A] isn't inside
# the triangle. If the cross products do point in the same direction, then we need to test p with the other lines
# as well. If the point was on the same side of AB as C and is also on the same side of BC as A and on the same side
# of CA as B, then it is in the triangle.

# Implementing this is a breeze. We'll make a function that tells us if two points are on the same side of a line
# and have the actual point-in-triangle function call this for each edge.

# /* Check whether p1 and p2 lie on the same side of line ab */
def same_side(p1, p2, a, b):
    return True if side(p1, p2, a, b) >= 0 else False


def point_in_triangle(p, a, b, c):
    return True if same_side(p, a, b, c) and same_side(p, b, a, c) and same_side(p, c, a, b) else False


def side(p1, p2, a, b):
    # z1 = (b[0] - a[0]) * (p1[1] - a[1]) - (p1[0] - a[0]) * (b[1] - a[1])
    # z2 = (b[0] - a[0]) * (p2[1] - a[1]) - (p2[0] - a[0]) * (b[1] - a[1])
    # return z1 * z2
    p1, p2, a, b = np.array(p1), np.array(p2), np.array(a), np.array(b)
    cp1 = np.cross(b - a, p1 - a)
    cp2 = np.cross(b - a, p2 - a)
    return np.dot(cp1, cp2)


# check whether segment p0p1 intersects with triangle t0 t1 t2
def segment_intersection_2d(p0, p1, t0, t1, t2):
    # check whether segment is outside one of the three half-planes delimited by the triangle
    f1, f2, f3 = side(p0, t2, t0, t1), side(p1, t2, t0, t1), side(p0, t0, t1, t2)
    f4, f5, f6 = side(p1, t0, t1, t2), side(p0, t1, t2, t0), side(p1, t1, t2, t0)

    # check whether triangle is totally inside one of the two half-planes delimited by the segment
    f7, f8 = side(t0, t1, p0, p1), side(t1, t2, p0, p1)
    # print(f1, f2, f3, f4, f5, f6, f7, f8)

    # if segment is strictly outside triangle, or triangle is strictly apart from the line, we're not intersecting
    if (f1 < 0 and f2 < 0) or (f3 < 0 and f4 < 0) or (f5 < 0 and f6 < 0) or (f7 > 0 and f8 > 0):
        return 0, "NOT_INTERSECTING"

    # if segment is aligned with one of the edges, we're overlapping
    if (f1 == 0 and f2 == 0) or (f3 == 0 and f4 == 0) or (f5 == 0 and f6 == 0):
        return 2, "OVERLAPPING"

    # if segment is outside but not strictly (also ==), or triangle is apart but not strictly, we're touching
    if (f1 <= 0 and f2 <= 0) or (f3 <= 0 and f4 <= 0) or (f5 <= 0 and f6 <= 0) or (f7 >= 0 and f8 >= 0):
        return -1, "TOUCHING"

    # if both segment points are strictly inside the triangle, we are not intersecting either
    if f1 > 0 and f2 > 0 and f3 > 0 and f4 > 0 and f5 > 0 and f6 > 0:
        return 0, "NOT_INTERSECTING"

    # otherwise we're intersecting with at least one edge
    return 1, "INTERSECTING"


def face_intersection_2d(f0, f1):
    # test each side (face segment) on intersection
    edge0 = segment_intersection_2d(p0=f0[0], p1=f0[1], t0=f1[0], t1=f1[1], t2=f1[2])
    edge1 = segment_intersection_2d(p0=f0[1], p1=f0[2], t0=f1[0], t1=f1[1], t2=f1[2])
    edge2 = segment_intersection_2d(p0=f0[2], p1=f0[0], t0=f1[0], t1=f1[1], t2=f1[2])
    # print(edge0, edge1, edge2)

    # if segments are outside of triangle
    if edge0[0] == 0 and edge1[0] == 0 and edge2[0] == 0:
        # test if triangle is not inside of other because if function segment_intersection_2d() return 0
        # because edge is not intersection triangle, but it is inside
        face = [f0, f1]
        for idx in range(-1, 1):
            f, inside = face[idx], 0
            for vertice in f:
                inside += 1 if point_in_triangle(vertice, face[idx + 1][0], face[idx + 1][1], face[idx + 1][2]) else 0
            if inside == 3:
                return 1, "INTERSECTING"
        return 0, "NOT_INTERSECTING"

    # if one edge is overllaping
    if (edge0[0] == 2 and edge1[0] == -1 and edge2[0] == 2) or (
        edge0[0] == 2 and edge1[0] == 2 and edge2[0] == -1) or (
        edge0[0] == -1 and edge1[0] == 2 and edge2[0] == 2):

        intersection = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                edge_intersection = ei(f0[i], f0[i + 1], f1[j], f1[j + 1])[1]
                if edge_intersection is True:
                    intersection += 1
        if intersection < 6:
            return 2, "EDGE_OVERLAPPING"

    if (edge0[0] == -1 and edge1[0] == 2 and edge2[0] == -1) or (
        edge0[0] == -1 and edge1[0] == -1 and edge2[0] == 2) or (
        edge0[0] == 2 and edge1[0] == -1 and edge2[0] == -1):
        return 2, "EDGE_OVERLAPPING"

    if ((edge0[0] == -1 and edge1[0] == 0 and edge2[0] == 2) or (
         edge0[0] == -1 and edge1[0] == 2 and edge2[0] == 0) or (
         edge0[0] == 0 and edge1[0] == -1 and edge2[0] == 2) or (
         edge0[0] == 0 and edge1[0] == 2 and edge2[0] == -1) or (
         edge0[0] == 2 and edge1[0] == -1 and edge2[0] == 0) or (
         edge0[0] == 2 and edge1[0] == 0 and edge2[0] == -1)) or (

        (edge0[0] == -1 and edge1[0] == 0 and edge2[0] == -1) or (
         edge0[0] == 0 and edge1[0] == -1 and edge2[0] == -1) or (
         edge0[0] == -1 and edge1[0] == -1 and edge2[0] == 0)):

        return -1, "TOUCHING"

    return 1, "INTERSECTING"


# # not intersection example:
    # faces = [[[0.0, 0.5, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 0.0, 0.0],
    #           [1.0, 0.4, 0.0],
    #           [0.0, -.7, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # not intersection example:
    # faces = [[[0.0, 0.5, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 0.0, 0.0],
    #           [1.0, 0.3, 0.0],
    #           [0.0, 0.3, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # overllaping example:
    # faces = [[[0.0, 0.5, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 0.0, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 0.5, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # overllaping example:
    # faces = [[[0.0, 0.0, 0.0],
    #           [1.0, 0.0, 0.0],
    #           [0.5, 0.5, 0.0]],
    #          [[0.0, 1.0, 0.0],
    #           [1.0, 1.0, 0.0],
    #           [1.0, 0.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # overllaping example:
    # faces = [[[0.0, 0.0, 0.0],
    #           [1.0, 0.0, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[-1., 1.0, 0.0],
    #           [0.0, 1.0, 0.0],
    #           [0.0, 0.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # touching example
    # faces = [[[0.0, 0.0, 0.0],
    #           [1.0, 0.0, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 0.0, 0.0],
    #           [0.0, -.5, 0.0],
    #           [-.5, -.5, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # touching example
    # faces = [[[0.0, 0.0, 0.0],
    #           [1.0, 0.0, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 0.0, 0.0],
    #           [-.1, -.5, 0.0],
    #           [-.5, -.5, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # touching example
    # faces = [[[0.0, 0.0, 0.0],
    #           [1.0, 0.0, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 0.0, 0.0],
    #           [-.5, 0.0, 0.0],
    #           [-.5, -.5, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # touching example
    # faces = [[[0.0, 0.0, 0.0],
    #           [1.0, 0.0, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.5, -.5, 0.0],
    #           [-.5, 0.5, 0.0],
    #           [-.5, -.5, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # intersection example
    # faces = [[[0.0, 0.5, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 2.0, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 0.5, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # intersection example
    # faces = [[[0.0, 0.5, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 1.0, 0.0]],
    #          [[0.0, 0.5, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.0, 1.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # # intersection example
    # faces = [[[0.0, 0.0, 0.0],
    #           [2.0, 0.0, 0.0],
    #           [0.0, 2.0, 0.0]],
    #          [[0.0, 0.0, 0.0],
    #           [1.0, 0.0, 0.0],
    #           [0.0, 1.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # intersection example
    # faces = [[[0.0, 0.0, 0.0],
    #           [2.0, 0.0, 0.0],
    #           [0.0, 2.0, 0.0]],
    #          [[0.5, .25, 0.0],
    #           [1.0, 0.5, 0.0],
    #           [0.5, 1.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    #
    # # intersection example
    # faces = [[[0.0, 0.0, 0.0],
    #           [2.0, 0.0, 0.0],
    #           [0.0, 2.0, 0.0]],
    #          [[0.5, -.5, 0.0],
    #           [1.0, -.5, 0.0],
    #           [0.5, 1.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # intersection example
    # faces = [[[0.0, 0.0, 0.0],
    #           [2.0, 0.0, 0.0],
    #           [0.0, 2.0, 0.0]],
    #          [[0.5, -.5, 0.0],
    #           [1.0, -.5, 0.0],
    #           [0.5, 2.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
    #
    # # intersection example
    # faces = [[[0.0, 0.0, 0.0],
    #           [2.0, 0.0, 0.0],
    #           [0.0, 2.0, 0.0]],
    #          [[-.9, -.9, 0.0],
    #           [-3., 3.5, 0.0],
    #           [9.5, 1.0, 0.0]]]
    # print(face_intersection_2d(f0=faces[0], f1=faces[1]))
    # Plt.plot_3d(faces=[faces], faces_view=True, normals_view=False, points_view=False, face_color=[["r", "g"]],
    #             face_alpha=0.5, azim=-90, elev=90)
