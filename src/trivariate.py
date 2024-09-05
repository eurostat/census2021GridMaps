


def trivariate_classifier(properties, total_function, opts=None):
    if opts is None:
        opts = {}

    # The three properties
    p0, p1, p2 = properties[0], properties[1], properties[2]

    # The classifier center point. Sum must be equal to 1
    c0, c1, c2 = opts.get('center', [1 / 3, 1 / 3, 1 / 3])

    # Parameter to decide whether to use mixed classes m0, m1, m2
    with_mixed_classes = opts.get('withMixedClasses', True)

    # centerCoefficient: Parameter to decide whether to use a central class, and the size of this central class
    # Set to 0 or None for not showing any central class. Set to 1 for a central class that contains the mixed classes
    cc = 1 - opts['centerCoefficient'] if 'centerCoefficient' in opts else None

    #print(c0,c1,c2,with_mixed_classes, cc)

    # The output classifier method
    def fun(c):
        # Get total
        tot = total_function(c)
        if not tot:
            return None
        # Compute shares
        s0, s1, s2 = float(c[p0]) / tot, float(c[p1]) / tot, float(c[p2]) / tot

        # Class 0
        if s0 >= c0 and s1 <= c1 and s2 <= c2:
            # Central class near class 0
            if cc is not None and (s2 - c2) * c1*(1 - cc) >= (s1 - cc * c1) * c2*(cc - 1):
                return "center"
            return "0"

        # Class 1
        if s0 <= c0 and s1 >= c1 and s2 <= c2:
            # Central class near class 1
            if cc is not None and (s2 - c2) * c0*(1 - cc) >= (s0 - cc * c0) * c2*(cc - 1):
                return "center"
            return "1"

        # Class 2
        if s0 <= c0 and s1 <= c1 and s2 >= c2:
            # Central class near class 2
            if cc is not None and (s1 - c1) * c0*(1 - cc) >= (s0 - cc * c0) * c1*(cc - 1):
                return "center"
            return "2"

        # Middle class 0 - intersection class 1 and 2
        if s0 <= c0 and s1 >= c1 and s2 >= c2:
            # Central class
            if cc is not None and s0 > cc * c0:
                return "center"
            if with_mixed_classes:
                return "m0"
            return "1" if s1 > s2 else "2"

        # Middle class 1 - intersection class 0 and 1
        if s0 >= c0 and s1 <= c1 and s2 >= c2:
            # Central class
            if cc is not None and s1 > cc * c1:
                return "center"
            if with_mixed_classes:
                return "m1"
            return "0" if s0 > s2 else "2"

        # Middle class 2 - intersection class 0 and 1
        if s0 >= c0 and s1 >= c1 and s2 <= c2:
            # Central class
            if cc is not None and s2 > cc * c2:
                return "center"
            if with_mixed_classes:
                return "m2"
            return "1" if s1 > s0 else "0"

        # Should not happen
        print(s0,s1,s2)
        return "unknown"

    # Attach information to output function
    fun.center = [c0, c1, c2]
    fun.center_coefficient = opts.get('centerCoefficient')

    return fun
