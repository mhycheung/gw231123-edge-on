"""Directions, rotations and the line of sight."""

import numpy as np


def unit_vector(theta, phi):
    theta, phi = np.broadcast_arrays(theta, phi)
    return np.stack([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi),
                     np.cos(theta)], axis=-1)


def angles(n):
    """(theta, phi) of unit vector(s) n, shape (..., 3)."""
    n = np.asarray(n)
    return np.arccos(np.clip(n[..., 2], -1, 1)), np.arctan2(n[..., 1], n[..., 0])


def line_of_sight(iota, phase):
    """N in the source frame: (theta, phi) = (iota, pi/2 - phase), LAL convention."""
    return unit_vector(iota, np.pi / 2 - phase)


def angle_between(a, b):
    a, b = np.asarray(a), np.asarray(b)
    c = np.sum(a * b, axis=-1) / (np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1))
    return np.arccos(np.clip(c, -1, 1))


def quat_rotate_z(q):
    """R(q) z for unit quaternions q = (w, x, y, z), shape (4, ...): v' = q v q^-1."""
    w, x, y, z = q
    return np.stack([2 * (x * z + w * y), 2 * (y * z - w * x), 1 - 2 * (x * x + y * y)],
                    axis=-1)


def fibonacci_sphere(n):
    """n nearly uniform unit vectors, shape (n, 3)."""
    i = np.arange(n) + 0.5
    theta = np.arccos(1 - 2 * i / n)
    phi = np.pi * (1 + 5 ** 0.5) * i
    return unit_vector(theta, np.mod(phi, 2 * np.pi))


def tangent_basis(n0):
    """Two unit vectors orthogonal to n0 and to each other."""
    n0 = np.asarray(n0, float)
    a = np.array([1.0, 0, 0]) if abs(n0[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n0, a)
    u /= np.linalg.norm(u)
    return u, np.cross(n0, u)
