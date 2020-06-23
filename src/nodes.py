
def repr_node(node, index=0):
	node_type = type(node).__name__
	if node_type == "NumberNode":
		return repr_NumberNode(node, index)
	elif node_type == "BinaryOpNode":
		return repr_BinaryOpNode(node, index)
	elif node_type == "UnaryOpNode":
		return repr_UnaryOpNode(node, index)
	elif node_type == "VarAssignNode":
		return repr_VarAssignNode(node, index)
	elif node_type == "VarAccessNode":
		return repr_VarAccessNode(node, index)
	elif node_type == "ConditionalNode":
		return repr_ConditionalNode(node, index)
	elif node_type == "ForLoopNode":
		return repr_ForLoopNode(node, index)
	elif node_type == "WhileLoopNode":
		return repr_WhileLoopNode(node, index)
	elif node_type == "FuncDeclNode":
		return repr_FuncDeclNode(node, index)
	elif node_type == "ReturnNode":
		return repr_ReturnNode(node, index)
	elif node_type == "FuncCallNode":
		return repr_FuncCallNode(node, index)
	else:
		return "bruhh"

def repr_NumberNode(node, index=0):
	return "    " * index + f"{node.token}"

def repr_BinaryOpNode(node, index=0):
	return "    " * index + f"( {node.left_node} {node.op_token} {node.right_node} )"

def repr_UnaryOpNode(node, index=0):
	return "    " * index + f"( {node.op_token} {node.node} )"

def repr_VarAssignNode(node, index=0):
	return "    " * index + f"( {node.var_name} = {node.expr_assign} )\n"

def repr_VarAccessNode(node, index=0):
	return f"{node.var_name}\n"

def repr_ConditionalNode(node, index=0):
	cond_repr = "    " * index + f"if {node.if_cond} " + " {\n"
	for expr in node.if_expr:
		cond_repr += repr_node(expr, index + 1)
	cond_repr += "    " * index + "} "
	for elif_cond, elif_expr in node.elif_conds_exprs:
		cond_repr += f"elif {elif_cond}" + " {\n"
		for expr in elif_expr:
			cond_repr += repr_node(expr, index + 1)
	cond_repr += "    " * index + "}"
	if node.else_expr:
		cond_repr += " else {\n"
		for expr in node.else_expr:
			cond_repr += repr_node(expr, index + 1)
		cond_repr += "    " * index + "}\n"
	return cond_repr

def repr_ForLoopNode(node, index=0):
	for_repr = "   " * index + f"for var {node.var_name} = {node.init_expr} to {node.final_expr} " + "{\n"
	for expr in node.loop_expr:
		for_repr += repr_node(expr, index + 1)
	for_repr += "    " * index + "}\n"
	return for_repr

def repr_WhileLoopNode(node, index=0):
	while_repr = "    " * index + f"while {node.while_cond}" + " {\n"
	for expr in node.loop_expr:
		while_repr += repr_node(expr, index + 1)
	while_repr += "    " * index + "}\n"
	return while_repr

def repr_FuncDeclNode(node, index=0):
	func_repr = "    " * index + f"def {node.func_name} ("
	for i in range(len(node.params)):
		func_repr += f"{node.params[i]}" if i == 0 else f", {node.params[i]}"
	func_repr += ") {\n"
	for expr in node.func_expr:
		func_repr += repr_node(expr, index + 1)
	func_repr += "    " * index + "}\n"
	return func_repr

def repr_ReturnNode(node, index=0):
	return "    " * index + f"return {node.return_expr}\n"

def repr_FuncCallNode(node, index=0):
	call_repr = "    " * index + f"{node.func_name}"
	for args in node.args_seq:
		call_repr += '('
		for i in range(len(args)):
			call_repr += f"{args[i]}" if i == 0 else f", {args[i]}"
		call_repr += ')'
	return call_repr

"""
Numbers
"""

class NumberNode:
	def __init__(self, token):
		self.token = token
		self.start_pos = token.start_pos
		self.end_pos = token.end_pos

	def __repr__(self):
		return repr_node(self, 0)

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
		return repr_node(self, 0)

# :Token: -> :Node:
class UnaryOpNode:
	def __init__(self, op_token, node):
		self.op_token = op_token
		self.node = node
		self.start_pos = op_token.start_pos
		self.end_pos = node.end_pos

	def __repr__(self):
		return repr_node(self, 0)

"""
Variables
"""

# :Token: -> :Node:
class VarAssignNode:
	def __init__(self, var_name, expr_assign=None):
		self.var_name = var_name
		self.expr_assign = expr_assign
		self.start_pos = var_name.start_pos
		self.end_pos = expr_assign.end_pos if expr_assign else None

	def __repr__(self):
		return repr_node(self, 0)

# :Token:
class VarAccessNode:
	def __init__(self, var_name):
		self.var_name = var_name
		self.start_pos = var_name.start_pos
		self.end_pos = var_name.end_pos

	def __repr__(self):
		return repr_node(self, 0)

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
			self.end_pos = else_expr[len(else_expr) - 1].end_pos
		elif elif_conds_exprs:
			last_elif_expr = elif_conds_exprs[len(elif_conds_exprs) - 1][1]
			self.end_pos = last_elif_expr[len(last_elif_expr) - 1].end_pos
		else:
			self.end_pos = if_expr[len(if_expr) - 1].end_pos

	def __repr__(self):
		return repr_node(self, 0)


"""
Loops
"""

# :string: :Node: -> :Node: -> :[Node]:
class ForLoopNode:
	def __init__(self, var_name, init_expr, final_expr, loop_expr):
		self.var_name = var_name
		self.init_expr = init_expr
		self.final_expr = final_expr
		self.loop_expr = loop_expr
		self.start_pos = init_expr.start_pos
		self.end_pos = loop_expr[len(loop_expr) - 1].end_pos

	def __repr__(self):
		return repr_node(self, 0)


# :Node: -> :Node:
class WhileLoopNode:
	def __init__(self, while_cond, loop_expr):
		self.while_cond = while_cond
		self.loop_expr = loop_expr
		self.start_pos = while_cond.start_pos
		self.end_pos = loop_expr[len(loop_expr) - 1].end_pos

	def __repr__(self):
		return repr_node(self, 0)


"""
Functions
"""

# :Token: -> :[VarAssign]: -> :[Node]: 
class FuncDeclNode:
	def __init__(self, func_name, params, func_expr):
		self.func_name = func_name
		self.params = params
		self.func_expr = func_expr
		self.start_pos = func_name.start_pos
		self.end_pos = func_expr[len(func_expr) - 1].end_pos

	def __repr__(self):
		return repr_node(self, 0)

# :Node:
class ReturnNode:
	def __init__(self, return_expr):
		self.return_expr = return_expr
		self.start_pos = return_expr.start_pos
		self.end_pos = return_expr.end_pos

	def __repr__(self):
		return repr_node(self, 0)

# :Token: -> :[[Node]]:
class FuncCallNode:
	def __init__(self, func_name, args_seq):
		self.func_name = func_name
		self.args_seq = args_seq
		self.start_pos = func_name.start_pos
		last_call = args_seq[len(args_seq) - 1] # Has to have atleast one sequence of arguments
		self.end_pos = func_name.end_pos if last_call == [] else last_call[len(last_call)-1].end_pos

	def __repr__(self):
		return repr_node(self, 0)




























