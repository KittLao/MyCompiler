import sys

from lexer import Lexer
from parser_ import Parser
from evaluator import Evaluator
from context import Context
from environment import *
from values import Value


global_env = Environment()
global_env.set("null", Value(0))
global_func_env = FunctionEnvironment()

def display(sequence, index=0):
	if type(sequence).__name__ == 'list':
		for elem in sequence:
			display(elem, index + 1)
	else:
		print(" "*index, sequence)

def interpret_stdin():
	context = Context("<stdin>", global_env, global_func_env)
	while True:
		text = input(">>> ")
		lexer = Lexer("<stdin>", text)
		tokens, errors = lexer.generate_tokens()
		if errors == None:
			# print(tokens)
			parser = Parser(tokens)
			ast = parser.parse()
			if ast.error == None:
				# print(ast.node)
				evaluator = Evaluator(ast.node, context)
				value = evaluator.evaluate()
				if value.error == None:
					print(value.value)
				else:
					print(value.error.as_string())
			else:
				print(ast.error.as_string())
		else:
			print(errors.as_string())

def interpret_program(program):
	file = open(program, 'r')
	lines = file.readlines()
	context = Context('<' + program + '>', global_env, global_func_env)
	lexer = Lexer('<' + program + '>', lines)
	tokens, errors = lexer.generate_tokens()
	if errors == None:
		print("Tokens: ")
		for x in tokens:
			print(x)
		parser = Parser(tokens)
		ast = parser.parse()
		if ast.error == None:
			print("AST's: ")
			for x in ast.node:
				print(x)
		else:
			print(ast.error.as_string())
	else:
		print(errors.as_string())


def main():
	argv = sys.argv
	if len(argv) < 2:
		interpret_stdin()
	else:
		program = argv[1]
		interpret_program(program)

main()













