import MLPlots
from local_conf import get_conf
def plot_it(event):
    artemis = get_conf('artemis')
    Plot=MLPlots.MLplots(event)
    Plot.path_lightcurves(artemis+'data/')
    Plot.path_models(artemis+'model/')
    Plot.load_models()
    Plot.set_data_limits()
    Plot.load_data()
    Plot.find_survey()
    Plot.align_data()
    Plot.set_plot_limits()
    Plot.get_colors()
    script, div = Plot.plot_data()
    return script, div
