#!/usr/bin/env python
# coding: utf-8

# Each tab is drawn by one script
from scatterplot import scatterplot_tab
from treemap import treemap_tab

import panel as pn

tabs = pn.Tabs(closable=False)

# Create each of the tabs
tab1 = scatterplot_tab()
tab2 = treemap_tab()


tabs.extend([
	('Scatterplot', tab1),
	('Treemap', tab2),
	])

tabs.servable()

