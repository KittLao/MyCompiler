"""
Numbers
"""

class NumberNode:
	def __init__(self, token):
		self.token = token
		self.start_pos = token.start_pos
		self.end_pos = token.end_pos

	def __repr__(self):
		return f"{self.token}"

"""
Operations
"""

# :Token: -> :Node: -> :Node:
class BinaryOpNode:
	def __init__(self, op_token, left_node, right_node):
		self.op_token = op_token 
		self.left_node = left_node
		self.right_node = right_node
		self.start_pos = left_node.start_pos
		self.end_pos = right_node.end_pos

	def __repr__(self):
		return f"({self.left_node} {self.op_token} {self.right_node})"

# :Token: -> :Node:
class UnaryOpNode:
	def __init__(self, op_token, node):
		self.op_token = op_token
		self.node = node
		self.start_pos = op_token.start_pos
		self.end_pos = node.end_pos

	def __repr__(self):
		return f"({self.op_token} {self.node})"

"""
Variables
"""

# :Token: -> :Node:
class VarAssignNode:
	def __init__(self, var_name, expr_assign):
		self.var_name = var_name
		self.expr_assign = expr_assign
		self.start_pos = var_name.start_pos
		self.end_pos = expr_assign.end_pos

	def __repr__(self):
		return f"({self.var_name} = {self.expr_assign})"

# :Token:
class VarAccessNode:
	def __init__(self, var_name):
		self.var_name = var_name
		self.start_pos = var_name.start_pos
		self.end_pos = var_name.end_pos

	def __repr__(self):
		return f"{self.var_name}"

"""
conditional statements
"""

# :Node: -> :Node: -> :[(:Node:, :Node:)]: -> :Node:
class ConditionalNode:
	def __init__(self, if_cond, if_expr, elif_conds_exprs, else_expr):
		self.if_cond = if_cond
		self.if_expr = if_expr
		self.elif_conds_exprs = elif_conds_exprs
		self.else_expr = else_expr
		self.start_pos = if_cond.start_pos
		if else_expr:
			self.end_pos = else_expr.end_pos
		elif elif_conds_exprs:
			self.end_pos = elif_conds_exprs[len(elif_conds_exprs) - 1][1].end_pos
		else:
			self.end_pos = if_expr.end_pos

	def __repr__(self):
		cond_repr = f"if {self.if_cond} then\n\t{self.if_expr}\n"
		for elif_cond, elif_expr in self.elif_conds_exprs:
			cond_repr += f"elif {elif_cond} then\n\t{elif_expr}\n"
		if self.else_expr:
			cond_repr += f"else\n\t{self.else_expr}\n"
		cond_repr += "endif"
		return cond_repr


"""
Loops
"""

# :string: :Node: -> :Node: -> :Node:
class ForLoopNode:
	def __init__(self, var_name, init_expr, final_expr, loop_expr):
		self.var_name = var_name
		self.init_expr = init_expr
		self.final_expr = final_expr
		self.loop_expr = loop_expr
		self.start_pos = init_expr.start_pos
		self.end_pos = loop_expr.end_pos

	def __repr__(self):
		return f"for var {self.var_name} = {self.init_expr} to {self.final_expr} then\n\t{self.loop_expr}\nendfor\n"


# :Node: -> :Node:
class WhileLoopNode:
	def __init__(self, while_cond, loop_expr):
		self.while_cond = while_cond
		self.loop_expr = loop_expr
		self.start_pos = while_cond.start_pos
		self.end_pos = loop_expr.end_pos

	def __repr__(self):
		return f"while {self.while_cond} then\n\t{self.loop_expr}\nendwhile\n"










