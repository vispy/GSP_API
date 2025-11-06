# -----------------------------------------------------------------------------
# GL Mathematics for numpy
# Copyright 2023 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Literal


def normalize(V: np.ndarray) -> np.ndarray:
    """Normalize V"""

    return V / (1e-16 + np.sqrt((np.array(V) ** 2).sum(axis=-1)))[..., np.newaxis]


def clamp(V: np.ndarray, vmin: float = 0, vmax: float = 1) -> np.ndarray:
    """Clamp V between vmin and vmax"""

    return np.minimum(np.maximum(V, vmin), vmax)


def viewport(x: int, y: int, w: int, h: int, d: float, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Viewport matrix

    Args:

        x (int):
            X origin (pixels) of the viewport (lower left)

        y (int):
            Y origin (pixels) of the viewport (lower left)

        h (int):
            Height (pixels) of the viewport

        w (int):
            Width (pixels) of the viewport

        d (float):
            Depth of the viewport.

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Viewport matrix
    """

    M = np.array(
        [
            [w / 2, 0, 0, x + w / 2],
            [0, h / 2, 0, y + h / 2],
            [0, 0, d / 2, d / 2],
            [0, 0, 0, 1],
        ],
        dtype=dtype,
    )
    return M


def frustum(
    left: float,
    right: float,
    bottom: float,
    top: float,
    znear: float,
    zfar: float,
    dtype: np.dtype = np.dtype(np.float32),
) -> np.ndarray:
    r"""View frustum matrix

    Args:

        left (float):
            Left coordinate of the field of view.

        right (float):
            Right coordinate of the field of view.

        bottom (float):
            Bottom coordinate of the field of view.

        top (float):
            Top coordinate of the field of view.

        znear (float):
            Near coordinate of the field of view.

        zfar (float):
            Far coordinate of the field of view.

        dtype (numpy dtype):
            dtype of the resulting array

    Returns:

        View frustum matrix
    """

    M = np.zeros((4, 4), dtype=dtype)
    M[0, 0] = +2.0 * znear / (right - left)
    M[1, 1] = +2.0 * znear / (top - bottom)
    M[2, 2] = -(zfar + znear) / (zfar - znear)
    M[0, 2] = (right + left) / (right - left)
    M[2, 1] = (top + bottom) / (top - bottom)
    M[2, 3] = -2.0 * znear * zfar / (zfar - znear)
    M[3, 2] = -1.0

    return M


def perspective(
    fovy: float,
    aspect: float,
    znear: float,
    zfar: float,
    dtype: np.dtype = np.dtype(np.float32),
) -> np.ndarray:
    """Perspective projection matrix

    Args:

        fovy (float):
            The field of view along the y axis.

        aspect (float):
            Aspect ratio of the view.

        znear (float):
            Near coordinate of the field of view.

        zfar (float):
            Far coordinate of the field of view.

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Perspective projection matrix
    """

    h = np.tan(0.5 * np.radians(fovy)) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar, dtype)


def ortho(left, right, bottom, top, znear, zfar, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create orthographic projection matrix

    Args:

        left (float):
            Left coordinate of the field of view.

        right (float):
            Right coordinate of the field of view.

        bottom (float):
            Bottom coordinate of the field of view.

        top (float):
            Top coordinate of the field of view.

        znear (float):
            Near coordinate of the field of view.

        zfar (float):
            Far coordinate of the field of view.

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Orthographic projection matrix
    """

    M = np.zeros((4, 4), dtype=dtype)
    M[0, 0] = +2.0 / (right - left)
    M[1, 1] = +2.0 / (top - bottom)
    M[2, 2] = -2.0 / (zfar - znear)
    M[3, 3] = 1.0
    M[0, 2] = -(right + left) / float(right - left)
    M[1, 3] = -(top + bottom) / float(top - bottom)
    M[2, 3] = -(zfar + znear) / float(zfar - znear)

    return M


def lookat(eye=(0, 0, 4.5), center=(0, 0, 0), up=(0, 0, 1), dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """
    Creates a viewing matrix derived from an eye point, a reference
    point indicating the center of the scene, and an up vector.

    Args:

        eye (vec3):
            Eye point

        center (vec3):
            Reference point

        up (vec3):
            Up vector

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        View matrix
    """

    eye = np.array(eye)
    center = np.array(center)
    up = np.array(up)

    Z = normalize(eye - center)
    Y = up
    X = normalize(np.cross(Y, Z))
    Y = normalize(np.cross(Z, X))
    return np.array([[X[0], X[1], X[2], -np.dot(X, eye)], [Y[0], Y[1], Y[2], -np.dot(Y, eye)], [Z[0], Z[1], Z[2], -np.dot(Z, eye)], [0, 0, 0, 1]], dtype=dtype)


def scale(scale: np.ndarray, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Non-uniform scaling along the x, y, and z axes

    Args:

        scale (vec3):
            Scaling vector

        dtype (np dtype):
            dtype of the resulting array

    Returns:

        Scaling matrix
    """

    x, y, z = np.array(scale)
    S = np.array(
        [
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1],
        ],
        dtype=dtype,
    )

    return S


def fit(vertices: np.ndarray) -> np.ndarray:
    """Fit vertices to the normalized cube

    Args:

        vertices (np.array): Vertices to fit

    Returns:

        (np.ndarray): vertices contained in the normalize cube
    """

    Vmin = vertices.min(axis=0)
    Vmax = vertices.max(axis=0)
    # return 2*(vertices-vmin) / max(vmax-vmin)-1
    V = 2 * (vertices - Vmin) / max(Vmax - Vmin) - 1
    return V - (V.min(axis=0) + V.max(axis=0)) / 2


def translate(translate: np.ndarray, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """
    Translation by a given vector

    Args:

        translate (vec3):
            Translation vector.

        dtype (np dtype):
            dtype of the resulting array

    Returns:

        Translation matrix
    """

    x, y, z = np.array(translate)
    T = np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]], dtype=dtype)

    return T


def center(vertices: np.ndarray) -> np.ndarray:
    """Center vertices around the origin.

    Args:

        vertices (np.array): Vertices to center

    Returns:

        (np.ndarray): vertices centered
    """

    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    return vertices - (vmax + vmin) / 2


def xrotate(angle_x: float = 0.0, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Rotation about the X axis

    Args:

        angle_x (float):
            Specifies the angle of rotation, in degrees.

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Rotation matrix
    """

    t = np.radians(angle_x)
    c, s = np.cos(t), np.sin(t)
    R = np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=dtype)

    return R


def yrotate(angle_y: float = 0.0, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Rotation about the Y axis

    Args:

        angle_y (float):
            Specifies the angle of rotation, in degrees.

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Rotation matrix
    """

    t = np.radians(angle_y)
    c, s = np.cos(t), np.sin(t)
    R = np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=dtype)

    return R


def zrotate(angle_z: float = 0.0, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Rotation about the Z axis

    Args:

        angle_z (float):
            Specifies the angle of rotation, in degrees.

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Rotation matrix
    """

    t = np.radians(angle_z)
    c, s = np.cos(t), np.sin(t)
    R = np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=dtype)

    return R


def rotate(angle: float, axis: np.ndarray, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Rotation around an arbitrary axis of angle

    Args:

        angle (float):
            Specifies the angle of rotation, in degrees.

        axis (vec3):
            Axis of rotation

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Rotation matrix
    """

    t = np.radians(angle)

    axis = normalize(np.array(axis))
    a = np.cos(t / 2)
    b, c, d = -axis * np.sin(t / 2)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    R = np.array(
        [
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac), 0],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab), 0],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc, 0],
            [0, 0, 0, 1],
        ],
        dtype=dtype,
    )

    return R


def align(U: np.ndarray, V: np.ndarray, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """
    Return the rotation matrix that aligns U to V

    Args:

        U (vec[234]):
            First vector

        U (vec[234]):
            Second vector

        dtype (np.dtype):
            dtype of the resulting array

    Returns:

        Rotation matrix
    """

    a, b = normalize(U), normalize(V)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.zeros((4, 4), dtype=dtype)
    R[:3, :3] = np.eye(3) + K + K @ K * ((1 - c) / (s**2))
    R[3, 3] = 1

    return R


def frontback(triangles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Sort front and back facing triangles

    Parameters:
    -----------
    T : (n,3) array
       Triangles to sort

    Returns:
    --------
    front and back facing triangles as (n1,3) and (n2,3) arrays (n1+n2=n)
    """
    Z = (
        (triangles[:, 1, 0] - triangles[:, 0, 0]) * (triangles[:, 1, 1] + triangles[:, 0, 1])
        + (triangles[:, 2, 0] - triangles[:, 1, 0]) * (triangles[:, 2, 1] + triangles[:, 1, 1])
        + (triangles[:, 0, 0] - triangles[:, 2, 0]) * (triangles[:, 0, 1] + triangles[:, 2, 1])
    )
    return Z < 0, Z >= 0


def camera(xrotation: float = 25.0, yrotation: float = 45.0, zoom: float = 1.0, mode: Literal["perspective", "ortho"] = "perspective") -> np.ndarray:
    xrotation = min(max(xrotation, 0), 90)
    yrotation = min(max(yrotation, 0), 90)
    zoom = max(0.1, zoom)
    scale_vector = np.array([zoom, zoom, zoom], dtype=np.float32)
    model = scale(scale_vector) @ xrotate(xrotation) @ yrotate(yrotation)
    translate_vector = np.array([0, 0, -4.5], dtype=np.float32)
    view = translate(translate_vector)
    if mode == "ortho":
        proj = ortho(-1, +1, -1, +1, 1, 100)
    elif mode == "perspective":
        proj = perspective(25, 1, 1, 100)
    else:
        raise ValueError("Unknown camera mode: " + mode)
    return proj @ view @ model
