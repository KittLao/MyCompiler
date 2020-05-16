from tokens import *
from errors import *
from position import Position
import string

IRRELEVENT_SYMBOLS = " \n\t" # The shit that we ignore
DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

class Lexer:
	"""
	:string: -> :string:
	"""
	def __init__(self, file_name, text):
		self.text = text
		self.file_name = file_name
		self.pos = Position(-1, 0, -1, file_name, text)
		self.cur_symbol = None
		self.advance()

	def advance(self):
		self.pos.advance(self.cur_symbol)
		self.cur_symbol = self.text[self.pos.index] if self.pos.index < len(self.text) else None

	def generate_tokens(self):
		tokens = []
		while self.cur_symbol != None:
			if self.cur_symbol in IRRELEVENT_SYMBOLS:
				self.advance()
			elif self.cur_symbol in DIGITS + '.':
				tokens.append(self.generate_number())
			elif self.cur_symbol in LETTERS: # Gaurantees first symbol has to be a letter. The rest can be any.
				tokens.append(self.generate_word()) # Either keyword, variable, boolean or word oeprator.
			elif self.cur_symbol == '+':
				tokens.append(Token(TT_PLUS, start_pos=self.pos))
				self.advance()
			elif self.cur_symbol == '-':
				tokens.append(Token(TT_MINUS, start_pos=self.pos))
				self.advance()
			elif self.cur_symbol == '*':
				tokens.append(Token(TT_MULT, start_pos=self.pos))
				self.advance()
			elif self.cur_symbol == '/':
				tokens.append(self.generate_compare(TT_NE, TT_DIV))
			elif self.cur_symbol == '^':
				tokens.append(Token(TT_EXP, start_pos=self.pos))
				self.advance()
			elif self.cur_symbol == '%':
				tokens.append(Token(TT_MOD, start_pos=self.pos))
				self.advance()	
			elif self.cur_symbol == '(':
				tokens.append(Token(TT_L_PAREN, start_pos=self.pos))
				self.advance()
			elif self.cur_symbol == ')':
				tokens.append(Token(TT_R_PAREN, start_pos=self.pos))
				self.advance()
			elif self.cur_symbol == '=':
				tokens.append(self.generate_compare(TT_EQT, TT_EQ))
			elif self.cur_symbol == '<':
				tokens.append(self.generate_compare(TT_LTE, TT_LT))
			elif self.cur_symbol == '>':
				tokens.append(self.generate_compare(TT_GTE, TT_GT))
			else:
				pos_begin = self.pos.copy()
				illegal_symbol = self.cur_symbol
				self.advance()
				return ([], IllegalSymbolError(pos_begin, self.pos, "'" + illegal_symbol + "'"))
		tokens.append(Token(TT_EOF, start_pos=self.pos))
		return (tokens, None)

	def generate_number(self):
		number_str = ""
		decimal_cnt = 0
		start_pos = self.pos.copy()
		while self.cur_symbol != None and self.cur_symbol in DIGITS + '.':
			if self.cur_symbol == '.':
				decimal_cnt += 1
				if decimal_cnt > 1: break
			else:
				number_str += self.cur_symbol
			self.advance()
		if decimal_cnt == 0:
			return Token(TT_INT, int(number_str), start_pos, self.pos)
		return Token(TT_FLOAT, float(number_str), start_pos, self.pos)

	def generate_word(self):
		id_str = ""
		pos_start = self.pos.copy()
		while self.cur_symbol != None and self.cur_symbol in LETTERS_DIGITS + '_':
			id_str += self.cur_symbol
			self.advance()
		if id_str in KEYWORDS:
			tok_type = TT_KEYWORD
		elif id_str in BOOLEANS:
			tok_type = TT_BOOL
			id_str = True if id_str == "True" else False
		elif id_str in WORD_OPERATOR:
			if id_str == "and":
				tok_type = TT_AND
			elif id_str == "or":
				tok_type = TT_OR
			else:
				tok_type = TT_NOT
		else:
			tok_type = TT_ID
		return Token(tok_type, id_str, pos_start, self.pos)

	def generate_compare(self, cmp_tok_a, cmp_tok_b):
		start_pos = self.pos.copy()
		self.advance()
		if self.cur_symbol == '=':
			self.advance()
			return Token(cmp_tok_a, start_pos=start_pos, end_pos=self.pos)
		return Token(cmp_tok_b, start_pos=start_pos, end_pos=self.pos)


















