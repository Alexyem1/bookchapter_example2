#!/usr/bin/env python
# coding: utf-8

from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import Select, ColumnDataSource
import pandas as pd
from bokeh.models.widgets import Div, DataTable, TableColumn, HTMLTemplateFormatter
from bokeh.layouts import widgetbox

import panel as pn
import os


# Make a treemap and return the corresponding tab
def treemap_tab():

	basepath = (os.sep.join(os.path.dirname(__file__).split(os.sep)[:0]))
	url = os.path.join(os.path.basename(basepath),"panel_app","static","")
	url_table = url+"topgo_"
	source = ColumnDataSource(dict(url = [url+"dhog_0min.png"]))
	df = pd.read_csv(os.path.join(basepath,"panel_app","data","input_data.csv"), sep="\t", header=0)
	df_table = pd.read_csv(url_table+"dhog_0min.txt", sep="\t", header=0, index_col=0)
	source_table = ColumnDataSource(df_table)

	def create_figure(source):
		p = figure(x_range=(0,1), y_range=(0,1), plot_width=800, plot_height=400,tools='wheel_zoom,reset,save', toolbar_location="below")
		p.image_url(url='url', x=0.5, y=0.5, h=1, w=1, anchor='center', source=source)
		p.xaxis.visible = None
		p.yaxis.visible = None
		return p
		
		
	
	def create_table(source_table):
		template_classicFisher ="""
			<div style="background:<%= 
				(function colorfromint(){
					if(value <= 0.01){
						return("green")}
					else{return("gray")}
					}()) %>; 
				color: white"> 
			<%= value %></div>
			"""
		template_term = """<span href="#" data-toggle="tooltip" title="<%= value %>"><%= value %></span>"""
		
		formatter1 =  HTMLTemplateFormatter(template=template_term)
		formatter2 =  HTMLTemplateFormatter(template=template_classicFisher)
		
			
		columns = [
				TableColumn(field="GO.ID", title="GO.ID", width = 100),
				TableColumn(field="Term", title="Term", width = 270, formatter=formatter1),
				TableColumn(field="classicFisher", title="classicFisher", width = 50, formatter=formatter2)
			]
		data_table = DataTable(source=source_table, columns=columns, width=520, height=500)

		return widgetbox(data_table)


	def update_data(attr, old, new):
		source = ColumnDataSource(dict(url = [url+str(x.value)+".png"]))
		source_table = ColumnDataSource(pd.read_csv(url_table+str(x.value)+".txt", sep="\t", header=0, index_col=0))
		layout1.children[1] = create_figure(source)
		layout2.children[1] = column(div, create_table(source_table))


	x = Select(title="Option:", value="dhog_0min", options=sorted(list(df.iloc[:,2:].columns)))
	x.on_change('value', update_data)
	
	div = Div(text="<b>TopGO results - significant BP processes</b>", style={'font-size': '100%', 'color': 'black'})

	controls = column(x, width=300)
	layout1 = column(controls, create_figure(source))
	layout2 = row(layout1, column(div,create_table(source_table)))

	# Make a tab with the layout 
	tab = pn.pane.Bokeh(layout2)

	return tab
