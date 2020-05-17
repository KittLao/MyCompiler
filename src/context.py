"""
A linked list of contexts. Each context consists of the function name, and
the parent context
"""
class Context:
	# :string: -> :Context: -> :Position:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.env = None # data environment
		self.func_env = None # function environemnt