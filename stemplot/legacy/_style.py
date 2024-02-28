from matplotlib.patches import ArrowStyle, ConnectionStyle

# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Arrow styles
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

simple_arrow = ArrowStyle.Simple(head_length=1, head_width=1, tail_width=0.4)
double_arrow = ArrowStyle.CurveFilledAB(head_length=1, head_width=0.5)
flexible_arrow =  ArrowStyle.CurveFilledB(head_length=1, head_width=0.5)


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Arrow connection styles
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
connection_line = ConnectionStyle.Arc3(rad=0.)

c1 = ConnectionStyle.Angle3(angleA=90, angleB=0)
c2 = ConnectionStyle.Angle3(angleA=0, angleB=90)


c3 = ConnectionStyle.Angle(angleA=90, angleB=0, rad=5)
c4 = ConnectionStyle.Angle(angleA=0, angleB=90, rad=5)

rc1 = {'xtick.direction': 'in',
       'xtick.major.size': 2,
       'xtick.major.width': 0.5,
       'xtick.minor.size': 1,
       'xtick.minor.width': 0.5,
       'xtick.minor.visible': True,
       'xtick.labelsize': 6,

       'ytick.direction': 'in',
       'ytick.major.size': 2,
       'ytick.major.width': 0.5,
       'ytick.minor.size': 1,
       'ytick.minor.width': 0.5,
       'ytick.minor.visible': True,
       'ytick.labelsize': 6,

       # x and y labelsize
       'axes.labelsize': 10,

       # Set line widths
       'axes.linewidth': 0.5,
       'grid.linewidth': 0.5,
       'lines.linewidth': 1.,

       # Remove legend frame
       'legend.frameon': False,
       'legend.fontsize': 8,

       'axes.unicode_minus': True,
       'mathtext.fontset': 'dejavusans',  # Should be 'dejavusans' (default),
       # 'dejavuserif', 'cm' (Computer Modern), 'stix',
       # 'stixsans'

       #'text.usetex': True,
       #'text.latex.preamble': r"\usepackage{amsmath}"
       }

