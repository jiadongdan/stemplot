import numpy as np
from skimage.transform import rotate
from matplotlib.colors import hsv_to_rgb


def find_rotation(com_x, com_y, order=16, outputall=False):
    def DPC_ACD(dpcx, dpcy, tlow, thigh):
        A, C, D = [], [], []
        for t in np.linspace(tlow, thigh, 100, endpoint=False):
            rdpcx = dpcx * np.cos(t) - dpcy * np.sin(t)
            rdpcy = dpcx * np.sin(t) + dpcy * np.cos(t)
            gXY, gXX = np.gradient(rdpcx)
            gYY, gYX = np.gradient(rdpcy)
            C.append(np.std(gYX) + np.std(gXY))
            D.append(np.std(gXX) + np.std(gYY))
            A.append(t)
        R = np.average([A[np.argmin(C)], A[np.argmax(D)]])
        return R, A, C, D

    RotCalcs = []
    RotCalcs.append(DPC_ACD(com_x, com_y, 0, np.pi))
    for i in range(1, order):
        RotCalcs.append(
            DPC_ACD(com_x, com_y, RotCalcs[i - 1][0] - np.pi / (10 ** i),
                    RotCalcs[i - 1][0] + np.pi / (10 ** i)))
    rotation = RotCalcs[-1][0]
    if outputall:
        return RotCalcs
    else:
        return RotCalcs[-1][0]

def rotate_com_xy(com_x, com_y, rotation):
    Ex = com_x
    Ey = com_y
    rEx = Ex * np.cos(rotation) - Ey * np.sin(rotation)
    rEy = Ex * np.sin(rotation) + Ey * np.cos(rotation)
    return rEx, rEy


def max_divergence(com_x, com_y):
    rotation = find_rotation(com_x, com_y)
    rEx, rEy = rotate_com_xy(com_x, com_y, rotation)
    return rEx, rEy


def get_potential(e1, hpass=0.015, lpass=0):
    rEx = e1.real
    rEy = e1.imag

    # solving the poisson equation via Fourier transfrom.
    fCX = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(rEx)))
    fCY = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(rEy)))
    KX = fCX.shape[1]
    KY = fCY.shape[0]
    kxran = np.linspace(-1, 1, KX, endpoint=True)
    kyran = np.linspace(-1, 1, KY, endpoint=True)
    kx, ky = np.meshgrid(kxran, kyran)
    fCKX = fCX * kx
    fCKY = fCY * ky
    fnum = (fCKX + fCKY)
    fdenom = np.pi * 2 * (0 + 1j) * (hpass + (kx ** 2 + ky ** 2) + lpass * (kx ** 2 + ky ** 2) ** 2)
    fK = np.divide(fnum, fdenom)
    return np.real(np.fft.ifftshift(np.fft.ifft2(np.fft.ifftshift(fK))))


def efield2rgb(rEx, rEy):
    # electric filed magnitude
    EMag = np.hypot(rEx, rEy)
    EMagScale = EMag / EMag.max()

    h = np.arctan2(rEy, rEx) / (2 * np.pi) % 1
    s = np.ones_like(rEx)
    v = EMagScale
    hsv = np.dstack([h, s, v])
    return hsv_to_rgb(hsv)

class CoMxy:

    def __init__(self, com_x, com_y, max_div=False):
        if max_div:
            self.com_x, self.com_y = max_divergence(com_x, com_y)
        else:
            self.com_x = com_x
            self.com_y = com_y
        self.efield_complex = self.com_x + 1j*self.com_y
        self.pot = get_potential(self.efield_complex)
        self.efield_rgb = efield2rgb(self.com_x, self.com_y)

    def rotate(self, angle, resize=True):
        com_x = rotate(self.com_x, angle, resize=resize)
        com_y = rotate(self.com_y, angle, resize=resize)
        self.com_x, self.com_y = rotate_com_xy(com_x, com_y, np.deg2rad(angle))
        self.efield_complex = self.com_x + 1j * self.com_y
        self.pot = get_potential(self.efield_complex)
        self.efield_rgb = efield2rgb(self.com_x, self.com_y)
