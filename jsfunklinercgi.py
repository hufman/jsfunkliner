#!/usr/bin/python

import cgi
import jsfunkliner
import jsparser
import sys
import datetime
import pprint

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
	print('<textarea id="%s" name="%s" rows="%s" cols="50" %s>%s</textarea>'%(attribute, attribute, rows, readonly, data))
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
#feedbackcontainer {
	visibility: hidden;
}
</style>
<script type="text/javascript">
var loader=function() {
	var examples=[{
			'desc':'Blank',
			'library':'',
			'snippet':''
	},{
			'desc':'Simple Test',
			'library':'function foo(){\\n alert("bar");\\n}',
			'snippet':'foo();'
	},{
			'desc':'Two Level Object',
			'library':'object = function(){};\\nobject.prototype={\\n log : function(message) {\\n  this.reallog(message);\\n },\\n reallog: function (message) {\\n  if (typeof(console) != "undefined" && typeof(console.log) != "undefined")\\n   console.log(message);\\n  else\\n   window.alert(message)\\n }\\n};\\nobject2 = new object();',
			'snippet':'object2.log("This is a test")'
	},{
			'desc':'Single Returns',
			'library':'function add(one, two) { return one + two; }\\nfunction sub(one, two) { return one - two; }',
			'snippet':'var final = add(2,3) + add(3,5) + sub(8,1)'
	},{
			'desc':'Retval Returns',
			'library':'function square(one) {\\n var two = one;\\n return one * two;\\n}',
			'snippet':'var final = square(2) + square(3) + square(4)'
	},{
			'desc':'Forloop unrolling',
			'library':'',
			'snippet':'var sum = 0;\\nfor (var i=0; i<7; i++) { sum = sum + i; }'
	},{
			'desc':'Advanced objects',
			'library':'myobject = function(){};\\nmyobject.prototype={reallog: function (message) {\\n if (typeof(console) != "undefined" && typeof(console.log) != "undefined")\\n  console.log(message)\\n }\\n};',
			'snippet':'log = function(logger /*:myobject*/ , message) {\\n logger.reallog(message);\\n}'
	},{
			'desc':'Function switch',
			'library':'steps = {\\n\\t0:function(){\\n\\t\\tthis.increment(1)},\\n\\t1:function(){\\n\\t\\tthis.increment(2)},\\n\\t2:function(){\\n\\t\\tthis.decrement(3)}\\n}',
			'snippet':'for (var step = 0; step<steps.length; step++) {\\n\\tsteps[step].call(datablob);\\n}'
	}];

	var box = document.getElementById('examples');
	if (!box) return;
	var library = document.getElementById('library');
	var snippet = document.getElementById('snippet');

	for (var i=0; i<examples.length; i++) {
		var curexample = examples[i]
		var mine = document.createElement('option');
		mine.libraryContent = curexample['library'];
		mine.snippetContent = curexample['snippet'];
		mine.appendChild(document.createTextNode(curexample['desc']));
		box.appendChild(mine);
	}
	var changed = function(e) {
		var index = this.selectedIndex;
		var cur = this.childNodes[index];
		library.value = cur.libraryContent;
		snippet.value = cur.snippetContent;
	}

	box.onchange = changed;
	
	document.getElementById('leavefeedback').onclick = function(e) {
		document.getElementById('feedbackcontainer').style.visibility='visible';
	};
}
if (window.attachEvent) {window.attachEvent('onload', loader);}
else if (window.addEventListener) {window.addEventListener('load', loader, false);}
else {document.addEventListener('load', loader, false);}

</script>
</head>
<body>
<p>Use this page to inline Javascript</p>
<p>Any code in the Snippet box that calls functions in the Library box will have the function's body inlined</p>
<p>
Features:
<ul>
<li>Function expanding, with argument replacing</li>
<li>For loop unrolling</il>
<li>Subscript function calls get converted to switch statements [ object[selector]() ]</li>
</ul>
</p>
<p>
Limitations:
<ul>
<li>Does not handle closures</li>
<li>Can not handle multiple returns</li>
<li>Recursive functions will continually expand</li>
<li>Incorrect results when passing an incrementing variable through a call [ blahfunction(a++) ]</li>
</ul>
</p>

""")
	print('<p>Examples: <select id="examples"></select></p>')
	print('<form action="" method="POST">')
	printContainer('library')
	printContainer('snippet')
	if error:
		print('<p class="error">An error occurred:<br>')
		print(error.replace('\n','<br />') + "</p>")
	if jsdata['output']['data']:
		printContainer('output')
	if jsdata['nextoutput']['data']:
		printContainer('nextoutput')
	print('<input type="submit" name="single" value="Inline Once"></input>')
	print("""
<button id="leavefeedback" type="button">Send Feedback</button>
<div id="feedbackcontainer">
<p><label for="feedback_name">Name:</label> <input id="feedback_name" name="name"></input></p>
<p><label for="feedback_comment">Comment:</label>
<textarea id="feedback_comment" name="comment" cols="50" rows="7"></textarea></p>
<input type="submit" name="feedback" value="Submit Feedback"></input>
</div>
""")


def saveInputLog(name, jsdata, other=None):
	timestamp=datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%S.%f')
	name='inliner-%s-%s'%(name, timestamp)
	output = file('/var/log/inliner/%s'%name, 'w')

	pp = pprint.PrettyPrinter(stream=output)
	for attr in ['library', 'snippet', 'output', 'nextoutput']:
		pp.pprint({attr+"old": jsdata[attr]['olddata']})
		pp.pprint({attr: jsdata[attr]['data']})
	if other:
		pp.pprint(other)
	output.close()


# handle input
data=cgi.FieldStorage();
for attr in ['library', 'snippet', 'output', 'nextoutput']:
	jsdata[attr]['data'] = data.getfirst(attr, '')
	jsdata[attr]['olddata'] = data.getfirst('old' + attr, '')
cmd_inlinesingle = data.getfirst('single')
cmd_feedback = data.getfirst('feedback')

if cmd_inlinesingle:
	saveInputLog('input', jsdata)
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
		saveInputLog('output', jsdata)
	except jsparser.SyntaxError_:
		error = sys.exc_info()[1].message
		jsdata['output']['data'] = ''
		jsdata['nextoutput']['data'] = ''
	except:
		error = "I will be looking into why this happened.\nThanks for helping my code!"
		saveInputLog('error', jsdata)
	# display output
	printPage()

elif cmd_feedback:
	feedback={
		'name': data.getfirst('name'),
		'comment': data.getfirst('comment')
	}
	saveInputLog('feedback', jsdata, {'feedback':feedback})
	# display output
	printPage()
	print('<p>Thanks! Your feedback has been saved</p>')

else:
	printPage();
