import numpy as np
from ase import Atoms
from ase.cell import Cell
from ase.data import chemical_symbols
from abtem import show_atoms
from sklearn.neighbors import NearestNeighbors


def get_a_thickness(formula):
    a_thickness_dict = {
        'MoS2': (3.19, 3.139),
        'MoSe2': (3.33, 3.350),
        'MoTe2': (3.57, 3.625),
        'NbS2': (3.37, 3.137),
        'NbSe2': (3.49, 3.368),
        'PdSe2': (3.91, 2.512),
        'TaS2': (3.34, 3.131),
        'TaSe2': (3.47, 3.354),
        'VS2': (3.18, 2.987),
        'WS2': (3.19, 3.147),
        'WSe2': (3.33, 3.365),
        'WTe2': (3.56, 3.362),
    }
    try:
        a, t = a_thickness_dict[formula]
    except:
        a, t = 3.41, 3.230
    return a, t


def mx2(formula='MoS2', size=(1, 1, 1), vacuum=2):
    # get a and thickness according to formula
    a, thickness = get_a_thickness(formula)

    basis = [(0, 0, 0),
             (2 / 3, 1 / 3, 0.5 * thickness),
             (2 / 3, 1 / 3, -0.5 * thickness)]
    cell = [[a, 0, 0], [-a / 2, a * 3 ** 0.5 / 2, 0], [0, 0, 0]]

    atoms = Atoms(formula, cell=cell, pbc=(1, 1, 0))
    atoms.set_scaled_positions(basis)
    if vacuum is not None:
        atoms.center(vacuum, axis=2)
    atoms = atoms.repeat(size)
    return atoms


def make_it_orhto(atoms):
    cell_ = atoms.cell.copy()
    a, b, c = atoms.cell
    cell_[1] = [0., b[1], 0.]

    atoms.set_cell(cell_)
    atoms.wrap()
    atoms.center()
    return atoms


def get_centered_m(atoms):
    z_dict = {symbol: Z for Z, symbol in enumerate(chemical_symbols)}

    metal = [e for e in atoms.symbols.species() if e not in ['S', 'Se', 'Te']][0]
    Z = z_dict[metal]
    pts_ = atoms.positions[atoms.numbers == Z]
    pts = pts_[:, 0:2]
    p = atoms.cell.array.sum(axis=0)[None, 0:2] / 2

    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(pts)
    d, ind = nbrs.kneighbors(p)
    p_xyz = pts_[ind[0][0]]
    p_xyz[2] = 0
    return p_xyz


def get_centered_x(atoms):
    z_dict = {symbol: Z for Z, symbol in enumerate(chemical_symbols)}

    element = [e for e in atoms.symbols.species() if e in ['S', 'Se', 'Te']][0]
    Z = z_dict[element]
    pts_ = atoms.positions[atoms.numbers == Z]
    pts = pts_[:, 0:2]
    p = atoms.cell.array.sum(axis=0)[None, 0:2] / 2

    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(pts)
    d, ind = nbrs.kneighbors(p)
    p_xyz = pts_[ind[0][0]]
    p_xyz[2] = 0
    return p_xyz


def crop_atoms(atoms, L=20):
    pts = atoms.positions
    x, y, z = pts.T
    l = L
    mask1 = np.logical_and(x > -l, x < l)
    mask2 = np.logical_and(y > -l, y < l)
    mask = mask1 * mask2
    pts_ = pts[mask]
    numbers_ = atoms.numbers[mask]
    return Atoms(numbers=numbers_, positions=pts_, cell=atoms.cell)


def get_mx2_atoms(L=10, formula='MoS2', vacuum=2, theta=0, center='m'):
    L = L / 2.

    unit = mx2(formula=formula, vacuum=vacuum)

    # repeat, L has to be integer
    S = np.ceil(L).astype(int)
    atoms = unit.repeat([S, S, 1])
    # make it orthogonal
    atoms = make_it_orhto(atoms)
    if center == 'm':
        center_xyz = get_centered_m(atoms)
    elif center == 'x':
        center_xyz = get_centered_x(atoms)

    atoms.translate(-center_xyz)
    atoms.rotate(theta, 'z')
    atoms = crop_atoms(atoms, L)
    atoms.translate([L, L, center_xyz[2]])

    c_new = unit.cell[2]
    cell_new = Cell.fromcellpar([2 * L, 2 * L, c_new, 90, 90, 90])

    return Atoms(atoms.symbols, atoms.positions, cell=cell_new)


def remove_atoms(atoms, inds):
    atoms_copy = atoms.copy()
    del atoms_copy[inds]
    return atoms_copy


def replace_atoms(atoms, inds, element):
    atoms_copy = atoms.copy()
    if np.iterable(inds):
        for ind in inds:
            atoms_copy.symbols[ind] = element
    else:
        atoms_copy.symbols[inds] = element


def get_mx_elements(symbols):
    elements = np.unique(list(symbols), return_counts=False)[::-1]
    e1, e2 = elements[0:2]
    if e1 in ['S', 'Se', 'Te']:
        return e2, e1
    else:
        return e1, e2


