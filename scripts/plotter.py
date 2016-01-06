import MLPlots

def plot_it(event):
	
	Plot=MLPlots.MLplots(event)

 	Plot.path_lightcurves('/home/Tux/ytsapras/Data/RoboNet/ARTEMiS/data/')
	Plot.path_models('/home/Tux/ytsapras/Data/RoboNet/ARTEMiS/model/')
	Plot.load_data()
	Plot.load_models()
	Plot.find_survey()
	Plot.align_data()
	Plot.set_limits()
	Plot.get_colors()	
	script, div = Plot.plot_data()
	return script, div


def main():
	
	Plot=MLPlots.MLplots('OB150808')

 	Plot.path_lightcurves('/home/Tux/ytsapras/Data/RoboNet/ARTEMiS/data/')
	Plot.path_models('/home/Tux/ytsapras/Data/RoboNet/ARTEMiS/model/')
	Plot.load_data()
	Plot.load_models()
	Plot.find_survey()
	Plot.align_data()
	Plot.set_limits()
	Plot.get_colors()	

	Plot.plot_data()
	#

if __name__ == "__main__":
    main()
