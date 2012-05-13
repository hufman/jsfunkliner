#!/usr/bin/python

import jsparser
import types
import traceback
import sys

def _crawlFunctions(namespace, code):
	ret={}
	for node in code:
		if node.type=='FUNCTION':
			name=namespace+"."+node.name
			ret[name]=node
	return ret

def _crawlCalls(namespace, code):
	CHILD_ATTRS = ['thenPart', 'elsePart', 'expression', 'body', 'initializer']
	ret=[]
	if code.type=='SCRIPT':
		ret.extend(_crawlCalls(namespace, code[0]))
		return ret;
	if code.type=='CALL':	# direct call
		code[0].value=namespace+'.'+code[0].value
		ret.append(code)
		return ret;
	for node in code:
		if node.type=='CALL':	# direct call
			node[0].value=namespace+'.'+node[0].value
			ret.append(node)
		for attr in CHILD_ATTRS:
			child = getattr(node, attr, None)
			if child:
				ret.extend(_crawlCalls(namespace, child))
	return ret

def inlineFunction(librarytext, function, arguments, retval):
	"""
	Given a jsparse'd function object and a list of arguments that called it,
	replace any uses of the function-defined args with the caller-defined args
	and return the body of the function as a flat string
	Note: Only supports a single return as the last line of the function, if any return at all

	If it is a single line function that returns stuff, .needsRetVal == False
	If it is a multi-line function that returns stuff, .needsRetVal == True and .retval will contain the variable name to use
		The retval passed to the inlineFunction function can be None, in which case any return lines are deleted
			This is used for calls that don't use the return
	If it is a function that does not return stuff, .needsRetVal == False
	"""
	#print("Inlining function with args "+str(arguments))
	class FunctionPromoter():
		CHILD_ATTRS = ['thenPart', 'elsePart', 'expression', 'body', 'initializer']
		def __init__(self, function, librarytext, retval):
			self.output=[]
			self.params=function.params
			self.inputoffset=function.body[0].start
			self.librarytext=librarytext
			self.retval = retval

			if function.body[0].type!='RETURN' and self.retval != None:
				self.needsRetVal=True
				self.output.append('var %s = undefined;\n'%self.retval)
			else:
				self.needsRetVal=False
			oldoffset=self.inputoffset
			#print("Looking at function "+str(function))
			self.walkbranch(function.body)
			#print("Inlined function: "+self.librarytext[oldoffset:self.inputoffset])

		def walkbranch(self, branch):
			for statement in branch:
				self.walkstatement(statement)
			if self.inputoffset < branch.end:
				#print("appending "+self.librarytext[self.inputoffset:branch.end])
				self.output.append(self.librarytext[self.inputoffset:branch.end])
				self.inputoffset=branch.end

		def walkstatement(self, statement):
			#print("Looking at statement "+str(statement))
			if statement.type == "RETURN":
				self.output.append(self.librarytext[self.inputoffset:statement.start])
				if self.needsRetVal and self.retval != None:
					self.output.append("%s = "%self.retval)
				self.inputoffset=statement.value.start
				self.walkexpression(statement.value)
			elif statement.type == 'CALL':
				self.replaceIdentifier(statement[0])	# possibly replace the function name
				self.walkexpression(statement[1])	# replace any arguments to the function
			elif statement.type == 'IF':
				self.walkexpression(statement.condition)
			elif statement.type == 'SEMICOLON':
				self.walkexpression(statement.expression)
			elif statement.type == 'VAR':
				self.walkexpression(statement[0].initializer)
			for attr in FunctionPromoter.CHILD_ATTRS:
				#import pdb; pdb.set_trace()
				child = getattr(statement, attr, None)
				if child and isinstance(child, jsparser.Node):
					if hasattr(child, 'expression'):
						self.walkstatement(child.expression)
					elif hasattr(child, 'length'):
						self.walkbranch(child)
					else:
						try:
							firstchild = child[0]
							self.walkbranch(child)
						except:
							try:
								self.walkstatement(child.expression)
							except:
								excinfo=sys.exc_info()
								sys.excepthook(excinfo[0], excinfo[1], excinfo[2])
								print("unknown type of child: "+str(child))
			if self.inputoffset < statement.end:
				#print("Setting offset to "+str(statement.end))
				self.output.append(self.librarytext[self.inputoffset:statement.end])
				self.inputoffset=statement.end

		def walkexpression(self, expression):
			for piece in expression:
				#print("Looking at expression piece "+str(piece));
				length = getattr(piece, 'length', None)
				if piece.type=='IDENTIFIER':
					self.replaceIdentifier(piece)
				elif piece.type=='CALL':
					self.walkexpression(piece)
				elif piece.type=='STRING':
					pass
				elif length:
					self.walkexpression(piece)
				else:
					try:
						firstchild = piece[0]
						self.walkexpression(piece)
					except:
						try:
							self.walkexpression(piece.expression)
						except:
							excinfo=sys.exc_info()
							sys.excepthook(excinfo[0], excinfo[1], excinfo[2])
							print("unknown type of piece: "+str(piece))

		def replaceIdentifier(self, identifier):
			#print("Trying to replace "+str(identifier.value)+" in "+str(self.params))
			if identifier.value in self.params:
				#print("Replacing "+identifier.value+" with "+str(arguments[self.params.index(identifier.value)]))
				self.output.append(self.librarytext[self.inputoffset:identifier.start])
				self.output.append(str(arguments[self.params.index(identifier.value)]))
				self.inputoffset = identifier.end
				#print(self.output)

		def getOutput(self):
			return ''.join(self.output)

	walker = FunctionPromoter(function, librarytext, retval)
	return walker


