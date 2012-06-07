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

	def test_callsubarg(self):
		input="window.alert(this.sub[2])"
		expected="window.alert(this.sub[2])"
		output=jsfunkliner.inlineSingle(input, '')
		self.assertEqual(expected, output)

	def test_nullreturn(self):
		library="function log(message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); return}"
		input='log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); "
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecalldot(self):
		library="function log(message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='log(this.message)'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message)"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallsub(self):
		library="function log(message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }"
		input='log(this.message[0])'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message[0])"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecallincrement(self):
		library="function log(message, message2) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message, message2) }"
		input='log(this.message++, ++this.message)'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message++, ++this.message)"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_singlecalldecrement(self):
		library="function log(message, message2) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message, message2) }"
		input='log(this.message--, --this.message)'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message--, --this.message)"
		output=jsfunkliner.inlineSingle(input, library)
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

	def test_triplecallinline(self):
		library="function add(one, two) { return one + two; }"
		input="var final = add(2,3) + add(4,1) + add(40,12)"
		expected="var final = (2 + 3) + (4 + 1) + (40 + 12)"
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

	def test_triplecallretval(self):
		library="function square(one) { var two = one; return one * two; }"
		input="var final = square(2) + square(3) + square(4)"
		expected="var retfinal0 = undefined;\nvar two = 2; retfinal0 = 2 * two;\nvar retfinal1 = undefined;\nvar two = 3; retfinal1 = 3 * two;\nvar retfinal2 = undefined;\nvar two = 4; retfinal2 = 4 * two;\nvar final = retfinal0 + retfinal1 + retfinal2"
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
	def test_notfunloop(self):
		library="function add(one, two) { return one + two; }"
		input="var x = 0; for (var i=0; i<4; i=i*2) { x = add(x, i) }"
		expected="var x = 0; for (var i=0; i<4; i=i*2) { x = (x + i) }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_notfunloop2(self):
		library="function add(one, two) { return one + two; }"
		input="var x = 0; for (var i=0; i<4; i=i*2) { x = add(x, i) + add(x, i) }"
		expected="var x = 0; for (var i=0; i<4; i=i*2) { x = (x + i) + (x + i) }"
		output=jsfunkliner.inlineSingle(input, library)
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
		
	def test_objectsinglecallthis(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message + message) } }"
		input='object.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(object.message + \"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
		
	def test_objectsinglecallthiscall(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message + message) } }"
		input='object.log.call(other,"This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(other.message + \"This is a test\")"
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

class TestAssignment(unittest.TestCase):
	def test_varasssinglecall(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }; var log2 = log"
		input='log2("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varasssinglecallelse(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) }; var log2 = log"
		input='log2("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_varasssinglecallbrace(self):
		library="var log = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } };  var log2 = log"
		input='log2("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_objectasssinglecall(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } }; var object2 = object"
		input='object2.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_objectasssinglecallelse(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) } }; var object2 = object"
		input='object2.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_objectasssinglecallbrace(self):
		library="var object={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } } }; var object2 = object"
		input='object2.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

class TestNewObject(unittest.TestCase):
	def test_newobjectsinglecall(self):
		library="object = function(){}; object.prototype={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } }; object2 = new object()"
		input='object2.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_newobjectsinglecallelse(self):
		library="object = function(){}; object.prototype={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) } }; object2 = new object()"
		input='object2.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

	def test_newobjectsinglecallbrace(self):
		library="object = function(){}; object.prototype={log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } } }; object2 = new object()"
		input='object2.log("This is a test")'
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

