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
		expected="var x = 1 + 2;"
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


if __name__ == '__main__':
	if len(sys.argv)>1:
		if hasattr(TestBasic,sys.argv[1]):
			case = TestBasic(sys.argv[1])
			case.run()
		else:
			print("Invalid testcase: "+sys.argv[1])
	else:
		unittest.main()