# use composition
# center index, and nearby three indices
class MX2:

    def __init__(self, L=10, formula='MoS2', vacuum=2, theta=0, center='m'):
        self.formula = formula
        self.center = center
        self.a, t = get_a_thickness(self.formula)
        self.atoms = get_mx2_atoms(L=L, formula=formula, vacuum=vacuum, theta=theta, center=center)
        self.m_element, self.x_element = get_mx_elements(self.atoms.symbols)

    @property
    def m_ind(self):
        return np.where(self.atoms.symbols == self.m_element)[0]

    @property
    def x_top_ind(self):
        inds = np.where(self.atoms.symbols == self.x_element)[0]
        x_atoms = self.atoms[inds]
        z_mean = self.m_atoms.positions[:, 2].mean()
        mask1 = x_atoms.positions[:, 2] > z_mean
        return inds[mask1]

    @property
    def x_bottom_ind(self):
        inds = np.where(self.atoms.symbols == self.x_element)[0]
        x_atoms = self.atoms[inds]
        z_mean = self.m_atoms.positions[:, 2].mean()
        mask1 = x_atoms.positions[:, 2] < z_mean
        return inds[mask1]


    @property
    def m_atoms(self):
        mask = self.atoms.symbols == self.m_element
        return self.atoms[mask]


    @property
    def x_top_atoms(self):
        mask = self.atoms.symbols == self.x_element
        x_atoms = self.atoms[mask]
        z_mean = self.m_atoms.positions[:, 2].mean()
        mask1 = x_atoms.positions[:, 2] > z_mean
        return x_atoms[mask1]

    @property
    def x_bottom_atoms(self):
        mask = self.atoms.symbols == self.x_element
        x_atoms = self.atoms[mask]
        z_mean = self.m_atoms.positions[:, 2].mean()
        mask1 = x_atoms.positions[:, 2] < z_mean
        return x_atoms[mask1]


    def create_m_configs(self):
        assert self.center == 'm', 'center has to be metal.'
        idx1 = self.get_inds(self.m_atoms)
        idx2 = self.get_inds(self.x_top_atoms)
        idx3 = self.get_inds(self.x_bottom_atoms)

        ind = self.m_ind[idx1]  # len 1
        ind1 = self.x_top_ind[idx2] # len 3
        ind2 = self.x_bottom_ind[idx3] # len 3

        # create single vacancies
        atoms1 = remove_atoms(self.atoms, ind1[0:1])
        atoms2 = remove_atoms(self.atoms, ind1[0:2])
        atoms3 = remove_atoms(self.atoms, ind1[0:3])

        # create double vacancies
        atoms4 = remove_atoms(self.atoms, np.hstack([ind1[0:1], ind2[0:1]]))
        atoms5 = remove_atoms(self.atoms, np.hstack([ind1[0:2], ind2[0:2]]))
        atoms6 = remove_atoms(self.atoms, np.hstack([ind1[0:3], ind2[0:3]]))

        # create mix vacancies
        i = np.hstack([ind1[0:3], ind2[0:1]])
        atoms7 = remove_atoms(self.atoms, i)
        i = np.hstack([ind1[0:3], ind2[0:2]])
        atoms8 = remove_atoms(self.atoms, i)
        i = np.hstack([ind1[0:2], ind2[1:2]])
        atoms9 = remove_atoms(self.atoms, i)
        i = np.hstack([ind2[0:2], ind1[1:2]])
        atoms10 = remove_atoms(self.atoms, i)

        l = [atoms1, atoms2, atoms3, atoms4, atoms5, atoms6, atoms7, atoms8, atoms9, atoms10]
        return l

    def create_x2_configs(self, dopant):
        assert self.center == 'x', 'center has to be S, Se or Te.'
        idx1 = self.get_inds(self.m_atoms)
        idx2 = self.get_inds(self.x_top_atoms)
        idx3 = self.get_inds(self.x_bottom_atoms)

        # ind has three elements
        ind = self.m_ind[idx1]  # len 3
        ind1 = self.x_top_ind[idx2]   # len 1
        ind2 = self.x_bottom_ind[idx3]   # len 1

        atoms1 = replace_atoms(self.atoms, ind[0:1], dopant)
        atoms2 = replace_atoms(self.atoms, ind[0:2], dopant)
        atoms3 = replace_atoms(self.atoms, ind[0:3], dopant)

        # not finished yet




    def crop_atoms(self, r=None):
        if r is None:
            r = self.a * 1.2
        L = self.atoms.cell.cellpar()[0]
        print(L)
        pts = self.atoms.positions[:, 0:2] - [L / 2., L / 2.]
        R = np.hypot(pts[:, 0], pts[:, 1])
        mask = R < r
        self.atoms = self.atoms[mask]
        return self

    def get_inds(self, atoms_selected):
        r = (np.sqrt(3) + 3) / 6 * self.a
        L = self.atoms.cell.cellpar()[0]
        pts = atoms_selected.positions[:, 0:2] - [L / 2., L / 2.]
        R = np.hypot(pts[:, 0], pts[:, 1])
        return np.where(R < r)[0]


    def show(self):
        show_atoms(self.atoms)
