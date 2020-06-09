from tokens import *
from values import *
from context import Context
from environment import *
from errors import *

class EvaluateResult:
	def __init__(self):
		self.value = None
		self.error = None

	"""
	:EvaluateResult: -> :EvaluateResult:
	"""
	def register(self, result):
		if result.error: self.error = result.error
		return result.value

	"""
	:Value: -> :EvaluateResult:
	"""
	def success(self, value):
		self.value = value
		return self

	"""
	:Error: -> :EvaluateResult:
	"""
	def failure(self, error):
		self.error = error
		return self

class Evaluator:
	def __init__(self, ast, context):
		self.ast = ast
		self.context = context

	def evaluate(self):
		return self.eval(self.ast, self.context)

	def eval(self, node, context):
		"""
		eval_BinaryOpNode
		eval_UnaryOpNode
		eval_NumberNode
		eval_VarAccessNode
		eval_VarAssignNode
		eval_ConditionalNode
		eval_ForLoopNode
		eval_WhileLoopNode
		eval_FuncDeclNode
		eval_FuncCallNode
		"""
		method_name = f"eval_{type(node).__name__}"
		method = getattr(self, method_name, self.eval_unknown)
		return method(node, context)

	"""
	All evals type:
	:Node: -> :Context: -> :EvaluateResult:
	"""
	def eval_unknown(self, node, context):
		raise Exception(f"No evaluation method defined for {type(node).__name__}")

	def eval_NumberNode(self, node, context):
		return EvaluateResult().success(
			Value(node.token.value).set_pos(node.start_pos, node.end_pos).set_context(context))

	def eval_UnaryOpNode(self, node, context):
		result = EvaluateResult()
		value = result.register(self.eval(node.node, context))
		if result.error: return result

		if node.op_token.type == TT_MINUS:
			value, error = value.mult_by(Value(-1))
		elif node.op_token.type == TT_PLUS:
			value, error = value.mult_by(Value(1))
		elif node.op_token.type == TT_NOT:
			value, error = value.negate()
		else:
			raise Exception("Invalid operation")
		if result.error: return result.failure(error)
		return result.success(value.set_pos(node.start_pos, node.end_pos))


	def eval_BinaryOpNode(self, node, context):
		result = EvaluateResult()
		left = result.register(self.eval(node.left_node, context))
		if result.error: return result
		right = result.register(self.eval(node.right_node, context))
		if result.error: return result

		if node.op_token.type == TT_PLUS:
			value, error = left.add_to(right)
		elif node.op_token.type == TT_MINUS:
			value, error = left.sub_by(right)
		elif node.op_token.type == TT_MULT:
			value, error = left.mult_by(right)
		elif node.op_token.type == TT_DIV:
			value, error = left.div_by(right)
		elif node.op_token.type == TT_EXP:
			value, error = left.pow_of(right)
		elif node.op_token.type == TT_MOD:
			value, error = left.mod_by(right)
		elif node.op_token.type == TT_EQT:
			value, error = left.eq_to(right)
		elif node.op_token.type == TT_NE:
			value, error = left.not_eq_to(right)
		elif node.op_token.type == TT_LT:
			value, error = left.less_than(right)
		elif node.op_token.type == TT_GT:
			value, error = left.grt_than(right)
		elif node.op_token.type == TT_LTE:
			value, error = left.less_eq(right)
		elif node.op_token.type == TT_GTE:
			value, error = left.grt_eq(right)
		elif node.op_token.type == TT_OR:
			value, error = left.or_by(right)
		elif node.op_token.type == TT_AND:
			value, error = left.and_by(right)
		else:
			raise Exception("Invalid operation")

		if error: return result.failure(error)
		return result.success(value.set_pos(node.start_pos, node.end_pos))

	def eval_VarAccessNode(self, node, context):
		result = EvaluateResult()
		var_name = node.var_name.value
		value = context.env.get(var_name)
		if not value:
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"'{var_name}' is not defined", context))
		"""
		Building a copy of the value node and resetting the start and
		end position will help display the runtime error at the most
		recent location where it occured.

		Ex:
			>>> VAR a = 0
			>>> 5 / a

		The error would point to ">>> 5 / a"
		"""
		if isinstance(value, Value):
			value = value.copy().set_pos(node.start_pos, node.end_pos)
		return result.success(value)

	def eval_VarAssignNode(self, node, context):
		result = EvaluateResult()
		var_name = node.var_name.value
		if context.func_env.exists(var_name):
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"'{var_name}' is already declared as a function", context))
		var_value = result.register(self.eval(node.expr_assign, context))
		if result.error: return result
		context.env.set(var_name, var_value)
		return result.success(var_value)

	def eval_ConditionalNode(self, node, context):
		result = EvaluateResult()
		# Evaluates condition for if statement.
		if_cond = result.register(self.eval(node.if_cond, context))
		if result.error: return result
		# Build new context for the scope of the expression.
		child_context = Context(context.display_name, Environment(context.env),
								FunctionEnvironment(context.func_env), context,
								node.start_pos)
		# If condition is true, evaluate the if expression and just return the value
		if if_cond.value:
			if_value = result.register(self.eval(node.if_expr, child_context))
			if result.error: return result
			return result.success(if_value)
		# Evaluates elif statements, if exists
		for elif_cond, elif_expr in node.elif_conds_exprs:
			# Evaluate all elif conditions and expressions inorder. If a condition is
			# true, return just return the value
			elif_cond = result.register(self.eval(elif_cond, context))
			if result.error: return result
			if elif_cond.value:
				elif_value = result.register(self.eval(elif_expr, child_context))
				if result.error: return result
				return result.success(elif_value)
		# Evaluates else statement if exists
		if not node.else_expr: return result.success(Value(None).set_pos(node.start_pos, node.end_pos))
		else_value = result.register(self.eval(node.else_expr, child_context))
		if result.error: return result
		return result.success(else_value)

	def eval_ForLoopNode(self, node, context):
		result = EvaluateResult()
		# Evaluate initial and final values for the iterator and make
		# sure they are integers
		init_val = result.register(self.eval(node.init_expr, context))
		if result.error: return result
		if type(init_val.value).__name__ != "int":
			return result.failure(RunTimeError(init_val.start_pos,
				init_val.end_pos, f"Exptecing int", context))
		final_val = result.register(self.eval(node.final_expr, context))
		if result.error: return result
		if type(final_val.value).__name__ != "int":
			return result.failure(RunTimeError(final_val.start_pos,
				final_val.end_pos, f"Exptecing int", context))
		# Build new context for the loop scope and allow iterator to within bounds
		child_context = Context(context.display_name, Environment(context.env),
								FunctionEnvironment(context.func_env), context,
								node.start_pos)
		child_context.env.set(node.var_name.value, init_val)
		# Evaluate the expression iteratively
		loop_val = Value(None)
		while init_val.value < final_val.value:
			loop_val = result.register(self.eval(node.loop_expr, child_context))
			if result.error: return result
			# Makue sure to increment the iterator and update the new value
			# in the context.
			init_val, error = init_val.add_to(Value(1))
			if error: return result.failure(error)
			child_context.env.set(node.var_name.value, init_val)
		return result.success(loop_val.set_pos(node.start_pos, node.end_pos))

	def eval_WhileLoopNode(self, node, context):
		result = EvaluateResult()
		# Evaluate condition for the loop
		while_cond = result.register(self.eval(node.while_cond, context))
		if result.error: return result
		# Build new context for the loop scope
		child_context = Context(context.display_name, Environment(context.env),
								FunctionEnvironment(context.func_env), context,
								node.start_pos)
		# Keep evaluating the exxpression of the loop while the condition is
		# true.
		loop_val = Value(None)
		while while_cond.value:
			loop_val = result.register(self.eval(node.loop_expr, child_context))
			if result.error: return result
			while_cond = result.register(self.eval(node.while_cond, context))
			if result.error: return result
		return result.success(loop_val.set_pos(node.start_pos, node.end_pos))

	"""
	Function errors:
		Duplicate function
		Duplicate aparameter
		Function undefined
		Invalid number of arguments
		Function name already exists as variable
		Return value not callable
	"""

	def eval_FuncDeclNode(self, node, context):
		result = EvaluateResult()
		param_ids = [var.var_name.value for var in node.params]
		func_name = node.func_name.value
		# Check if there are duplicate parameters.
		if len(param_ids) != len(set(param_ids)):
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"Duplicate parameters in function '{func_name}'", context))
		# Check to see if function already exists.
		if context.func_env.exists(func_name):
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"Duplicate funtion '{func_name}'", context))
		# Check to see if function name isn't overiding variable name
		if context.env.exists(func_name):
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"'{func_name}' declared as variable", context))
		# Update the variable and funciton environment
		func_value = FunctionValue(node, context)
		context.func_env.set(func_name, func_value)
		context.env.set(func_name, func_value)
		return result.success(func_value.set_pos(node.start_pos, node.end_pos))

	def eval_FuncCallNode(self, node, context):
		result = EvaluateResult()
		func_call_name = node.func_name.value # string
		# Retreive the function associated with the name
		func_value = context.env.get(func_call_name) # FunctionValue
		# Function needs to be defined.
		if not func_value:
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"'{func_call_name}' function is not defined", context))
		# Retreive the functions declared name, used for tracing and debuggin
		func_name = func_value.get_declared_name() # string
		# For every function call, bind all arguments to the function's
		# paremeters and evaluate the function's body expression. The 
		# intial body expression is from the funtion's identifier, while
		# the rest are from the return values of the previous function
		# call.
		for args in node.args_seq: # [[Node]]
			# Make sure next call is a function if still calling.
			if not isinstance(func_value, FunctionValue):
				return result.failure(RunTimeError(node.start_pos,
					node.end_pos, f"{func_call_name} not callable", context))
			func_node = func_value.value # FuncDeclNode
			func_expr = func_node.func_expr # Node
			params = func_node.params # [VarAssignNode]
			# Number of arguments and parameters need to match.
			if len(args) != len(params):
				return result.failure(RunTimeError(node.start_pos,
					node.end_pos, f"Invalid number of arguments", context))
			# The relative context is basically the context where the function
			# being called was declared.
			relative_context = func_value.relative_context
			# Declare a new context for funciton being evaluated. The function's
			# The context of the function's body is the child of the context for
			# where the function is declared. The function's body also includes
			# what's declared inside the function, and the parameters.
			child_context = Context(func_name, Environment(relative_context.env),
									FunctionEnvironment(relative_context.func_env),
									relative_context, node.start_pos)
			# Bind all arguments to the parameters.
			for param, arg in list(zip(params, args)): # [(VarAssignNode, Node)]
				param_name = param.var_name.value
				# Evaluating the argumetns should  be done using the context
				# for where the expression is declared.
				param_value = result.register(self.eval(arg, context)) # Value
				if result.error: return result
				child_context.env.set(param_name, param_value)
			func_value = result.register(self.eval(func_expr, child_context))
			if result.error: return result
		return result.success(func_value.set_pos(node.start_pos, node.end_pos))
		



















