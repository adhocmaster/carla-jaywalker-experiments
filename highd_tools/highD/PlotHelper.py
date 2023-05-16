import matplotlib.pyplot as plt
import seaborn as sns

# Apply the default theme
sns.set_theme()

class Histogram:

    @staticmethod
    def plotXY(data, x, y, xlabel="", ylabel=""):
        fig, ax = plt.subplots()
        ax.scatter(data[x].values, data[y].values)
        ax.set(title=f'Scatter Plot {xlabel} vs {ylabel}', xlabel=xlabel, ylabel=ylabel)
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
        g.set_axis_labels(xlabel if xlabel else col, "Count")
        g.set_titles(f"Distribution of {xlabel if xlabel else col}")
        plt.axvline(x=data[col].mean(), color='red')
        plt.show()

    @staticmethod
    def plot2MetricsDF(data, col1, col2, bins=10, title="", xlabel=""):
        g = sns.displot(data=data, x=col1, hue=col2, kde=True, stat="probability", bins=bins, palette="colorblind")
        g.set_titles(title if title else f"Distribution of {col1} by {col2}")
        plt.show()

    @staticmethod
    def plot2StackedMetricsDF(data, col1, col2, bins=10, title="", xlabel=""):
        g = sns.displot(data=data, x=col1, hue=col2, multiple="stack", stat="probability", bins=bins, palette="colorblind")
        g.set_titles(title if title else f"Distribution of {col1} by {col2}")
        plt.show()

    @staticmethod
    def plot2MetricsDFSep(data, col1, col2, bins=10, title="", xlabel=""):
        g = sns.displot(data=data, x=col1, col=col2, kde=True, stat="probability", bins=bins, palette="colorblind")
        g.set_axis_labels(xlabel if xlabel else col1, "probability")
        g.set_titles(title if title else f"Distribution of {col1} by {col2}")
        plt.show()







    # @staticmethod
    # def visualize_summary_statistics(tMeta, vehicle_type):
    #     # Filter by vehicle type
    #     vehicle_df = tMeta[tMeta['class'] == vehicle_type]

    #     # Define the columns to analyze
    #     columns_to_analyze = ['minDHW', 'minTHW', 'minTTC', 'minXVelocity', 'maxXVelocity', 'meanXVelocity']

    #     # Set up the subplots
    #     nplots = len(columns_to_analyze)
    #     fig, axes = plt.subplots(2, nplots, figsize=(nplots * 4, 10))
    #     fig.suptitle(f"Summary Statistics for {vehicle_type}s", fontsize=16)

    #     # Plot box plots and histograms for each column
    #     for i, col in enumerate(columns_to_analyze):
    #         sns.boxplot(y=col, data=vehicle_df, ax=axes[0, i], color='royalblue')
    #         sns.histplot(vehicle_df[col], kde=True, ax=axes[1, i], color='royalblue', alpha=0.6)
    #         axes[1, i].set_xlabel(col)

    #     # Adjust layout
    #     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    #     plt.show()




    