class TestNewThis(unittest.TestCase):
	def test_newthisobjectsinglecall(self):
		library="object = function(){}; object.prototype={log : function(message) {this.reallog(message);}, reallog : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } }; object2 = new object()"
		input='object2.log("This is a test")'
		expected='object2.reallog("This is a test")'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\")"
		output=jsfunkliner.inlineSingle(output, library)
		self.assertEqual(expected, output)

	def test_newthisobjectsinglecallelse(self):
		library="object = function(){}; object.prototype={log : function(message) {this.reallog(message);}, reallog: function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); else window.alert(message) } }; object2 = new object()"
		input='object2.log("This is a test")'
		expected='object2.reallog("This is a test")'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(\"This is a test\"); else window.alert(\"This is a test\")"
		output=jsfunkliner.inlineSingle(output, library)
		self.assertEqual(expected, output)

	def test_newthisobjectsinglecallbrace(self):
		library="object = function(){}; object.prototype={log : function(message) {this.reallog(message);}, reallog : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(message); } } }; object2 = new object()"
		input='object2.log("This is a test")'
		expected='object2.reallog("This is a test")'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
		expected="if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') { console.log(\"This is a test\"); }"
		output=jsfunkliner.inlineSingle(output, library)
		self.assertEqual(expected, output)

class TestSwitch(unittest.TestCase):
	def test_switch(self):
		library="cases = {log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); } }"
		input='var select="log"; cases[select]();'
		expected="var select=\"log\"; switch (select) {\n\tcase \"log\":\nif (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);\n\tbreak;\n\tdefault:\n\tcases[select]();\n}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_deeperswitch(self):
		library="cases = {log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); } }"
		input='var select="log"; window.cases[select]();'
		expected="var select=\"log\"; switch (select) {\n\tcase \"log\":\nif (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);\n\tbreak;\n\tdefault:\n\twindow.cases[select]();\n}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_nestedswitchcall(self):
		library="object = {cases:{log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); } }}"
		input='var select="log"; object.cases[select]();'
		expected="var select=\"log\"; switch (select) {\n\tcase \"log\":\nif (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);\n\tbreak;\n\tdefault:\n\tobject.cases[select]();\n}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_switchret(self):
		library="cases = {add : function (one, two) { return one + two; }}"
		input='var select="add";\nvar x = cases[select](1, 2);'
		expected="var select=\"add\";\nswitch (select) {\n\tcase \"add\":\nvar retx0 = undefined;\nretx0 = 1 + 2;\n\tbreak;\n\tdefault:\n\tcases[select](1, 2);\n}\nvar x = retx0;"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_deeperswitchthis(self):
		library="cases = {log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message); } }"
		input='var select="log"; window.cases[select]();'
		expected="var select=\"log\"; switch (select) {\n\tcase \"log\":\nif (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(window.cases.message);\n\tbreak;\n\tdefault:\n\twindow.cases[select]();\n}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_deeperswitchcall(self):
		library="cases = {log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(this.message); } }"
		input='var select="log"; window.cases[select].call(called);'
		expected="var select=\"log\"; switch (select) {\n\tcase \"log\":\nif (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(called.message);\n\tbreak;\n\tdefault:\n\twindow.cases[select].call(called);\n}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_forswitch(self):
		library='steps = {0:function(){this.increment(1)},1:function(){this.increment(2)},2:function(){tthis.decrement(3)}}'
		input="for (var step = 0; step<steps.length; step++) {steps[step].call(datablob);}"
		expected='for (var step = 0; step<steps.length; step++) {switch (step) {\n\tcase "1":\n\tcase 1:\ndatablob.increment(2);\n\tbreak;\n\tcase "0":\n\tcase 0:\ndatablob.increment(1);\n\tbreak;\n\tcase "2":\n\tcase 2:\ntthis.decrement(3);\n\tbreak;\n\tdefault:\n\tsteps[step].call(datablob);\n}}'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_arrayforswitch(self):
		library='steps = [function(){this.increment(1)},function(){this.increment(2)},function(){tthis.decrement(3)}]'
		input="for (var step = 0; step<steps.length; step++) {steps[step].call(datablob);}"
		expected='for (var step = 0; step<steps.length; step++) {switch (step) {\n\tcase "1":\n\tcase 1:\ndatablob.increment(2);\n\tbreak;\n\tcase "0":\n\tcase 0:\ndatablob.increment(1);\n\tbreak;\n\tcase "2":\n\tcase 2:\ntthis.decrement(3);\n\tbreak;\n\tdefault:\n\tsteps[step].call(datablob);\n}}'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_arrayvarforswitch(self):
		library='var steps = [function(){this.increment(1)},function(){this.increment(2)},function(){tthis.decrement(3)}]'
		input="for (var step = 0; step<steps.length; step++) {steps[step].call(datablob);}"
		expected='for (var step = 0; step<steps.length; step++) {switch (step) {\n\tcase "1":\n\tcase 1:\ndatablob.increment(2);\n\tbreak;\n\tcase "0":\n\tcase 0:\ndatablob.increment(1);\n\tbreak;\n\tcase "2":\n\tcase 2:\ntthis.decrement(3);\n\tbreak;\n\tdefault:\n\tsteps[step].call(datablob);\n}}'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_arraynestedforswitch(self):
		library='object = {steps:[function(){this.increment(1)},function(){this.increment(2)},function(){tthis.decrement(3)}]}'
		input="for (var step = 0; step<steps.length; step++) {object.steps[step].call(datablob);}"
		expected='for (var step = 0; step<steps.length; step++) {switch (step) {\n\tcase "1":\n\tcase 1:\ndatablob.increment(2);\n\tbreak;\n\tcase "0":\n\tcase 0:\ndatablob.increment(1);\n\tbreak;\n\tcase "2":\n\tcase 2:\ntthis.decrement(3);\n\tbreak;\n\tdefault:\n\tobject.steps[step].call(datablob);\n}}'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_switchargs(self):
		library="cases = {log : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message); } }"
		input='var select="log"; cases[select](thing);'
		expected="var select=\"log\"; switch (select) {\n\tcase \"log\":\nif (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(thing);\n\tbreak;\n\tdefault:\n\tcases[select](thing);\n}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_switchinstance(self):
		library='cases = {"0" : function (instance) { this.get(instance); this.temp = this.get(instance); } }'
		input='cases[select](thing);'
		expected="switch (select) {\n\tcase \"0\":\n\tcase 0:\ncases.get(thing); cases.temp = cases.get(thing);\n\tbreak;\n\tdefault:\n\tcases[select](thing);\n}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_nestedswitch(self):
		library='var foo=function(thing){var x = thing}'
		input='switch(thing){case "foo": foo(thing); break; case 1: foo(1); break; case 2: foo(2); break;}'
		expected='switch(thing){case "foo": var x = thing; break; case 1: var x = 1; break; case 2: var x = 2; break;}'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

class TestDef(unittest.TestCase):
	def test_def(self):
		library="object = function(){}; object.prototype={reallog : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } };"
		input='object.prototype.log = function(message) {this.reallog(message);}'
		expected="object.prototype.log = function(message) {if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_new(self):
		library="object = function(){this.reallog = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }}; object2 = new object()"
		input='object.prototype.log = function(message) {this.reallog(message);}'
		expected="object.prototype.log = function(message) {if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_varnew(self):
		library="var object = function(){this.reallog = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }}; object2 = new object()"
		input='object.prototype.log = function(message) {this.reallog(message);}'
		expected="object.prototype.log = function(message) {if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_funnew(self):
		library="function object(){this.reallog = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }}; object2 = new object()"
		input='object.prototype.log = function(message) {this.reallog(message);}'
		expected="object.prototype.log = function(message) {if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_newdouble(self):
		library="object = function(){this.reallog = function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) }; this.reallog2 = function (message) { if (typeof(console) != 'undefined' && 'log' in console) console.log(message) }}; object2 = new object()"
		input='object.prototype.log = function(message) {this.reallog2(message);}'
		expected="object.prototype.log = function(message) {if (typeof(console) != 'undefined' && 'log' in console) console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_doublenew(self):
		library="function adder(){this.run = function(one, two) { return one + two }} function mather(){this.add = new adder(); } mathing = new mather()"
		input='var x = mathing.add.run(1,2);'
		expected="var x = (1 + 2);"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_nesteddoublenew(self):
		library="var object={}; object.adder = function(){}; object.adder.prototype={run : function(one, two) { return one + two }}; function mather(){this.add = new object.adder(); }; mathing = new mather()"
		input='var x = mathing.add.run(1,2);'
		expected="var x = (1 + 2);"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_2nesteddoublenew(self):
		library="var object={}; object.nested={}; object.nested.adder = function(){}; object.nested.adder.prototype={run : function(one, two) { return one + two }}; function mather(){this.add = new object.nested.adder(); }; mathing = new mather()"
		input='var x = mathing.add.run(1,2);'
		expected="var x = (1 + 2);"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_3nesteddoublenew(self):
		library="var object={}; object.nested=function(){this.adder = new object.nested.adder()}; object.nested.adder = function(){}; object.nested.adder.prototype={run : function(one, two) { return one + two }}; function mather(){this.add = new object.nested.adder(); }; mathing = new mather()"
		input='var x = mathing.add.run(1,2);'
		expected="var x = (1 + 2);"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_deferrednew(self):
		library="var object={}; object.nested=function(){this.adder = new object.nested.adder()}; object.nested.adder = function(){}; object.nested.adder.prototype={run : function(one, two) { return one + two }}; mathing = new object.nested()"
		input='var x = mathing.adder.run(1,2);'
		expected="var x = (1 + 2);"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_deferrednewargs(self):
		library="var object={}; object.nested=function(){this.adder = new object.nested.adder(empty)}; object.nested.adder = function(empty){}; object.nested.adder.prototype={run : function(one, two) { return one + two }}; mathing = new object.nested()"
		input='var x = mathing.adder.run(1,2);'
		expected="var x = (1 + 2);"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

class TestPassing(unittest.TestCase):
	def test_pass(self):
		library="object = function(){}; object.prototype={reallog : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } };"
		input='log = function(logger/*:object*/, message) {logger.reallog(message);}'
		expected="log = function(logger/*:object*/, message) {if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_passSpace(self):
		library="object = function(){}; object.prototype={reallog : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } };"
		input='log = function(logger /* : object */ , message) {logger.reallog(message);}'
		expected="log = function(logger /* : object */ , message) {if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_passDeep(self):
		library="deep={object:{}};deep.object.prototype={reallog : function (message) { if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message) } };"
		input='log = function(logger/*:deep.object*/, message) {logger.reallog(message);}'
		expected="log = function(logger/*:deep.object*/, message) {if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined') console.log(message);}"
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)

class TestPassing(unittest.TestCase):
	def test_shortcall(self):
		library="function twoargs(one, two) { var x = one + two; }"
		input='twoargs(ones)'
		expected='var x = ones + undefined'
		output=jsfunkliner.inlineSingle(input, library)
		self.assertEqual(expected, output)
	def test_longcall(self):
		library="function twoargs(one, two) { var x = one + two; }"
		input='twoargs(ones, twos, threes)'
		expected='var x = ones + twos'
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
