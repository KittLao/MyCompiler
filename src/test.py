from lexer import Lexer
from parser_ import Parser
from evaluator import Evaluator
from context import Context
from environment import Environment
from values import Value

global_env = Environment()
global_env.set("null", Value(0))
global_func_env = FunctionEnvironment()

while True:
	text = input(">>> ")
	lexer = Lexer("<stdin>", text)
	tokens, errors = lexer.generate_tokens()
	if errors == None:
		print(tokens)
		parser = Parser(tokens)
		ast = parser.parse()
		if ast.error == None:
			print(ast.node)
			context = Context("<program>")
			context.env = global_env
			context.func_env = global_func_env
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