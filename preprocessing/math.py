import math

def calc_dist(x, y, slope, intercept):
    return abs(slope * x - y + intercept)/math.sqrt(slope**2 + 1)

def get_slope_intercept(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    return slope, intercept

def get_y_val(x, slope, y_intercept):
    return (x*slope) + y_intercept