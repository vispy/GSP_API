# -----------------------------------------------------------------------------
# GL Mathematics for numpy
# Copyright 2023 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
"""OpenGL Mathematics (GLM) utilities for numpy.

This module provides mathematical functions commonly used in 3D graphics,
including matrix transformations, projections, rotations, and vector operations.
All operations are implemented using numpy for efficient computation.
"""
import numpy as np
from typing import Literal


def normalize(V: np.ndarray) -> np.ndarray:
    """Normalize a vector or array of vectors to unit length.
    
    Args:
        V: Vector or array of vectors to normalize.
        
    Returns:
        Normalized vector(s) with unit length.
    """
    return V / (1e-16 + np.sqrt((np.array(V) ** 2).sum(axis=-1)))[..., np.newaxis]


def clamp(V: np.ndarray, vmin: float = 0, vmax: float = 1) -> np.ndarray:
    """Clamp values between minimum and maximum bounds.
    
    Args:
        V: Array of values to clamp.
        vmin: Minimum value (default: 0).
        vmax: Maximum value (default: 1).
        
    Returns:
        Array with values clamped to [vmin, vmax].
    """
    return np.minimum(np.maximum(V, vmin), vmax)


def viewport(x: int, y: int, w: int, h: int, d: float, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create a viewport transformation matrix.

    Args:
        x (int): X origin (pixels) of the viewport (lower left)
        y (int): Y origin (pixels) of the viewport (lower left)
        w (int): Width (pixels) of the viewport
        h (int): Height (pixels) of the viewport
        d (float): Depth of the viewport.
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Viewport matrix
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
    r"""Create a view frustum projection matrix.

    Args:
        left (float): Left coordinate of the field of view.
        right (float): Right coordinate of the field of view.
        bottom (float): Bottom coordinate of the field of view.
        top (float): Top coordinate of the field of view.
        znear (float): Near coordinate of the field of view.
        zfar (float): Far coordinate of the field of view.
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: View frustum matrix
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
    """Create a perspective projection matrix.

    Args:
        fovy (float): The field of view along the y axis.
        aspect (float): Aspect ratio of the view.
        znear (float): Near coordinate of the field of view.
        zfar (float): Far coordinate of the field of view.
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Perspective projection matrix
    """
    h = np.tan(0.5 * np.radians(fovy)) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar, dtype)


def ortho(left: float, right: float, bottom: float, top: float, znear: float, zfar: float, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create an orthographic projection matrix.

    Args:
        left (float): Left coordinate of the field of view.
        right (float): Right coordinate of the field of view.
        bottom (float): Bottom coordinate of the field of view.
        top (float): Top coordinate of the field of view.
        znear (float): Near coordinate of the field of view.
        zfar (float): Far coordinate of the field of view.
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Orthographic projection matrix
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


def lookat(
    eye: tuple[float, float, float] = (0, 0, 4.5),
    center: tuple[float, float, float] = (0, 0, 0),
    up: tuple[float, float, float] = (0, 0, 1),
    dtype: np.dtype = np.dtype(np.float32),
) -> np.ndarray:
    """Create a viewing matrix derived from an eye point, reference point, and up vector.
    
    Args:
        eye (tuple[float, float, float]): Eye point
        center (tuple[float, float, float]): Reference point
        up (tuple[float, float, float]): Up vector
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: View matrix
    """
    eye_np = np.array(eye)
    center_np = np.array(center)
    up_np = np.array(up)

    Z = normalize(eye_np - center_np)
    Y = up_np
    X = normalize(np.cross(Y, Z))
    Y = normalize(np.cross(Z, X))
    return np.array(
        [
            [X[0], X[1], X[2], -np.dot(X, eye_np)],
            [Y[0], Y[1], Y[2], -np.dot(Y, eye_np)],
            [Z[0], Z[1], Z[2], -np.dot(Z, eye_np)],
            [0, 0, 0, 1],
        ],
        dtype=dtype,
    )


def scale(scale: np.ndarray, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create a non-uniform scaling matrix along the x, y, and z axes.

    Args:
        scale (np.ndarray): Scaling vector
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Scaling matrix
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
    """Fit vertices to the normalized cube.

    Args:
        vertices (np.ndarray): Vertices to fit

    Returns:
        np.ndarray: vertices contained in the normalize cube
    """
    Vmin = vertices.min(axis=0)
    Vmax = vertices.max(axis=0)
    # return 2*(vertices-vmin) / max(vmax-vmin)-1
    V = 2 * (vertices - Vmin) / max(Vmax - Vmin) - 1
    return V - (V.min(axis=0) + V.max(axis=0)) / 2


def translate(translate: np.ndarray, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create a translation matrix by a given vector.

    Args:
        translate (np.ndarray): Translation vector.
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Translation matrix
    """
    x, y, z = np.array(translate)
    T = np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]], dtype=dtype)

    return T


