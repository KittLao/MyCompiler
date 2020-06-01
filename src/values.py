from errors import RunTimeError

class Primitives:
	def __init__(self, value):
		self.value = value # int, float, boolean, Node, None
		self.set_pos()
		self.set_context()

	def __repr__(self):
		return f"{self.value}"

	def set_pos(self, start_pos=None, end_pos=None):
		self.start_pos = start_pos
		self.end_pos = end_pos
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def copy(self):
		copy = Value(self.value)
		copy.set_pos(self.start_pos, self.end_pos)
		copy.set_context(self.context)
		return copy


class Value(Primitives):
	def __init__(self, value):
		Primitives.__init__(self, value)

	# :Value: -> :Value:
	def add_to(self, other):
		if isinstance(other, Value):
			return Value(self.value + other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def sub_by(self, other):
		if isinstance(other, Value):
			return Value(self.value - other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def mult_by(self, other):
		if isinstance(other, Value):
			return Value(self.value * other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def div_by(self, other):
		if isinstance(other, Value):
			if other.value == 0:
				return None, RunTimeError(other.start_pos,
					other.end_pos,
					"Division by zero",
					self.context)
			return Value(self.value / other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def pow_of(self, other):
		if isinstance(other, Value):
			return Value(self.value ** other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def mod_by(self, other):
		if isinstance(other, Value):
			if other.value == 0:
				return None, RunTimeError(other.start_pos,
					other.end_pos,
					"Modulo by zero",
					self.context)
			return Value(self.value % other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def negate(self):
		if isinstance(self, Value):
			return Value(not self.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def eq_to(self, other):
		if isinstance(other, Value):
			return Value(self.value == other.value).set_context(self.context), None 
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def not_eq_to(self, other):
		if isinstance(other, Value):
			return Value(self.value != other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def less_than(self, other):
		if isinstance(other, Value):
			return Value(self.value < other.value).set_context(self.context), None 
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def grt_than(self, other):
		if isinstance(other, Value):
			return Value(self.value > other.value).set_context(self.context), None 
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def less_eq(self, other):
		if isinstance(other, Value):
			return Value(self.value <= other.value).set_context(self.context), None 
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def grt_eq(self, other):
		if isinstance(other, Value):
			return Value(self.value >= other.value).set_context(self.context), None 
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def and_by(self, other):
		if isinstance(other, Value):
			return Value(self.value and other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

	def or_by(self, other):
		if isinstance(other, Value):
			return Value(self.value or other.value).set_context(self.context), None
		return None, RunTimeError(other.start_pos, other.end_pos,
					"Requires 'Value' type", self.context)

class FunctionValue(Primitives):
	def __init__(self, func_node, context):
		Primitives.__init__(self, func_node)
		self.relative_context = context

	def get_declared_name(self):
		return self.value.func_name.value







