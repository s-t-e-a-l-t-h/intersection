import Plot as Plt
import numpy as np

PRECISION = 10

normal = [[0.1, 0.0, 0.0], [0.0, 0.0, 0.0]]
point = [[1.2, 1.2, 0.0], [0.32, 0.35, 0.28]]


def line(u, a, b):
    # line equation
    # x = a  + u * (b - a)
    a, b = np.array(a), np.array(b)
    return a + (u * (b - a))


def line_t(u, a, t):
    """
    :rtype: ndarray
    """
    a, t = np.array(a), np.array(t)
    return a + (u * t)


def plane(n, p, a, b):
    # plane equation
    # (x - p)  n = 0
    # coo of plane point x = [a, b, c]
    # get a, b and return [a, b, c] if n[2] != 0 etc.
    n, p = np.array(n), np.array(p)
    if n[2] != 0:
        c = (np.dot(p, n) - (a * n[0]) - (b * n[1])) / n[2]
        return a, b, c
    elif n[1] != 0:
        c = (np.dot(p, n) - (a * n[0]) - (b * n[2])) / n[1]
        return a, c, b
    elif n[0] != 0:
        c = (np.dot(p, n) - (a * n[1]) - (b * n[2])) / n[0]
        return c, a, b
    else:
        return False

def planeline_intersection(a, b, p, n):
    """
    :rtype: ndarray
    """
    a, b, p, n = np.array(a), np.array(b), np.array(p), np.array(n)
    if np.dot((b - a), n) != 0:
        u_intersection = np.dot((p - a), n) / np.dot((b - a), n)
        return line(u_intersection, a, b)
    return False


def to_2d_plane(s1, s2, s3, pt):
    # s1, s2, s3 - orthonormal vectors of reference frame
    s1, s2, s3, pt = np.array(s1), np.array(s2), np.array(s3), np.array(pt)
    m = [[np.dot(np.array([1., 0., 0.]), s1), np.dot(np.array([0., 1., 0.]), s1), np.dot(np.array([0., 0., 1.]), s1)],
         [np.dot(np.array([1., 0., 0.]), s2), np.dot(np.array([0., 1., 0.]), s2), np.dot(np.array([0., 0., 1.]), s2)],
         [np.dot(np.array([1., 0., 0.]), s3), np.dot(np.array([0., 1., 0.]), s3), np.dot(np.array([0., 0., 1.]), s3)]]
    return np.dot(m, pt)


def get_projection_plane(n, p):
    projection_plane = [p]
    a, b = np.array([[1.5, 1.5], [0.0, 1.0]])
    for i in range(0, 2):
        projection_plane.append(np.array(plane(n, p, a[i], b[i])))
    return np.array(projection_plane)


projection_point = line_t(-10, point[0], normal[0])
normal.append([0, 0, 0])
point.append(projection_point)

intersection = planeline_intersection(point[-1], point[1], point[0], normal[0])
normal.append([0, 0, 0])
point.append(intersection)

pp = get_projection_plane(normal[0], point[0])

ref1, ref3 = (pp[0] - pp[1]) / (np.linalg.norm(pp[0] - pp[1])), normal[0] / np.linalg.norm(normal[0])
ref2 = np.cross(ref1, ref3) / np.linalg.norm(np.cross(ref1, ref3))

print(to_2d_plane(ref1, ref2, ref3, intersection - point[0]))

normal.append(ref1)
normal.append(ref2)

point.append(point[0])
point.append(point[0])

normal[0] = ref3
normal = Plt.vector_array_translation(vector_arr=normal, translation_arr=point)
# print(intersection)
# print(to_plane())




Plt.plot_3d(faces=[[pp]], vertices=[point], normals=[normal], faces_view=True, normals_view=True, points_view=True,
            face_color=[["r", "g"]], point_color=["r", "g", "b", "k"], face_alpha=0.5, azim=-90, elev=90, point_size=20)
