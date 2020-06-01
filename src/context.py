"""
A linked list of contexts. Each context consists of the function name, and
the parent context
"""
class Context:
	# :string: -> :Environment: -> :FunctionEnvironment: -> :Context: -> :Position:
	def __init__(self, display_name, env, func_env, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.env = env # variable environment
		self.func_env = func_env # function environment

	def get_context_relative_to(self, func_name):
		cur_ctx = self
		while cur_ctx:
			if func_name in cur_ctx.env.symbols: return cur_ctx
			cur_ctx = cur_ctx.parent

