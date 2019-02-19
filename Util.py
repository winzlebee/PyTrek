import math

# Utility functions that help with transformations made in the game

# Get shortest angle distance between two angles and in which direction
def shortAngleDist(a0,a1):
    maxA = 360;
    da = (a1 - a0) % maxA;
    return 2*da % maxA - da;

# Linearly interpolate between two angles t amount
def angleLerp(a0,a1,t):
    return a0 + shortAngleDist(a0,a1)*t
