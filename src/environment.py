class Environment:
	def __init__(self, parent=None):
		# :string: => :Value: if environment
		# :string: => :Node: if func_env
		self.symbols = {}
		self.parent = parent # :Environment:

	"""
	Will refer to the symbol in the most current
	environment. If it doesn't exist, return None.
	"""
	def get(self, var_name):
		value = self.symbols.get(var_name, None)
		if value == None and self.parent:
			return self.parent.get(var_name)
		return value

	"""
	The symbol in the most current environment will get updated.
	If the symbol doesn't exist, then a new one will be created
	in the most current environment.
	"""
	def set(self, var_name, var_value):
		"""
		If symbol doesn't exist at all, create new one in current
		environment.
		"""
		if not self.set_exists(self, var_name, var_value):
			self.symbols[var_name] = var_value

	"""
	:Environment: -> :string: -> :Value: -> :Boolean:
	"""
	def set_exists(self, env, var_name, var_value):
		if env == None: # If does't exist at all.
			return False
		if var_name in env.symbols: # If exists in current environment, just update.
			env.symbols[var_name] = var_value
			return True
		else:
			return self.set_exists(env.parent, var_name, var_value) # Check if exist in parent.


	"""
	Will remove the symbol in the most current environment
	"""
	def remove(self, var_name):
		if var_name in self.symbols:
			del self.symbols[var_name]

class FunctionEnvironment(Environment):
	def __init__(self, parent=None):
		super().__init__(parent)
























