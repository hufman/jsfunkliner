#!/usr/bin/python

import jsparser
import types
import traceback
import sys

class JSEnvironment:
	def __init__(self, root, this):
		"""
		Create a blank environment, with the given root object and a blank local scope
		"""
		self.root = root
		self.this = [this]
		self.scopes = [{}]

	def pushThis(self, newthis):
		"""
		Change the current this object, saving the old one for a future pop
		"""
		self.this.append(newthis)

	def popThis(self):
		"""
		Delete the current this object and revert to the previous
		"""
		return self.this.pop

	def getThis(self):
		"""
		Return the current this object
		"""
		return self.this[-1]

	def pushScope(self):
		"""
		Change the current local scope, saving the old scope for a future pop
		"""
		self.scopes.append({})

	def popScope(self):
		"""
		Delete the current scope and revert to the previous
		"""
		self.scopes.pop()

	def createLocal(self, name):
		"""
		Define a variable in the current local scope
		"""
		self.scopes[-1][name] = None

	def set(self, name, value):
		"""
		Set a variable in the current local scope, if it is defined
		Otherwise, create it inside the global object

		if the name has period separators, navigate the scopes to find it
		"""
		parts=name.split('.')
		if len(parts)>1:
			if parts[0] == 'this':
				curobject = self.this[-1]
			elif parts[0] in self.scopes[-1]:
				curobject = self.scopes[-1][parts[0]]
			else:
				curobject = self.root[parts[0]]

			for part in parts[1:-1]:
				curobject = curobject.get(part)

			curobject[parts[-1]] = value
		else:
			if parts[0] in self.scopes[-1]:
				self.scopes[-1][name] = value
			else:
				self.root[name] = value


	def get(self, name):
		"""
		Returns the value for a variable in the current scope
		If it is not in the local scope, return the variable of the global scope

		if the name has period separators, navigate the scopes to find it
		"""
		parts=name.split('.')
		if len(parts)>1:
			if parts[0] == 'this':
				curobject = self.this[-1]
			elif parts[0] in self.scopes[-1]:
				curobject = self.scopes[-1][parts[0]]
			else:
				curobject = self.root[parts[0]]

			for part in parts[1:-1]:
				curobject = curobject.get(part)

			if parts[-1] in curobject:
				return curobject[parts[-1]]
		else:
			if name in self.scopes[-1]:
				return self.scopes[-1][name]
			else:
				#import pdb; pdb.set_trace()
				if name in self.root:
					return self.root[name]

class JSObject:
	def __init__(self, function=None, parent=None, members=None):
		"""
		Create a new JSObject, ready to have members added
		If you pass in a parent, like a javascript prototype, its members are duplicated
		You can also pass in some extra members to add at the start
		"""
		if parent == None:
			self.members = members if members else {}
		else:
			self.members = dict.copy(parent.members)
			if members:
				self.members.update(members)
		self.function = function

	def __setitem__(self, name, value):
		"""
		Add/update this member on this object
		"""
		self.members[name] = value

	def __getitem__(self, name):
		"""
		Return this member
		"""
		return self.members[name]
	def __contains__(self, name):
		return name in self.members
	def getFunction(self):
		return self.function

def _crawlIdentifier(object, valuename):
	if object.type=='IDENTIFIER':
		return getattr(object, valuename)
	if object.type=='DOT':
		return _crawlIdentifier(object[0], valuename) + "." + _crawlIdentifier(object[1], valuename)

def _crawlFunctions(env, code):
	#import pdb; pdb.set_trace()
	for node in code:
		if node.type=='FUNCTION':
			env.set(node.name, JSObject(node))
		elif node.type=='VAR':
			name = node[0].value
			if node[0].initializer.type=='FUNCTION':
				env.set(name, JSObject(node[0].initializer))
			elif node[0].initializer.type=='OBJECT_INIT':
				newthis = JSObject()
				env.set(node[0].name, newthis)
				env.pushThis(newthis)
				_crawlFunctions(env, node[0].initializer)
				env.popThis()
			else:
				fromname = _crawlIdentifier(node[0].initializer, 'value')
				env.set(name, env.get(fromname))
		elif node.type=='SEMICOLON' and node.expression and node.expression.type=='ASSIGN':
			name = _crawlIdentifier(node.expression[0], 'value')
			if node.expression[1].type == 'FUNCTION':		# x = function() {}
				env.set(name, JSObject(node.expression[1]))
			elif node.expression[1].type == 'IDENTIFIER':		# x = x;
				fromname = _crawlIdentifier(node.expression[1], 'value')
				env.set(name, env.get(fromname))
			elif node.expression[1].type=='OBJECT_INIT':		# x = {}
				newthis = JSObject()
				env.set(name, newthis)
				env.pushThis(newthis)
				_crawlFunctions(env, node.expression[1])
				env.popThis()
			elif node.expression[1].type == 'NEW':			# x = new a
				fromname = _crawlIdentifier(node.expression[1][0], 'value') + ".prototype"
				env.set(name, JSObject(None, env.get(fromname)))
		elif node.type=='PROPERTY_INIT' and node[0].type=='IDENTIFIER' and node[1].type=='FUNCTION':
			env.set("this."+node[0].value, JSObject(node[1]))
	return env

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
	params=function.params
	replacements={}
	for i in range(0, len(arguments)):
		replacements[params[i]] = arguments[i]
	return replaceIdentifiers(librarytext, function.body, replacements, retval)

