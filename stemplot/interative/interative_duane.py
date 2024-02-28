import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path

from ..colors._colors import colors_from_lbs


def pca(X, n_components=2):
    pca_model = PCA(n_components=n_components)
    X_pca = pca_model.fit_transform(X)
    return X_pca

class InteractiveAnnotation:

    def __init__(self, fig, X, lbs, pts, **kwargs):
        self.fig = fig
        self.ax1 = fig.axes[0]
        self.ax2 = fig.axes[1]

        self.X = X
        self.lbs = lbs
        self.pts = pts
        self.X1 = self.X[self.lbs == 0]
        self.X2 = self.X[self.lbs == 1]
        self.lbs1 = self.lbs[self.lbs == 0]
        self.lbs2 = self.lbs[self.lbs == 1]
        self.pts1 = self.pts[self.lbs == 0]
        self.pts2 = self.pts[self.lbs == 1]


        self.xy1 = pca(self.X1.rotinv().select(0))
        self.xy2 = pca(self.X2.rotinv().select(0))

        self.colors1 = colors_from_lbs(self.lbs1)
        self.colors2 = colors_from_lbs(self.lbs2)

        self.path_collection1 = self.ax1.scatter(self.xy1[:, 0], self.xy1[:, 1], c=self.colors1, **kwargs)
        self.path_collection2 = self.ax2.scatter(self.xy2[:, 0], self.xy2[:, 1], c=self.colors2, **kwargs)
        self.ax1.axis('equal')
        self.ax2.axis('equal')

        self.ind1 = None
        self.ind2 = None

        self.X1_selected = None
        self.X2_selected = None
        self.pts1_selected = None
        self.pts2_selected = None

        self.lasso1_active = False
        self.lasso2_active = False

        self.lasso1 = LassoSelector(self.ax1, onselect=self.onselect1)
        self.lasso2 = LassoSelector(self.ax2, onselect=self.onselect2)

        self.press = self.fig.canvas.mpl_connect("key_press_event", self.press_key)

        self.X1_train = []
        self.X2_train = []
        self.y1_train = []
        self.y2_train = []

        self.num_clusters1 = 0
        self.num_clusters2 = 0


    def onselect1(self, event):
        path = Path(event)
        self.ind1 = np.nonzero(path.contains_points(self.xy1))[0]
        if self.ind1.size != 0:
            self.lasso1_active = True
            self.lasso2_active = False
            self.X1_selected = self.X1[self.ind1]
            self.pts1_selected = self.pts1[self.ind1]

    def onselect2(self, event):
        path = Path(event)
        self.ind2 = np.nonzero(path.contains_points(self.xy2))[0]
        if self.ind2.size != 0:
            self.lasso1_active = False
            self.lasso2_active = True
            self.X2_selected = self.X2[self.ind2]
            self.pts2_selected = self.pts2[self.ind2]

    def press_key(self, event):
        if event.key == "enter":
            if self.lasso1_active:
                self.X1_train.append(self.X1_selected)
                self.y1_train.append(np.array([self.num_clusters1]*len(self.X1_selected)))
                self.num_clusters1 += 1
                print("One cluster has been created.")
            if self.lasso2_active:
                self.X2_train.append(self.X2_selected)
                self.y2_train.append(np.array([self.num_clusters2] * len(self.X2_selected)))
                self.num_clusters2 += 1
                print("One cluster has been created.")
            else:
                pass
        if event.key == 'shift':
            X1_train = np.vstack(self.X1_train)
            X2_train = np.vstack(self.X2_train)
            y1_train = np.hstack(self.y1_train)
            y2_train = np.hstack(self.y2_train)
            np.save('X1_train.npy', X1_train)
            np.save('X2_train.npy', X2_train)
            np.save('y1_train.npy', y1_train)
            np.save('y2_train.npy', y2_train)
            print("Created training datasets have beed saved.")

def interactive_annotation(X, lbs, pts, **kwargs):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    app = InteractiveAnnotation(fig, X, lbs, pts, **kwargs)
    return app