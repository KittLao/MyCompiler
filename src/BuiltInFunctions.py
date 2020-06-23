from evaluator import EvaluateResult
from values import *

# Contains all built in functions

# Specifically prints out stuff
# :Evaluator: -> :[[Node]]: -> :Context:
def my_print(interpreter, args_seq, context):
	result = EvaluateResult()
	# Print is not a high-order function
	args = args_seq[0] # [Node]
	for i in range(len(args)):
		value = result.register(interpreter.eval_node(args[i], context))
		if result.error: return result
		if i == 0:
			print(value, end='')
		else:
			print(' ', value, end='')
	print()
	return result.success(Value(None))