def replaceIdentifiers(librarytext, body, replacements, retval):
	"""
	Given a jsparse'd body object and a map of replacements,
	replace any identifiers that are found in the replacements map
	and return the body as a flat string
	If it is a function, special code happens for the return
	Note: Only supports a single return as the last line of the function, if any return at all

	If it is a single line function that returns stuff, .needsRetVal == False
	If it is a multi-line function that returns stuff, .needsRetVal == True and .retval will contain the variable name to use
		The retval passed to the replaceIdentifiers function can be None, in which case any return lines are deleted
			This is used for calls that don't use the return
	If it is a function that does not return stuff, .needsRetVal == False
	"""
	#print("Inlining function with args "+str(replacements))
	class Replacer():
		CHILD_ATTRS = ['thenPart', 'elsePart', 'expression', 'body', 'initializer']
		def __init__(self):
			self.output=[]
			if len(body):
				firstline=body[0]
			else:
				firstline=body
			self.inputoffset=firstline.start
			self.librarytext=librarytext
			self.retval = retval

			if firstline.type!='RETURN' and self.retval != None:
				self.needsRetVal=True
				self.output.append('var %s = undefined;\n'%self.retval)
			else:
				self.needsRetVal=False
			oldoffset=self.inputoffset
			#print("Looking at code "+str(body))
			if len(body):
				self.walkbranch(body, True)
			else:
				self.walkstatement(body)
			#print("Replaced params: "+self.librarytext[oldoffset:self.inputoffset])

		def walkbranch(self, branch, top):
			for statement in branch:
				self.walkstatement(statement)
			if self.inputoffset < branch.end:
				if top:
					end = branch[len(branch)-1].end		# point to the end of the last statement of the block, to trim off the semicolon and any whitespace
				else:
					end = branch.end					# point to the end of the block
				#print("appending "+self.librarytext[self.inputoffset:branch.end])
				self.output.append(self.librarytext[self.inputoffset:end])
				self.inputoffset=end

		def walkstatement(self, statement):
			#print("Looking at statement "+str(statement))
			if statement.type == "RETURN":
				self.output.append(self.librarytext[self.inputoffset:statement.start])
				self.inputoffset=statement.value.start
				if self.needsRetVal and self.retval != None:
					self.output.append("%s = "%self.retval)
					self.walkexpression(statement.value)
					self.output.append(self.librarytext[self.inputoffset:statement.end])
					self.inputoffset = statement.end
					self.output.append(";\n")
				else:
					self.walkexpression(statement.value)
			elif statement.type == 'CALL':
				self.replaceIdentifier(statement[0])	# possibly replace the function name
				self.walkexpression(statement[1])	# replace any replacements to the function
			elif statement.type == 'IF':
				self.walkexpression(statement.condition)
			elif statement.type == 'SEMICOLON':
				self.walkexpression(statement.expression)
			elif statement.type == 'VAR':
				self.walkexpression(statement[0].initializer)
			for attr in Replacer.CHILD_ATTRS:
				child = getattr(statement, attr, None)
				if child and isinstance(child, jsparser.Node):
					if hasattr(child, 'expression'):
						self.walkstatement(child.expression)
					elif len(child):
						self.walkbranch(child, False)
					else:
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
			if len(expression):
				for piece in expression:
					self.walkexpressionpiece(piece)
			else:
				self.walkexpressionpiece(expression)
		def walkexpressionpiece(self, piece):
			#print("Looking at expression piece "+str(piece));
			if piece.type=='IDENTIFIER':
				self.replaceIdentifier(piece)
			elif piece.type=='CALL':
				self.walkexpression(piece)
			elif piece.type=='STRING':
				pass
			elif piece.type=='NUMBER':
				pass
			elif len(piece):
				self.walkexpression(piece)
			else:
				try:
					self.walkexpressionpiece(piece.expression)
				except:
					excinfo=sys.exc_info()
					sys.excepthook(excinfo[0], excinfo[1], excinfo[2])
					print("unknown type of piece: "+str(piece))

		def replaceIdentifier(self, identifier):
			if identifier.value in replacements.keys():
				self.output.append(self.librarytext[self.inputoffset:identifier.start])
				self.output.append(str(replacements[identifier.value]))
				self.inputoffset = identifier.end

		def getOutput(self):
			return ''.join(self.output)

	walker = Replacer()
	return walker


