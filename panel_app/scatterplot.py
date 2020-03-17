#!/usr/bin/env python
# coding: utf-8

#import all required modules
from Bio import SeqIO
import pandas as pd
import numpy as np
from bokeh.layouts import column, row
from bokeh.models.widgets import Slider, Div, TextInput, Button
from bokeh.models import WheelZoomTool, Select, CDSView, BooleanFilter, ColumnDataSource, OpenURL, TapTool, HoverTool, CrosshairTool
from bokeh.io import export_svgs, output_notebook, show
from bokeh.plotting import figure, curdoc
from os.path import join, dirname
import panel as pn
import time



# Make a scatterplot and return the corresponding tab
def scatterplot_tab():

	#File input
	record_dict = SeqIO.index(join(dirname(__file__), "data/protein_sequences.fasta"), "fasta")
	df = pd.read_csv(join(dirname(__file__), 'data/input_data.csv'),sep="\t", header=0)
	df = df.fillna(0.0)

	cut_off = 2.0
	output_backend = "webgl"


	def create_figure(cut_off, df, output_backend):
		columns = sorted(df.columns[2:])

		#Initialize variables for data input
		xs = df[x.value].values
		ys = df[y.value].values
		geneid = df['AlternateID'].values
		desc = df['Annotation'].values
		x_title = x.value.lower()
		y_title = y.value.lower()

		#create a new column in df named seq storing protein sequences
		result={}
		for i in geneid:
			if i in record_dict.keys():
				result[i]= str(record_dict[i].seq)
			else: result[i] = str('*')
		df['seq']=result.values()
		seq = df['seq'].values

		data = {'x_values': xs,
			'y_values': ys,
			'fold_change': [(-x/y) if (x > y and y!=0) else (y/x) if (y>=x and x!=0) else 'NaN' for x,y in zip(xs,ys)],
			'GeneID': geneid,
			'Annotation': desc,
			'seq': seq
			}

		mysource = ColumnDataSource(data=data)

		#use CDSView function to determine a subset of significant genes for visualization
		significant_xy_view =  CDSView(source=mysource, 
					filters=[BooleanFilter([True if (
					(geneX > 0 and geneY > 0 and (abs(geneX/geneY) > cut_off)) 
					or (geneX > 0 and geneY > 0 and abs(geneY/geneX) > cut_off) and (geneX+geneY) > 10)
					else False for geneX,geneY in zip(mysource.data['x_values'],mysource.data['y_values'])])])

		# create a plot and style its properties
		kw = dict()
		kw['title'] = "%s vs %s" % (x_title, y_title)

		#make a plot
		p = figure(plot_height=500, plot_width=700, output_backend=output_backend, tools='pan,box_zoom,wheel_zoom,reset,save,tap', **kw)

		#make sure WheelZoomTool is activated by default
		p.toolbar.active_scroll = p.select_one(WheelZoomTool)
		p.xaxis.axis_label = x_title
		p.yaxis.axis_label = y_title
		p.yaxis.axis_label_text_font_size = '10pt'
		p.xaxis.axis_label_text_font_size = '10pt'
		p.yaxis.major_label_text_font_size = '10pt'
		p.xaxis.major_label_text_font_size = '10pt'
		p.title.text_font_size = '12pt'

		common_circle_kwargs = {
			'x': 'x_values',
			'y': 'y_values',
			'source': mysource,
			'hover_color': 'black'
			}

		p.circle(**common_circle_kwargs,color="skyblue", alpha=0.7, size=9, line_color="white")

		p.circle(**common_circle_kwargs,view= significant_xy_view,color="red", muted_alpha=0.1, 
				 legend_label='sig. genes', size=9, line_color="black")

		# Highlighting of genes using a substring in the gene annotation, if it is provided in the Textfield
		if desc_sel.value != "":
			selected = df[df.Annotation.str.contains(desc_sel.value, case=False) == True]
			p.circle(x=selected[x.value].values, y=selected[y.value].values,color="yellow", 
					 alpha=1.0, muted_alpha=0.1, legend_label='sel. genes', size=8, line_color="black")

		# Set autohide to true to only show the toolbar when mouse is over plot
		p.toolbar.autohide = True
		
		p.legend.title = 'Click to hide'
		p.legend.location = "bottom_right"
		p.legend.border_line_width = 1
		p.legend.border_line_color = "black"
		p.legend.border_line_alpha = 0.5

		# use the "seq" column of mysource to complete the URL
		# e.g. if the glyph at index 1 is selected, then @seq
		# will be replaced with mysource.data['seq'][1]
		url = "http://papers.genomics.lbl.gov/cgi-bin/litSearch.cgi?query=@seq&Search=Search"
		taptool = p.select(type=TapTool)
		taptool.callback = OpenURL(url=url)

		# Format the tooltip
		tooltips = [
			('GeneID','@GeneID'),
			('Annotation','@Annotation{safe}'),
			('fold change','@fold_change'),
			('FPKM (%s)' % (x_title),'@x_values'),
			('FPKM (%s)' % (y_title),'@y_values')]


		# Configure a renderer to be used upon hover
		hover_glyph = p.circle(**common_circle_kwargs,size=15, alpha=0,hover_fill_color='black', hover_alpha=0.5)

		# Add the custom HoverTool to the figure
		p.add_tools(HoverTool(tooltips=tooltips, renderers=[hover_glyph]))
		
		# Add the custom CrosshairTool to the figure
		p.add_tools(CrosshairTool(line_width=1))

		# Add interactivity to the legend
		p.legend.click_policy="hide"

		return p


	def update_data(attr, old, new):
		cut_off = float(sl.value)
		layout.children[1] = create_figure(cut_off, df, output_backend)


	x = Select(title='X-Axis: condition A', value='wt_0min', options=sorted(list(df.iloc[:,2:].columns)))
	x.on_change('value', update_data)

	y = Select(title='Y-Axis: condition B', value='wt_25min', options=sorted(list(df.iloc[:,2:].columns)))
	y.on_change('value', update_data)

	sl = Slider(start=0.0, end=10.0, value=cut_off, step=0.5, title='|fold change| \u003E')
	sl.callback_policy='mouseup'
	sl.on_change('value_throttled', update_data)

	desc_sel = TextInput(title="Gene annotation contains:")
	desc_sel.on_change('value', update_data)

	div = Div(text="""
		Interact with the widgets below to query a list of significant genes to plot.
		Hover over the circles to see more information about each gene.
		Click on the circle to get information from PaperBlast""")


	#add button for saving plot as .svg
	def button_handler():
		timestr = time.strftime("%Y%m%d-%H%M%S")
		p.output_backend = 'svg'
		export_svgs(p, filename="scatterplot{}.svg".format(timestr))
		p.output_backend = 'webgl'


	button = Button(label="Save as .svg", button_type="success")
	button.on_click(button_handler)

	p = create_figure(cut_off,df, output_backend)

	# Make a tab with the layout 
	controls = column( x, y, sl, desc_sel, button, width=200)
	layout = row(column(div,controls), p)


	tab = pn.pane.Bokeh(layout)

	return tab