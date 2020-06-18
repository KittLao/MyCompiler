class Position:
	def __init__(self, index, line, column, file_name, file_text):
		self.index = index
		self.line = line
		self.column = column
		self.file_name = file_name
		self.file_text = file_text

	def advance(self, cur_symbol=None):
		self.column += 1
		if cur_symbol in ('\n', '#'):
			self.column = 0
			self.line += 1
		return self

	def copy(self):
		return Position(self.index, self.line, self.column, self.file_name, self.file_text)