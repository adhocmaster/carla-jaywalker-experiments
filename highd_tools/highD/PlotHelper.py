import matplotlib.pyplot as plt
import seaborn as sns

# Apply the default theme
sns.set_theme()

class Histogram:

    @staticmethod
    def plotXY(data, x, y, xlabel="", ylabel=""):
        X = data[x].values
        Y = data[y].values
        #  create a figure and axis
        fig, ax = plt.subplots()
        #  plot the data
        ax.scatter(X, Y)
        #  set the title
        ax.set_title(f'Scatter Plot {xlabel} vs {ylabel}')
        #  set the x and y labels
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        #  show the plot
        plt.show()
    
    @staticmethod
    def plotNormalizedMetricsDF(data, col, name, bins=10):
        g = sns.displot(data=data, x=col, kde=True, stat="probability", bins=bins)
        g.set_axis_labels(name, "Density")
        g.set_titles(f"Distribution of {name}")
        plt.show()

    @staticmethod
    def plotMetricsDF(data, col, xlabel="", bins=10, kde=True):
        g = sns.displot(data=data, x=col, kde=kde, bins=bins)
        if xlabel != "":
            g.set_axis_labels(xlabel, "Count")

        g.set_titles(f"Distribution of {xlabel}")
        plt.axvline(x=data[col].mean(), color='red')
        plt.show()

    
    @staticmethod
    def plot2MetricsDF(data, col1, col2, bins=10, title="", xlabel=""):
        g = sns.displot(data=data, x=col1, hue=col2, kde=True, stat="probability", bins=bins, palette="colorblind")
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"{title}")
        plt.show()

    @staticmethod
    def plot2StackedMetricsDF(data, col1, col2, bins=10, title="", xlabel=""):
        g = sns.displot(data=data, x=col1, hue=col2, multiple="stack", stat="probability", bins=bins, palette="colorblind")
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"{title}")
        plt.show()

    @staticmethod
    def plot2MetricsDFSep(data, col1, col2, bins=10, title="", xlabel=""):
        g = sns.displot(data=data, x=col1, col=col2, kde=True, stat="probability", bins=bins, palette="colorblind")

        if xlabel != "":
            g.set_axis_labels(xlabel, "probability")

        if title != "":
            g.set_titles(title)
        plt.show()


