import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.image import imread

import numpy as np

class Spatial():

    @staticmethod
    def pies(
        df,
        *,
        image=None,                     # str path, numpy array, or None
        map_extent=None,                # (map_x1, map_x2, map_y1, map_y2), required if image is not None
        x_col="X",
        y_col="Y",
        value_cols=("oil", "water"),
        label_col="wellname",
        colors=None,
        alpha=0.7,
        figsize=(15, 5),
        flipud=True,
        origin="lower",
        radius_mode="quartic-root",
        radius_scale=1.0,
        scale_factor=500_000,
        edgecolor="black",
        edge_linewidth=0.5,
        circle_alpha=0.3,
        text_kwargs=None,
        show=True,
        save_path=None,
        dpi=300
    ):
        """
        Plot per-row pie charts on an image or on a white background if image=None.
        """

        if image is not None:
            # --- image loading ---
            if isinstance(image, str):
                img = imread(image)
            else:
                img = image
            if flipud:
                img = np.flipud(img)

            img_h, img_w = img.shape[0], img.shape[1]
            map_x1, map_x2, map_y1, map_y2 = map_extent
            map_deltax = float(map_x2 - map_x1)
            map_deltay = float(map_y2 - map_y1)

            # --- figure & axes ---
            fig, ax = plt.subplots(figsize=figsize)
            ax.imshow(img, origin=origin)
            ax.set_xlim([0, img_w])
            ax.set_ylim([0, img_h])

            coord_to_img = lambda x, y: (
                (x - map_x1) / map_deltax * img_w,
                (y - map_y1) / map_deltay * img_h
            )
        else:
            # No image: white background, coordinates directly in map units
            if map_extent is None:
                raise ValueError("map_extent must be provided when image=None")

            map_x1, map_x2, map_y1, map_y2 = map_extent
            fig, ax = plt.subplots(figsize=figsize)
            ax.set_facecolor("white")
            ax.set_xlim(map_x1, map_x2)
            ax.set_ylim(map_y1, map_y2)

            coord_to_img = lambda x, y: (x, y)

        if text_kwargs is None:
            text_kwargs = dict(ha="center", va="center", color="black", fontsize=6)

        # --- per-row pies ---
        for _, row in df.iterrows():
            vals = np.array([row[col] for col in value_cols], dtype=float)
            total = np.sum(vals)
            if total <= 0 or not np.isfinite(total):
                continue

            fracs = vals / total

            # radius scaling
            if radius_mode == "quartic-root":
                radius = (np.sqrt(scale_factor) * (total ** 0.25)) / 100.0
            elif radius_mode == "sqrt":
                radius = np.sqrt(total)
            else:
                raise ValueError("radius_mode must be 'quartic-root' or 'sqrt'")
            radius *= float(radius_scale)


            if colors is None:
                slice_colors = None
            else:
                slice_colors = []
                for c in colors:
                    r, g, b, _ = to_rgba(c)
                    slice_colors.append((r, g, b, alpha))

            # transform coords
            cx, cy = coord_to_img(row[x_col], row[y_col])

            # draw pie
            ax.pie(
                fracs,
                radius=radius,
                colors=slice_colors,
                startangle=90,
                center=(cx, cy),
                wedgeprops=dict(linewidth=0.0)
            )

            # label
            if label_col is not None and label_col in df.columns:
                ax.text(cx, cy, str(row[label_col]), **text_kwargs)

            # outline circle
            circle = plt.Circle((cx, cy), radius,
                                edgecolor=edgecolor,
                                fill=False,
                                alpha=circle_alpha,
                                linewidth=edge_linewidth)
            ax.add_artist(circle)

        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])

        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        if show:
            plt.show()

        return fig, ax

if __name__ == "__main__":

    import pandas as pd

    data = {
     "wellname": ["NFD_1795", "NFD_2118","NFD_2226_S1", "NFD_2271", "NFD_2680", "NFD_1661"],
            "X": [ 494071.76,  493891.73,  494148.5621,  493431.01,  494558.86,  494093.34],
            "Y": [4453174.78, 4453090.25, 4453086.194 , 4453237.29, 4453124.6 , 4453097.31],
          "oil": [15811, 33903, 19752,  2496, 1650, 73228],
        "water": [    0,     0,     0, 18211,    0,  1922],
    }

    frame = pd.DataFrame(data)

    frame['total'] = frame['oil'] + frame['water']

    frame['oil_ratio'] = frame['oil']/frame['total']
    frame['water_ratio'] = frame['water']/frame['total']

    fig, ax = Map.pies(
        frame,
        image=None,
        map_extent=(493_000, 494_800, 4_451_700, 4_454_100),
        value_cols=("oil","water"),
        colors=[(144/255, 238/255, 144/255), (0/255, 105/255, 148/255)],
        alpha=0.7,
        radius_mode="quartic-root",  # replicates your original scaling
        scale_factor=500_000,        # same as 50_0000 in your script
        radius_scale=1.0,            # tweak if pies feel too big/small
        text_kwargs=dict(ha='center', va='center', color='black', fontsize=6)
    )
