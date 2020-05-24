from tokens import *
from nodes import *
from errors import *

"""
Wrapper to accumulate errors whlie parsing
"""
class ParseResult:
	def __init__(self):
		self.error = None # :Error:
		self.node = None # :Node:
		self.advance_count = 0

	# Only for advancements
	def register_advancement(self):
		self.advance_count += 1

	"""
	Only for parse results

	:ParseResult: -> :ParseResult:
	"""
	def register(self, result):
		self.advance_count += result.advance_count
		if result.error:
			self.error = result.error
		return result.node

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		"""
		Do not want to override error if already exists. This is because
		if an error had already occurred, want to get to the root of it.
		"""
		if not self.error or self.advance_count == 0: self.error = error
		return self

"""
Does actual parsing
"""
class Parser:
	def __init__(self, tokens):
		self.tokens = tokens # :[Token]:
		self.tok_index = 0 # :int:
		self.cur_token = None # :Token:
		self.advance()

	def advance(self):
		if self.tok_index < len(self.tokens):
			self.cur_token = self.tokens[self.tok_index]
		self.tok_index += 1
		return self.cur_token

	def parse(self):
		result = self.build_var_ast()
		"""
		If there wasn't an error and haven't reached end of file, then there
		is code that hasn't been parsed, so there is a syntax error.
		"""
		if not result.error and self.cur_token.type != TT_EOF:
			error = InvalidSyntaxError(self.cur_token.start_pos, self.cur_token.end_pos, "Expected '+', '-', '*', '/', or '^'")
			return result.failure(error)
		return result

	def build_var_ast(self):
		result = ParseResult()
		if self.cur_token.matches(TT_KEYWORD, KEYWORDS[0]): # var
			result.register_advancement()
			self.advance()
			if self.cur_token.type != TT_ID:
				return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
					self.cur_token.end_pos, 
					"Expected identifier"))
			var_name = self.cur_token
			result.register_advancement()
			self.advance()
			if self.cur_token.type != TT_EQ:
				return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
					self.cur_token.end_pos, 
					"Expected '='"))
			result.register_advancement()
			self.advance()
			var_expr = result.register(self.build_var_ast())
			if result.error: return result
			return result.success(VarAssignNode(var_name, var_expr))

		logical_ast = result.register(self.build_logical_ast())
		if result.error:
			return result.failure(InvalidSyntaxError(
				self.cur_token.start_pos, self.cur_token.end_pos,
				"Expected 'VAR', int, float, indentifier, '+', '-', '*', '/', '%', '(', 'not', '==', '<', '>', '<=', '>=', 'or', or 'and'"
				))
		return result.success(logical_ast)

	def build_logical_ast(self):
		result = ParseResult()
		arith_ast = result.register(self.or_expr())
		if result.error:
			return result.failure(InvalidSyntaxError(
				self.cur_token.start_pos, self.cur_token.end_pos,
				"Expected int, float, indentifier, '+', '-', '*', '/', '%', '(', 'not', '==', '<', '>', '<=', '>=', 'or', or 'and'"
				))
		return result.success(arith_ast)

	def or_expr(self):
		result = ParseResult()
		left_operand = result.register(self.and_term())
		while self.cur_token.type == TT_OR: # or
			op_token = self.cur_token
			result.register_advancement()
			self.advance()
			right_operand = result.register(self.and_term())
			if result.error: return result
			left_operand = BinaryOpNode(op_token, left_operand, right_operand)
		return result.success(left_operand)

	def and_term(self):
		result = ParseResult()
		left_operand = result.register(self.build_cmp_ast())
		while self.cur_token.type == TT_AND: # and
			op_token = self.cur_token
			result.register_advancement()
			self.advance()
			right_operand = result.register(self.build_cmp_ast())
			if result.error: return result
			left_operand = BinaryOpNode(op_token, left_operand, right_operand)
		return result.success(left_operand)

	def build_cmp_ast(self):
		result = ParseResult()
		"""
		'Not' operations needs to be evaluated from right to left
		"""
		if self.cur_token.type == TT_NOT:
			op_token = self.cur_token
			result.register_advancement()
			self.advance()
			fact_ast = result.register(self.build_cmp_ast())
			if result.error: return result
			return result.success(UnaryOpNode(op_token, fact_ast))
		left_operand = result.register(self.build_arith_ast())
		while self.cur_token.type in (TT_EQT, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE):
			op_token = self.cur_token
			result.register_advancement()
			self.advance()
			right_operand = result.register(self.build_arith_ast())
			if result.error: return result
			left_operand = BinaryOpNode(op_token, left_operand, right_operand)
		return result.success(left_operand)

	def build_arith_ast(self):
		result = ParseResult()
		arith_ast = result.register(self.expr())
		if result.error:
			return result.failure(InvalidSyntaxError(
				self.cur_token.start_pos, self.cur_token.end_pos,
				"Expected int, float, indentifier, '+', '-', '*', '/', '%', or '('"
				))
		return result.success(arith_ast)

	def expr(self):
		result = ParseResult()
		left_operand = result.register(self.term())
		while self.cur_token.type in (TT_PLUS, TT_MINUS):
			op_token = self.cur_token
			result.register_advancement()
			self.advance()
			right_operand = result.register(self.term())
			if result.error: return result
			left_operand = BinaryOpNode(op_token, left_operand, right_operand)
		return result.success(left_operand)

	def term(self):
		result = ParseResult()
		left_operand = result.register(self.signed_factor())
		while self.cur_token.type in (TT_MULT, TT_DIV, TT_MOD):
			op_token = self.cur_token
			result.register_advancement()
			self.advance()
			right_operand = result.register(self.signed_factor())
			if result.error: return result
			left_operand = BinaryOpNode(op_token, left_operand, right_operand)
		return result.success(left_operand)

	def signed_factor(self):
		result = ParseResult()
		signs = []
		while self.cur_token.type in (TT_MINUS, TT_PLUS):
			signs.append(self.cur_token)
			result.register_advancement()
			if result.error: return result
			self.advance()
		operand = result.register(self.factor())
		for sign in signs[::-1]:
			operand = UnaryOpNode(sign, operand)
		return result.success(operand)

	def factor(self):
		result = ParseResult()
		token = self.cur_token
		if token.type in (TT_INT, TT_FLOAT, TT_ID, TT_BOOL):
			operand = result.register(self.terminal())
			if result.error: return result
			return result.success(operand)
		elif token.type == TT_L_PAREN:
			result.register_advancement()
			self.advance()
			sub_expr = result.register(self.build_var_ast())
			if result.error: return result
			"""
			When amount open parenthesis doesn't match amount of closed parenthesis.
			"""
			if self.cur_token.type != TT_R_PAREN:
				error = InvalidSyntaxError(self.cur_token.start_pos, self.cur_token.end_pos, "Expected ')'")
				return result.failure(error)
			result.register_advancement()
			next_tok = self.advance()
			return self.build_exp_ast(sub_expr, next_tok, result) if next_tok.type == TT_EXP else result.success(sub_expr)
		elif token.matches(TT_KEYWORD, KEYWORDS[1]): # if
			return self.build_conditional_ast()
		elif token.matches(TT_KEYWORD, KEYWORDS[6]): # for
			return self.build_forLoop_ast();
		elif token.matches(TT_KEYWORD, KEYWORDS[10]): # while
			return self.build_whileLoop_ast();
		elif token.matches(TT_KEYWORD, KEYWORDS[12]): # def
			return self.build_decl_func_ast();
		"""
		Comes across a symbol that isn't a terminal or leads to a sub expression.
		"""
		return result.failure(
			InvalidSyntaxError(token.start_pos, token.end_pos, 
				"Expected int, float, identifier, '^', or '('")
			)

	def terminal(self):
		result = ParseResult()
		token = self.cur_token
		if token.type in (TT_INT, TT_FLOAT, TT_BOOL):
			result.register_advancement()
			next_tok = self.advance()
			num = NumberNode(token)
			return self.build_exp_ast(num, next_tok, result) if next_tok.type == TT_EXP else result.success(num)
		elif token.type == TT_ID:
			result.register_advancement()
			next_tok = self.advance()
			if next_tok.type == TT_EXP:
				return self.build_exp_ast(var, next_tok, result)
			elif next_tok.type == TT_L_PAREN:
				func_call_ast = result.register(self.build_func_call_ast(token))
				if result.error: return result
				token = self.cur_token
				return self.build_exp_ast(func_call_ast, token, result) if token.type == TT_EXP else result.success(func_call_ast)
			else:
				return result.success(VarAccessNode(token))
		# Comes across a symbol that isn't a terminal or leads to a sub expression.
		return result.failure(
			InvalidSyntaxError(token.start_pos, token.end_pos, 
				"Expected int, float, or identifier")
			)

	"""
	If there is an exponent, build tree for it first. The exponent could
	either be a number, expression around parenthesis, or another exponent.
	It falls into the category of a factor.
	"""
	def build_exp_ast(self, left_operand, expo, result):
		result.register_advancement()
		self.advance()
		exp_fact = result.register(self.factor())
		if result.error: return result
		return result.success(BinaryOpNode(expo, left_operand, exp_fact)) 

	def build_conditional_ast(self):
		# Parse if statement
		result = ParseResult()
		result.register_advancement()
		self.advance()
		if_cond = result.register(self.build_logical_ast()) # Condition for if
		if result.error: return result
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[2]): # then
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'then'"))
		result.register_advancement()
		self.advance()
		if_expr = result.register(self.build_var_ast()) # Expression for if
		if result.error: return result

		# Parse elif statements if exists
		elif_conds_exprs = [] # List of tuples of elif condition and elif expression
		while self.cur_token.matches(TT_KEYWORD, KEYWORDS[3]): # elif
			result.register_advancement()
			self.advance()
			elif_cond = result.register(self.build_logical_ast()) # Condition for elif
			if result.error: return result
			if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[2]): # then
				return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
					self.cur_token.end_pos, 
					"Expected 'then'"))
			result.register_advancement()
			self.advance()
			elif_expr = result.register(self.build_var_ast()) # Expression for elif
			if result.error: return result
			elif_conds_exprs.append((elif_cond, elif_expr))

		# Parse else statement if exists.
		else_expr = None
		if self.cur_token.matches(TT_KEYWORD, KEYWORDS[4]): # else
			result.register_advancement()
			self.advance()
			else_expr = result.register(self.build_var_ast()) # Statement for else
			if result.error: return result

		# All conditionals must end in enfif
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[5]): # endif
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'endif'"))
		result.register_advancement()
		self.advance()
		return result.success(ConditionalNode(if_cond, if_expr, elif_conds_exprs, else_expr))

	def build_forLoop_ast(self):
		result = ParseResult()
		result.register_advancement()
		self.advance()
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[0]): # var
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'var'"))
		result.register_advancement()
		self.advance()
		if self.cur_token.type != TT_ID:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected identifier"))
		var_name = self.cur_token
		result.register_advancement()
		self.advance()
		if self.cur_token.type != TT_EQ:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected '='"))
		result.register_advancement()
		self.advance()
		init_expr = result.register(self.build_arith_ast())
		if result.error: return result
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[7]): # to
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'to'"))
		result.register_advancement()
		self.advance()
		final_expr = result.register(self.build_arith_ast())
		if result.error: return result
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[8]): # then
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'do'"))
		result.register_advancement()
		self.advance()
		loop_expr = result.register(self.build_var_ast())
		if result.error: return result
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[9]): # endfor
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'endfor'"))
		result.register_advancement()
		self.advance()
		return result.success(ForLoopNode(var_name, init_expr, final_expr, loop_expr))

	def build_whileLoop_ast(self):
		result = ParseResult()
		result.register_advancement()
		self.advance()
		while_cond = result.register(self.build_logical_ast())
		if result.error: return result
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[8]): # then
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'do'"))
		result.register_advancement()
		self.advance()
		loop_expr = result.register(self.build_var_ast())
		if result.error: return result
		if not self.cur_token.matches(TT_KEYWORD, KEYWORDS[11]): # endwhile
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected 'endwhile'"))
		result.register_advancement()
		self.advance()
		return result.success(WhileLoopNode(while_cond, loop_expr))

	def build_decl_func_ast(self):
		result = ParseResult()
		result.register_advancement()
		self.advance()
		if self.cur_token.type != TT_ID:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected identifier"))
		func_name = self.cur_token
		result.register_advancement()
		self.advance()
		if self.cur_token.type != TT_L_PAREN:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected '('"))
		result.register_advancement()
		self.advance()
		params = []
		while self.cur_token.type == TT_ID:
			params.append(self.cur_token)
			result.register_advancement()
			self.advance()
			if self.cur_token.type == TT_R_PAREN: break
			if self.cur_token.type != TT_COMMA:
				return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
					self.cur_token.end_pos, 
					"Expected ','"))
			result.register_advancement()
			self.advance()
		if self.cur_token.type != TT_R_PAREN:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected ')'"))
		result.register_advancement()
		self.advance()
		if self.cur_token.type != TT_L_C_BRACK:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected '{'"))
		result.register_advancement()
		self.advance()
		func_ast = result.register(self.build_var_ast())
		if result.error: return result
		if self.cur_token.type != TT_R_C_BRACK:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected '}'"))
		return result.success(FuncDeclNode(func_name, params, func_ast))

	def build_func_call_ast(self, func_name):
		result = ParseResult()
		result.register_advancement()
		self.advance()
		# parse through all the arguments.
		args = []
		while self.cur_token.type != TT_COMMA:
			if self.cur_token.type == TT_R_PAREN: break
			arg = result.register(self.build_logical_ast())
			if result.error: return result
			args.append(arg)
			if self.cur_token.type == TT_COMMA:
				result.register_advancement()
				self.advance()
		if self.cur_token.type != TT_R_PAREN:
			return result.failure(InvalidSyntaxError(self.cur_token.start_pos, 
				self.cur_token.end_pos, 
				"Expected ')'"))
		result.register_advancement()
		self.advance()
		return result.success(FuncCallNode(func_name, args))




















