#!/usr/bin/python

import cgi
import cgitb
import jsfunkliner
import jsparser
import sys

jsdata={
	'library': {
		'data':'',
		'olddata':'',
		'editable':True,
		'rows':10,
		'label':'Library'
	},
	'snippet': {
		'data':'',
		'olddata':'',
		'editable':True,
		'rows':3,
		'label':'Snippet'
	},
	'output': {
		'data':'',
		'olddata':'',
		'editable':False,
		'rows':10,
		'label':'Output'
	},
	'nextoutput': {
		'data':'',
		'olddata':'',
		'editable':False,
		'rows':10,
		'label':'Next Output'
	}
}
error = ''

def printContainer(attribute):
	label=jsdata[attribute]['label']
	rows=jsdata[attribute]['rows']
	data=jsdata[attribute]['data']
	editable=jsdata[attribute]['editable']
	readonly = 'readonly' if not editable else ''
	print('<textarea class="oldinput" name="old%s" rows="%s" cols="50" %s>%s</textarea>'%(attribute, rows, readonly, data))
	print('<div class="container">')
	print('<span class="label">%s</span>'%label)
	print('<textarea name="%s" rows="%s" cols="50" %s>%s</textarea>'%(attribute, rows, readonly, data))
	print('</div>')

def printPage():
	print("""Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style type="text/css">
.container {
	position: relative;
}
.oldinput {
	display: none;
}
span.label {
	position: absolute;
	top: 5px;
	right: 5px;
	opacity: 20%;
}
</style>
</head>
<body>
""")
	print('<p>Use this page to inline Javascript</p>')
	print('<form action="" method="POST">')
	printContainer('library')
	printContainer('snippet')
	if error:
		print('<p class="error">A syntax error occurred:<br>')
		print(error.replace('\n','<br />') + "</p>")
	if jsdata['output']['data']:
		printContainer('output')
	if jsdata['nextoutput']['data']:
		printContainer('nextoutput')
	print('<input type="submit" name="single" value="Inline Once"></input>')

# handle input
data=cgi.FieldStorage();
for attr in ['library', 'snippet', 'output', 'nextoutput']:
	jsdata[attr]['data'] = data.getfirst(attr, '')
	jsdata[attr]['olddata'] = data.getfirst('old' + attr, '')
cmd_inlinesingle = data.getfirst('single')

if cmd_inlinesingle:
	try:
		# if the yuser has changed the input, reset the output
		if jsdata['library']['data'] != jsdata['library']['olddata'] or \
		   jsdata['snippet']['data'] != jsdata['snippet']['olddata']:
			jsdata['output']['data'] = ''
			jsdata['nextoutput']['data'] = ''

		# if there is a nextoutput, move it to the output
		if jsdata['nextoutput']['data']:
			jsdata['output']['data'] = jsdata['nextoutput']['data']
		# find the latest snippet to do
		snippet = jsdata['output']['data'] if jsdata['output']['data'] else jsdata['snippet']['data']
		# inline it
		output = jsfunkliner.inlineSingle(snippet, jsdata['library']['data'])
		# save it to the right place
		if not jsdata['output']['data']:
			jsdata['output']['data'] = output
		else:
			jsdata['nextoutput']['data'] = output
	except jsparser.SyntaxError_:
		error = sys.exc_info()[1].message
		jsdata['output']['data'] = ''
		jsdata['nextoutput']['data'] = ''
	except:
		cgitb.handler()

# display output
printPage()