def inlineSingle(inputtext, librarytext):
	window = JSObject()
	window['window'] = window
	env = JSEnvironment(window, window)	# window is root and this

	library = jsparser.parse(librarytext)

	functions = _crawlFunctions(env, library)

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
						self.inputoffset=statement.start
						index = len(self.output)
						self.walkexpression(child, name, False)
						if len(self.preput)>0:
							self.output.insert(index, self.preput)
				elif statement.type == 'CALL':
					self.replacefunction(statement, statement[0].value)
				elif statement.type == 'FOR':
					self.unloopFor(statement)
					continue
				#else:
					#print("Unknown type of statement: "+str(statement))
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
				self.replacecall(expression, retname, usesReturn)
				self.callcount+=1
				return
			for piece in expression:
				if piece.type=='CALL':
					retname = 'ret'+name+str(self.callcount)
					if not usesReturn:
						retname = None
					self.replacecall(piece, retname, usesReturn)
					self.callcount+=1
				elif len(piece):
					crawlexpression(piece)

		def replacecall(self, call, name, usesReturn):
			#import pdb; pdb.set_trace()
			function = env.get(call[0].value)
			if function == None or function.getFunction() == None:
				return
			arguments = ['"'+node.value+'"' if node.type=='STRING' else node.value for node in call[1]]
			functionout = inlineFunction(self.librarytext, function.getFunction(), arguments, name)
			if functionout.needsRetVal:
				self.preput+=functionout.getOutput()
				self.output.append(self.inputtext[self.inputoffset:call.start])
				self.output.append(functionout.retval)
				self.inputoffset = call.end
			else:
				if usesReturn:
					self.output.append(self.inputtext[self.inputoffset:call.start]+"(")
					self.output.append(functionout.getOutput()+")")
				else:
					self.output.append(self.inputtext[self.inputoffset:call.start])
					self.output.append(functionout.getOutput())
				self.inputoffset = call.end

		def unloopFor(self, loop):
			variable=None	# variable to replace
			start=None		# starting value
			cur=None		# current value
			step=None		# how much to add/subtract on each loop
			stop=None		# function saying whether to stop
			maxiterations = 60		# how many times we will allow to unroll

			# parse the initialization
			setup = loop.setup
			if setup.type=='VAR':
				if setup[0].type=='IDENTIFIER' and \
				   setup[0].initializer.type=='NUMBER':
					variable = setup[0].value
					start = setup[0].initializer.value

			# parse the update
			update = loop.update
			if update.type=='INCREMENT':	# i++
				step=1
			elif update.type=='DECREMENT':	# i--
				step=-1
			elif update.type=='ASSIGN':		# more complex update
				# i+=1
				if update[0].type=='IDENTIFIER' and \
				   update[0].value==variable and \
				   update[1].type=='NUMBER':
					if update.value=='+':
						step=0+update[1].value
					elif update.value=='-':
						step=0-update[1].value
				# i=x+x
				if update[0].type=='IDENTIFIER' and \
				   update[0].value==variable and \
				   update[1].type=='PLUS':
					# i=i+1
					if update[1][0].value==variable and \
					   update[1][1].type=='NUMBER':
						step=0+update[1][1].value
					# i=1+i
					if update[1][1].value==variable and \
					   update[1][0].type=='NUMBER':
						step=0+update[1][0].value
				# i=x-x
				if update[0].type=='IDENTIFIER' and \
				   update[0].value==variable and \
				   update[1].type=='MINUS':
					# i=i-1
					if update[1][0].value==variable and \
					   update[1][1].type=='NUMBER':
						step=0-update[1][1].value

			# parse the ending criteria
			condition = loop.condition
			if condition.type in ['LT', 'LE', 'GT', 'GE'] and condition[0].type=='IDENTIFIER' and condition[0].value==variable:
				if condition.type=='LT' and step>0:
					stop=lambda i: i >= condition[1].value
				elif condition.type=='LE' and step>0:
					stop=lambda i: i > condition[1].value
				elif condition.type=='GT' and step<0:
					stop=lambda i: i <= condition[1].value
				elif condition.type=='GE' and step<0:
					stop=lambda i: i < condition[1].value

			# check that we parsed everything validly
			if start is None or step is None or stop is None:
				# could not parse something
				return

			# how many iterations in the loop
			iterations = 0
			cur = start
			while iterations < maxiterations and \
			      not stop(cur):
				iterations+=1
				cur += step
			if iterations >= maxiterations:
				# too many loop unwinds
				return

			# Do the unwinding
			iterations = 0
			cur = start
			self.output.append(self.inputtext[self.inputoffset:loop.start])
			self.inputoffset = loop.body.end
			while not stop(cur):
				bodyout = replaceIdentifiers(self.inputtext, loop.body, {"i":cur}, None)
				self.output.append(bodyout.getOutput())
				cur += step
				if len(loop.body):
					self.output.append(self.inputtext[loop.body[len(loop.body)-1].end:loop.end-1])
				if not stop(cur):
					self.output.append('\n')

		def getOutput(self):
			return ''.join(self.output)

	crawler = Crawler(inputtext, librarytext, library)
	return crawler.getOutput()