def inlineSingle(inputtext, librarytext):
	library = jsparser.parse(librarytext)

	functions = _crawlFunctions('window', library)

	class Crawler():
		CHILD_ATTRS = ['thenPart', 'elsePart', 'expression', 'body', 'initializer']
		def __init__(self, inputtext, librarytext, library):
			self.inputoffset = 0
			self.output = []
			self.inputtext = inputtext
			script = jsparser.parse(inputtext)
			self.librarytext = librarytext
			self.library = library

			self.preput = ''

			self.walkbranch(script)

		def walkbranch(self, branch):
			if not getattr(branch, 'end', None):
				branch.end = len(inputtext)
			for statement in branch:
				#print("Looking at statement "+str(statement))
				self.statementCalls = []
				if statement.type == "VAR":	# create a new variable
					child = getattr(statement[0], 'initializer', None)
					if child:
						name = statement[0].value
						self.callcount = 0
						self.preput = ''
						self.output.append(self.inputtext[self.inputoffset:statement.start])
						index = len(self.output)
						self.walkexpression(child, name, True)
						if len(self.preput)>0:
							self.output.insert(index, self.preput)
				elif statement.type == 'SEMICOLON':
					child = getattr(statement, 'expression', None)
					if child:
						name = statement.value
						self.callcount = 0
						self.preput = ''
						self.output.append(self.inputtext[self.inputoffset:statement.start])
						index = len(self.output)
						self.walkexpression(child, name, False)
						if len(self.preput)>0:
							self.output.insert(index, self.preput)
				elif statement.type == 'CALL':
					self.replacefunction(statement, statement[0].value)
				for attr in Crawler.CHILD_ATTRS:
					child = getattr(statement, attr, None)
					if child and isinstance(child, jsparser.Node):
						self.walkbranch(child)
			self.output.append(self.inputtext[self.inputoffset:branch.end])
			self.inputoffset=branch.end

		def walkexpression(self, expression, name, usesReturn):
			if expression.type=='CALL':
				retname = 'ret'+name+str(self.callcount)
				if not usesReturn:
					retname = None
				self.replacefunction(expression, retname)
				self.callcount+=1
				return
			for piece in expression:
				length = getattr(piece, 'length', None)
				if piece.type=='CALL':
					retname = 'ret'+name+str(self.callcount)
					if not usesReturn:
						retname = None
					self.replacefunction(piece, retname)
					self.callcount+=1
				elif length:
					crawlexpression(piece)

		def replacefunction(self, call, name):
			function = functions['window.'+call[0].value]
			arguments = ['"'+node.value+'"' if node.type=='STRING' else node.value for node in call[1]]
			functionout = inlineFunction(self.librarytext, function, arguments, name)
			if functionout.needsRetVal:
				self.preput+=functionout.getOutput()
				self.output.append(self.inputtext[self.inputoffset:call.start])
				self.output.append(functionout.retval)
				self.inputoffset = call.end
			else:
				self.output.append(self.inputtext[self.inputoffset:call.start])
				self.output.append(functionout.getOutput())
				self.inputoffset = call.end
		def getOutput(self):
			return ''.join(self.output)

	crawler = Crawler(inputtext, librarytext, library)
	return crawler.getOutput()
