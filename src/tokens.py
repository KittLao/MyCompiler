TT_INT = "<INT>"
TT_FLOAT = "<FLOAT>"
TT_BOOL = "<BOOL>"

TT_PLUS = "<PLUS>"
TT_MINUS = "<MINUS>"
TT_MULT = "<MULT>"
TT_DIV = "<DIV>"
TT_EXP = "<EXP>"
TT_MOD = "<MOD>"

TT_L_PAREN = "<L_PAREN>"
TT_R_PAREN = "<R_PAREN>"
TT_L_C_BRACK = "<L_C_BRACK>"
TT_R_C_BRACK = "<R_C_BRACK>"
TT_COMMA = "<COMMA>"

TT_WORD_OPERATOR = "<WORD_OPERATOR>"
TT_KEYWORD = "<KEYWORD>"
TT_ID = "<ID>"
TT_EQ = "<EQ>"

TT_NOT = "<NOT>"
TT_OR = "<OR>"
TT_AND = "<AND>"
TT_EQT = "<EQT>"
TT_NE = "<NE>"
TT_LT = "<LT>"
TT_GT = "<GT>"
TT_LTE = "<LTE>"
TT_GTE = "<GTE>"

TT_EOF = "<EOF>"

"""
List of keywords for program to help separate variable names from keywords
"""
KEYWORDS = [
	"var", # 0
	"if", # 1
	"elif", # 2
	"else", # 3
	"for", # 4
	"to", # 5
	"while", # 6
	"def", # 7
	"return" # 8
]

BOOLEANS = [
	"True",
	"False"
]

WORD_OPERATOR = [
	"or",
	"and",
	"not"
]

class Token:
	# :string: -> :{string, int, float, boolean}: -> :Position: -> :Position:
	def __init__(self, type_, value=None, start_pos=None, end_pos=None):
		self.type = type_ # :TT_:
		self.value = value # :{string, int, float, boolean}:
		if start_pos:
			self.start_pos = start_pos.copy()
			self.end_pos = start_pos.copy()
			self.end_pos.copy()
		if end_pos:
			self.start_pos = end_pos.copy()

	def __repr__(self):
		return f"{self.type}" if self.value == None else f"{self.type}:{self.value}"

	# :TT_: -> :{string, int, float}: -> :Boolean:
	def matches(self, type_, value):
		return self.type == type_ and self.value == value













