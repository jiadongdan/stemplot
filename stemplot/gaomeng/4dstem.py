import numpy as np
from matplotlib.colors import hsv_to_rgb
from scipy.ndimage import center_of_mass
from scipy.signal import find_peaks
from skimage.transform import warp_polar


def get_center(cbed_mean, threshold=0.4, method='cbed'):
    # get the normalized CBED pattern
    cbed_mean_norm = (cbed_mean - np.amin(cbed_mean)) / np.ptp(cbed_mean)
    mask = 1 * (cbed_mean_norm > threshold)

    if method == 'mask':
        y, x = center_of_mass(mask)
    elif method == 'cbed':
        y, x = center_of_mass(cbed_mean)
    elif method == 'mask_cbed':
        y, x = center_of_mass(cbed_mean*mask)
    else:
        y, x = center_of_mass(cbed_mean)
    return (x, y)


def get_calibration(cbed_mean, center_x, center_y, convergent_angle):
    center = (center_y, center_x)
    l = warp_polar(cbed_mean, center).mean(axis=0)
    l_grad = np.abs(np.gradient(l))
    _, prop = find_peaks(l_grad, distance=len(l_grad), width=1, rel_height=0.5)
    return (prop['left_ips'][0] + prop['right_ips'][0])/2/convergent_angle


def efield2rgb(rEx, rEy):
    # electric filed magnitude
    EMag = np.hypot(rEx, rEy)
    EMagScale = EMag / EMag.max()

    h = np.arctan2(rEy, rEx) / (2 * np.pi) % 1
    s = np.ones_like(rEx)
    v = EMagScale
    hsv = np.dstack([h, s, v])
    return hsv_to_rgb(hsv)


class STEMData4D:

    def __init__(self, data, convergent_angle=31.98, threshold=0.4, center_method=None):
        self.data = data
        self.convergent_angle = convergent_angle
        self.threshold = threshold
        self.cbed_mean = np.mean(self.data, axis=(0, 1))
        self.x, self.y = get_center(self.cbed_mean, self.threshold, method=center_method)
        self._calibration = get_calibration(self.cbed_mean, self.x, self.y, self.convergent_angle)

        self.com_x = None
        self.com_y = None
        self.rotation = None

    @classmethod
    def from_file(cls, filename, convergent_angle=31.98):
        data = np.load(filename)
        return cls(data, convergent_angle)

    @property
    def centers(self):
        return (self.x, self.y)

    @property
    def calibration(self):
        return self._calibration

    @property
    def mask(self):
        # get the normalized CBED pattern
        cbed_mean_norm = (self.cbed_mean - np.amin(self.cbed_mean)) / np.ptp(self.cbed_mean)
        mask = 1 * (cbed_mean_norm > self.threshold)
        return mask

    def get_icom(self, use_mask=True):
        # get the integrated center of mass image along x and y direction.
        xx = (np.arange(0, self.data.shape[3]) - self.x) / self.calibration
        yy = (np.arange(0, self.data.shape[2]) - self.y) / self.calibration
        X, Y = np.meshgrid(xx, yy)
        if use_mask:
            data_ = self.data * (self.mask > 0)
        else:
            data_ = self.data
        self.com_x = np.mean(data_ * X, axis=(2, 3))
        self.com_y = np.mean(data_ * Y, axis=(2, 3))
        return self.com_x, self.com_y

    def find_rotation(self, order=16, outputall=False):

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
        RotCalcs.append(DPC_ACD(self.com_x, self.com_y, 0, np.pi))
        for i in range(1, order):
            RotCalcs.append(
                DPC_ACD(self.com_x, self.com_y, RotCalcs[i - 1][0] - np.pi / (10 ** i), RotCalcs[i - 1][0] + np.pi / (10 ** i)))
        self.rotation = RotCalcs[-1][0]
        if outputall:
            return RotCalcs
        else:
            return RotCalcs[-1][0]


    def get_e_field(self, use_mask=True, return_rgb=True):
        if self.com_x is None and self.com_y is None:
            self.com_x, self.com_y = self.get_icom(use_mask=use_mask)
        if self.rotation is None:
            rotation = self.find_rotation()
        else:
            rotation = self.rotation

        Ex = self.com_x
        Ey = self.com_y
        rEx = Ex * np.cos(rotation) - Ey * np.sin(rotation)
        rEy = Ex * np.sin(rotation) + Ey * np.cos(rotation)
        self.efield_complex = rEx + 1j*rEy
        self.efield_rgb = efield2rgb(rEx, rEy)
        if return_rgb:
            return self.efield_complex, self.efield_rgb
        else:
            return self.efield_complex

    def get_charge_density(self, use_mask=True):
        if self.com_x is None and self.com_y is None:
            self.com_x, self.com_y = self.get_icom(use_mask=use_mask)
        if self.rotation is None:
            rotation = self.find_rotation()
        else:
            rotation = self.rotation

        Ex = self.com_x
        Ey = self.com_y
        # rotate first.
        rEx = Ex * np.cos(rotation) - Ey * np.sin(rotation)
        rEy = Ex * np.sin(rotation) + Ey * np.cos(rotation)

        # get the gradient, and then generate the charge density.
        gxx, gyy = np.gradient(rEx)[1], np.gradient(rEy)[0]

        return - gxx - gyy

    def get_potential(self, hpass=0.015, lpass=0, use_mask=True):
        if self.com_x is None and self.com_y is None:
            self.com_x, self.com_y = self.get_icom(use_mask=use_mask)
        if self.rotation is None:
            rotation = self.find_rotation()
        else:
            rotation = self.rotation

        Ex = self.com_x
        Ey = self.com_y

        # rotate first.
        rEx = Ex * np.cos(rotation) - Ey * np.sin(rotation)
        rEy = Ex * np.sin(rotation) + Ey * np.cos(rotation)

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
