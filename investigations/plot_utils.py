import matplotlib.pyplot as plt

def plot_results(x_values, series_dict, title, x_label, y_label, output_file=None):
    styles = ['-o', '--s', '-.^', ':D', '--x']  
    plt.figure()
    for (label, y_values), style in zip(series_dict.items(), styles):

        if len(x_values) >= 10 and 'o' in style or 's' in style or 'D' in style or 'x' in style:
            style = style.replace('o', '-').replace('s', '-').replace('D', '-').replace('x', '-')
        plt.plot(x_values, y_values, style, label=label)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    if output_file:
        plt.savefig(output_file)
    plt.show()
