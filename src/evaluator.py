from tokens import *
from values import *
from context import Context
from environment import Environment

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
		value = value.copy().set_pos(node.start_pos, node.end_pos)
		return result.success(value)

	def eval_VarAssignNode(self, node, context):
		result = EvaluateResult()
		var_name = node.var_name.value
		var_value = result.register(self.eval(node.expr_assign, context))
		if result.error: return result
		context.env.set(var_name, var_value)
		return result.success(var_value)

	def eval_ConditionalNode(self, node, context):
		result = EvaluateResult()
		"""
		Evaluates if statement.
		"""
		if_cond = result.register(self.eval(node.if_cond, context))
		if result.error: return result
		child_context = Context(context.display_name, context, node.start_pos)
		child_context.env = Environment(context.env)
		child_context.func_env = FunctionEnvironment(context.func_env)
		if if_cond.value:
			if_value = result.register(self.eval(node.if_expr, child_context))
			if result.error: return result
			return result.success(if_value)
		"""
		Evaluates elif statements, if exists.
		"""
		for elif_cond, elif_expr in node.elif_conds_exprs:
			elif_cond = result.register(self.eval(elif_cond, context))
			if result.error: return result
			if elif_cond.value:
				elif_value = result.register(self.eval(elif_expr, child_context))
				if result.error: return result
				return result.success(elif_value)
		"""
		Evaluates else statement if exists
		"""
		if not node.else_expr: return result.success(Value(None).set_pos(node.start_pos, node.end_pos))
		else_value = result.register(self.eval(node.else_expr, child_context))
		if result.error: return result
		return result.success(else_value)

	def eval_ForLoopNode(self, node, context):
		result = EvaluateResult()
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

		child_context = Context(context.display_name, context, node.start_pos)
		child_context.env = Environment(context.env)
		child_context.env.set(node.var_name.value, init_val)
		child_context.func_env = FunctionEnvironment(context.func_env)
		loop_val = Value(None)
		while init_val.value < final_val.value:
			loop_val = result.register(self.eval(node.loop_expr, child_context))
			if result.error: return result
			init_val, error = init_val.add_to(Value(1))
			if error: return result.failure(error)
			child_context.env.set(node.var_name.value, init_val)

		return result.success(loop_val.set_pos(node.start_pos, node.end_pos))

	def eval_WhileLoopNode(self, node, context):
		result = EvaluateResult()
		while_cond = result.register(self.eval(node.while_cond, context))
		if result.error: return result

		child_context = Context(context.display_name, context, node.start_pos)
		child_context.env = Environment(context.env)
		child_context.func_env = FunctionEnvironment(context.func_env)
		loop_val = Value(None)
		while while_cond.value:
			loop_val = result.register(self.eval(node.loop_expr, child_context))
			if result.error: return result
			while_cond = result.register(self.eval(node.while_cond, context))
			if result.error: return result

		return result.success(loop_val.set_pos(node.start_pos, node.end_pos))

	def eval_FuncDeclNode(self, node, context):
		result = EvaluateResult()
		param_ids = [x for x in node.params.value]
		# Check if there are duplicate parameters.
		if len(param_ids) != len(set(param_ids)):
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"Duplicate parameters in function '{node.func_name}'", context))
		# Store the declared function as a value in function environment
		context.func_env.set(node.func_name.value, node)
		return result.success(Value(None))

	def eval_FuncCallNode(self, node, context):
		func_name = node.func_name.value
		args = node.args
		func = context.func_env.get(func_name)
		# Function needs to be defined.
		if func == None:
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"'{func_name}' is not defined", context))
		params = func.params
		# Number of arguments and parameters need to match.
		if len(params) != len(args):
			return result.failure(RunTimeError(node.start_pos,
				node.end_pos, f"Invalid number of arguments", context))
		func_expr = func.func_expr
		# Declare a new context for the function.
		child_context = Context(func_name, context, node.start_pos)
		child_context.env = Environment(context.env)
		child_context.func_env = FunctionEnvironment(context.func_env)
		# Bind all arguments to the parameters.
		for param, arg in list(zip(params, args)):
			arg_val = result.register(self.eval(arg, context))
			if result.error: return result
			child_context.env.set(param.value, arg_val)
		# Evaluate the function expression.
		func_val = result.register(self.eval(func_expr, child_context))
		if result.error: return result
		return result.success(func_val.set_pos(node.start_pos, node.end_pos))
		



















