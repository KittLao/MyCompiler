from error_utilities import *

class Error:
	def __init__(self, pos_begin, pos_end, error_name, details):
		self.pos_begin = pos_begin
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details

	def as_string(self):
		error_msg = f"{self.error_name}: {self.details} "
		error_msg += f"File {self.pos_begin.file_name}, line {self.pos_begin.line + 1}"
		error_msg += "\n\n" + string_with_arrows(self.pos_begin.file_text, self.pos_begin, self.pos_end)
		return error_msg

"""
When lexer comes across a character it doesn't support.
"""
class IllegalSymbolError(Error):
	def __init__(self, pos_begin, pos_end, details):
		super().__init__(pos_begin, pos_end, "Illegal symbol", details)


"""
When parser detects a syntax that is not part of the grammar rules.
"""
class InvalidSyntaxError(Error):
	def __init__(self, pos_begin, pos_end, details):
		super().__init__(pos_begin, pos_end, "Invalid syntax", details)

"""
Catch errors during runtime. 

Types of errors:
	Division by zero

:Position: -> :Position: -> :string: -> :Context:
"""
class RunTimeError(Error):
	def __init__(self, pos_begin, pos_end, details, context):
		super().__init__(pos_begin, pos_end, "RunTime error", details)
		self.context = context

	def generate_traceback(self):
			trace = ""
			pos = self.pos_begin
			ctx = self.context
			while ctx:
				trace = f"File {pos.file_name}, line {str(pos.line + 1)}, in {ctx.display_name}\n" + trace
				pos = ctx.parent_entry_pos
				ctx = ctx.parent
			return "Traceback (most recent call last):\n" + trace


	"""
	Overload from parent because runtime errors.
	"""
	def as_string(self):
		error_msg = self.generate_traceback()
		error_msg += f"{self.error_name}: {self.details} "
		error_msg += "\n\n" + string_with_arrows(self.pos_begin.file_text, self.pos_begin, self.pos_end)
		return error_msg























