from ANPRmodel.preprocessing.math import get_slope_intercept, get_y_val, calc_dist

def detect_lane(x_min, y_min, x_max, y_max, slope_inner, slope_middle):
    # inner x-max
    slope_inner, intercept_inner = get_slope_intercept(*slope_inner)
    slope_middle, intercept_middle = get_slope_intercept(*slope_middle)
    if y_min <= get_y_val(x_max, slope_inner, intercept_inner):
        return "Inner (Lane 1)"

        # between inner slope
    elif y_min < get_y_val(x_min, slope_inner, intercept_inner) and y_min > get_y_val(x_max, slope_inner,
                                                                                      intercept_inner):
        if calc_dist(x_min, y_min, slope_inner, intercept_inner) > calc_dist(x_max, y_min, slope_inner,
                                                                             intercept_inner):
            return "Inner (Lane 1)"
        else:
            return "Middle (Lane 2)"

    # x-min>inner: definitely not in inner lane
    
    elif y_min > get_y_val(x_min, slope_inner, intercept_inner):

        # definitely outer lane
        if y_min <= get_y_val(x_min, slope_middle, intercept_middle):
            return "Outer (Lane 3)"

        elif y_min >= get_y_val(x_max, slope_middle, intercept_middle):
            return "Middle (Lane 2)"

        # if x_min smaller than middle slope ==> between middle slope
        elif y_min > get_y_val(x_min, slope_middle, intercept_middle):
            if calc_dist(x_min, y_min, slope_middle, intercept_middle) < calc_dist(x_max, y_min, slope_middle,
                                                                                   intercept_middle):
                return "Outer (Lane 3)"

        return "Middle (Lane 2)"
