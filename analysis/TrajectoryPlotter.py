import matplotlib.pyplot as plt
import seaborn as sns
# Apply the default theme
sns.set_theme()
palate = sns.color_palette("hls", 16)
sns.set_palette(palate)
# sns.set_palette("Paired")


class TrajectoryPlotter:

    @staticmethod
    def plot2MetricsDF(data, col1, col2, col1name, col2name):
        g = sns.relplot(data=data, x=col1, y=col2, kind="line", hue="episode", ci=None)
        plt.xlabel(col1name)
        plt.ylabel(col2name)
        plt.show()