def center(vertices: np.ndarray) -> np.ndarray:
    """Center vertices around the origin.

    Args:
        vertices (np.ndarray): Vertices to center

    Returns:
        np.ndarray: vertices centered
    """
    vmin = vertices.min(axis=0)
    vmax = vertices.max(axis=0)
    return vertices - (vmax + vmin) / 2


def xrotate(angle_x: float = 0.0, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create a rotation matrix about the X axis.

    Args:
        angle_x (float):
            Specifies the angle of rotation, in degrees.
        dtype (np.dtype):
            dtype of the resulting array

    Returns:
       np.ndarray: Rotation matrix
    """
    t = np.radians(angle_x)
    c, s = np.cos(t), np.sin(t)
    R = np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=dtype)

    return R


def yrotate(angle_y: float = 0.0, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create a rotation matrix about the Y axis.

    Args:
        angle_y (float): Specifies the angle of rotation, in degrees.
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Rotation matrix
    """
    t = np.radians(angle_y)
    c, s = np.cos(t), np.sin(t)
    R = np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=dtype)

    return R


def zrotate(angle_z: float = 0.0, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create a rotation matrix about the Z axis.

    Args:
        angle_z (float): Specifies the angle of rotation, in degrees.
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Rotation matrix
    """
    t = np.radians(angle_z)
    c, s = np.cos(t), np.sin(t)
    R = np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=dtype)

    return R


def rotate(angle: float, axis: np.ndarray, dtype: np.dtype = np.dtype(np.float32)) -> np.ndarray:
    """Create a rotation matrix around an arbitrary axis.

    Args:
        angle (float): Specifies the angle of rotation, in degrees.
        axis (np.ndarray): Axis of rotation
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Rotation matrix
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
    """Return the rotation matrix that aligns vector U to vector V.

    Args:
        U (np.ndarray): First vector
        V (np.ndarray): Second vector
        dtype (np.dtype): dtype of the resulting array

    Returns:
        np.ndarray: Rotation matrix
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
    """Sort front and back facing triangles.

    Args:
        triangles (np.ndarray): Triangles to sort

    Returns:
        tuple[np.ndarray, np.ndarray]: front and back facing triangles as (n1,3) and (n2,3) arrays (n1+n2=n)
    """
    Z = (
        (triangles[:, 1, 0] - triangles[:, 0, 0]) * (triangles[:, 1, 1] + triangles[:, 0, 1])
        + (triangles[:, 2, 0] - triangles[:, 1, 0]) * (triangles[:, 2, 1] + triangles[:, 1, 1])
        + (triangles[:, 0, 0] - triangles[:, 2, 0]) * (triangles[:, 0, 1] + triangles[:, 2, 1])
    )
    return Z < 0, Z >= 0


def camera(xrotation: float = 25.0, yrotation: float = 45.0, zoom: float = 1.0, mode: Literal["perspective", "ortho"] = "perspective") -> np.ndarray:
    """Create a camera transformation matrix.

    Args:
        xrotation (float): Rotation around the X axis in degrees.
        yrotation (float): Rotation around the Y axis in degrees.
        zoom (float): Zoom factor.
        mode (Literal["perspective", "ortho"]): Camera mode.

    Returns:
        np.ndarray: Camera matrix

    Raises:
        ValueError: If an unknown camera mode is provided.
    """
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
