import numpy as np
import scipy.optimize as sp

# The following two variables can be adjusted and affect the generation of lookup tables

# Array of user-provided stretch factors to compute.
# For each entry an appropriate lookup table './luts/lut_arcsinh_stretch_<user_stretch>.cube' will be calculated.
user_stretches = [5, 10, 15, 25, 40, 65, 105, 170, 275, 445, 720, 1165]
# number of elements in each lookup table
samples = 256

# internal helper variables
R0 = np.arange(0, 1, 1 / (samples - 1))  # unstretched lut values from 0.0 .. 1.0
cube_header = f"""
LUT_1D_SIZE {samples}
DOMAIN_MIN 0.0 0.0 0.0
DOMAIN_MAX 1.0 1.0 1.0
""".strip()  # .cube file format header


user_stretch_tmp = (
    -1
)  # global temporary variable that holds the current target user-provided stretch factor.


def beta(x):
    """Calculates the internal softening factor beta based on the user-provided stretch factor."""
    return x / np.arcsinh(x) - user_stretch_tmp


def stretch(x, beta):
    """Calculates the internal stretch factor k based on the PixInsight descriotion at https://pixinsight.com/doc/tools/ArcsinhStretch/ArcsinhStretch.html#__Mathematical_Description__
    beta corresponds to the described, internal softening factor that is calculated based on the user-provided stretch factor in function 'beta(x)'.
    """
    return np.arcsinh(beta * x) / np.arcsinh(beta)


def create_lut(user_stretch):
    """Calculates a lookup table for the given user-provided stretch factor and stores it in './luts/lut_arcsinh_stretch_<user_stretch>.cube'.
    Existing luts will be overwritten.
    """
    global R0
    b = sp.brentq(beta, 1, 100000)  # approximate the internal softening factory beta
    Ks = np.array(
        [stretch(r, b) for r in R0]
    )  # calculate samples of internal stretch factory k

    # export the lookup table
    f = open(f"./luts/lut_arcsinh_stretch_{user_stretch}.cube", "w", newline="\n")
    f.write(f"TITLE \"Arcsinh_Stretch_{user_stretch}\"\n")
    f.write(f"{cube_header}\n")  # write the .cube header
    for k in Ks:
        f.write(f"{k} {k} {k}\n")
    f.write(f"{1.0} {1.0} {1.0}")
    f.close()


# create an Arcsinh-based lookup table in .cube format for each user-provided stretch factor.
for u in user_stretches:
    user_stretch_tmp = u
    create_lut(u)
