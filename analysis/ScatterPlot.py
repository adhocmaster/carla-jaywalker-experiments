import matplotlib.pyplot as plt
import seaborn as sns
# Apply the default theme
sns.set_theme()


class ScatterPlot:

    
    @staticmethod
    def plot2MetricsDF(data, col1, col2, col1name, col2name):
        g = sns.scatterplot(data=data, x=col1, y=col2)
        plt.xlabel(col1name)
        plt.ylabel(col2name)
        plt.show()