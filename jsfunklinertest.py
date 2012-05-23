#!/usr/bin/python

import jsfunkliner
import unittest
import sys

class TestBasic(unittest.TestCase):
	def test_idempotent(self):
		input="var x = 1;"
		expected="var x = 1;"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)

	def test_external(self):
		input="window.alert('Test')"
		expected="window.alert('Test')"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)

	def test_singlecall(self):
		library="function log(message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallelse(self):
		library="function log(message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallbrace(self):
		library="function log(message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallbraceelse(self):
		library="function log(message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } else { window.alert(message); } }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); } else { window.alert(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlereturn(self):
		library="function add(one, two) { return one + two; }"
		input="var x = add(1,2);"
		expected="var x = (1 + 2);"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallmultifunction(self):
		library="function log(type, message) { var finalmessage = type + ': ' + message; if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(finalmessage); else window.alert(finalmessage) };"
		input='log("Test", "This is a test")'
		expected="var finalmessage = \"Test\" + ': ' + \"This is a test\"; if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(finalmessage); else window.alert(finalmessage)"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallmultifunction2(self):
		library="function log(time, type, message) { var finalmessage = type + ': ' + message; finalmessage = time + finalmessage; if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(finalmessage); else window.alert(finalmessage) };"
		input='log(30, "Test", "This is a test")'
		expected="var finalmessage = \"Test\" + ': ' + \"This is a test\"; finalmessage = 30 + finalmessage; if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(finalmessage); else window.alert(finalmessage)"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_doublecallinline(self):
		library="function add(one, two) { return one + two; }"
		input="var final = add(2,3) + add(4,1)"
		expected="var final = (2 + 3) + (4 + 1)"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_multicallinline(self):
		library="function add(one, two) { return one + two; }\nfunction sub(one, two) { return one - two; }"
		input="var final = add(2,3) + sub(4,1)"
		expected="var final = (2 + 3) + (4 - 1)"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallretval(self):
		library="function square(one) { var two = one; return one * two; }"
		input="var final = square(2)"
		expected="var retfinal0 = undefined;\nvar two = 2; retfinal0 = 2 * two;\nvar final = retfinal0"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_multicallretval(self):
		library="function square(one) { var two = one; return one * two; }\nfunction double(one) { var double = one * 2; return double; }"
		input="var final = square(2) + double(3)"
		expected="var retfinal0 = undefined;\nvar two = 2; retfinal0 = 2 * two;\nvar retfinal1 = undefined;\nvar double = 3 * 2; retfinal1 = double;\nvar final = retfinal0 + retfinal1"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_doublecallretval(self):
		library="function square(one) { var two = one; return one * two; }"
		input="var final = square(2) + square(3)"
		expected="var retfinal0 = undefined;\nvar two = 2; retfinal0 = 2 * two;\nvar retfinal1 = undefined;\nvar two = 3; retfinal1 = 3 * two;\nvar final = retfinal0 + retfinal1"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

class TestUnrolling(unittest.TestCase):
	def test_funloop(self):
		input="for (var i=0; i<2; i+=1) log(i);"
		expected="log(0);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloop2(self):
		input="for (var i=0; i<2; i=i+1) log(i);"
		expected="log(0);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloop3(self):
		input="for (var i=0; i<3; i=1+i) log(i);"
		expected="log(0);\nlog(1);\nlog(2);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloop4(self):
		input="for (var i=0; i<5; i=i+3) log(i);"
		expected="log(0);\nlog(3);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloop5(self):
		input="for (var i=0; i<2; i++) log(i);"
		expected="log(0);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloop6(self):
		input="for (var i=0; i<2; ++i) log(i);"
		expected="log(0);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_unfunloop(self):
		input="for (var i=2; i>0; i-=1) log(i);"
		expected="log(2);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_unfunloop2(self):
		input="for (var i=2; i>0; i=i-1) log(i);"
		expected="log(2);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_unfunloop3(self):
		input="for (var i=5; i>0; i=i-3) log(i);"
		expected="log(5);\nlog(2);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_unfunloop4(self):
		input="for (var i=2; i>0; i--) log(i);"
		expected="log(2);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_unfunloop5(self):
		input="for (var i=2; i>0; --i) log(i);"
		expected="log(2);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloopafter(self):
		input="for (var i=0; i<2; i+=1) log(i);\nalert('hi')"
		expected="log(0);\nlog(1);\nalert('hi')"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funnyloopafter(self):
		input="for (var i=0; i<2; i+=1) log(i) ;\nalert('hi')"
		expected="log(0) ;\nlog(1) ;\nalert('hi')"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloopblock(self):
		input="for (var i=0; i<2; i+=1) {log(i);}"
		expected="log(0);\nlog(1);"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funnyloopblock(self):
		input="for (var i=0; i<2; i+=1) {log( i) ;}"
		expected="log( 0) ;\nlog( 1) ;"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_doublefunloopblock(self):
		input="for (var i=0; i<2; i+=1) { log(i); window.alert(i); }"
		expected="log(0); window.alert(0); \nlog(1); window.alert(1); "
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)
	def test_funloopblockafter(self):
		input="for (var i=0; i<2; i+=1) {log(i);}\nalert('hi')"
		expected="log(0);\nlog(1);\nalert('hi')"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)

class TestVar(unittest.TestCase):
	def test_varsinglecall(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varsinglecallelse(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varsinglecallbrace(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_globalsinglecall(self):
		library="log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_globalsinglecallelse(self):
		library="log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_globalsinglecallbrace(self):
		library="log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_windowsinglecall(self):
		library="window.log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_windowsinglecallelse(self):
		library="window.log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_windowsinglecallbrace(self):
		library="window.log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } }"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varwindowsinglecall(self):
		library="log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='window.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varwindowsinglecallelse(self):
		library="log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) }"
		input='window.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varlocalwindowsinglecallbrace(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } }"
		input='window.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varlocalwindowsinglecall(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='window.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varlocalwindowsinglecallelse(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) }"
		input='window.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varwindowsinglecallbrace(self):
		library="log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } }"
		input='window.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

class TestObject(unittest.TestCase):
	def test_objectsinglecall(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } }"
		input='object.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_objectsinglecallelse(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) } }"
		input='object.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_objectsinglecallbrace(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } } }"
		input='object.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

if __name__ == '__main__':
	if len(sys.argv)>1:
		found = False
		wanted=sys.argv[1]
		suitename = None
		case = None
		for suitename in globals():
			if suitename[0:4] == 'Test':
				if hasattr(globals()[suitename], wanted):
					found = True
					case = globals()[suitename](wanted)
					case.run()
					break
		if not found:
			print("Invalid testcase: "+sys.argv[1])
	else:
		unittest.main()
