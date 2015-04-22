class Error(Exception):
  '''Base class for exceptions in this module.'''
  def __init__(self, parser):
    self.msg = 'Invalid syntax'
    self.msg += '\n' + self.show_error_location(parser)

  def __str__(self):
    return self.msg

  def show_error_location(self, parser):
    arg_string = parser.arg_string
    index = parser.arg_string.find(parser.current_token, parser.approximate_location)
    if index >= 0:
      return arg_string + '\n' + ' ' * index + '^'
    else:
      return arg_string + '\n' + ' ' * len(arg_string) + '^'

class NewExpressionError(Error):
  '''
  Exception raised when a new expression does not start with expr
  '''
  def __init__(self, parser):
    self.msg = 'Each expression must start with expr\n'
    self.msg += '\n' + self.show_error_location(parser)

class NewNestedExpressionError(Error):
  '''
  Exception raised when a new nested expression does not start with expr
  '''
  def __init__(self, parser):
    self.msg = 'Each nested expression must start with expr\nIf you were trying to use an open square bracket ([) as an expression, remember to use a valid modifier and end with a semicolon.'
    self.msg += '\n' + self.show_error_location(parser)

class UnclosedBracketError(Error):
  '''
  Exception raised when a nested expression is not finished
  '''
  def __init__(self, parser):
    self.msg = 'Each nested expression must end with a closed square bracket\nIf you were trying to use an open square bracket ([) as an expression, remember to use a valid modifier and end with a semicolon.'
    self.msg += '\n' + self.show_error_location(parser)

class IncompleteExpressionError(Error):
  '''
  Exception raised when a new expression is empty
  '''
  def __init__(self, parser):
    self.msg = 'Each expression must end in a semi-colon.\nFor empty input, remember to use quotes.'
    self.msg += '\n' + self.show_error_location(parser)

class IncompleteClassError(Error):
  '''
  Exception raised when an expression ends on the keyword "of" indicating a class
  '''
  def __init__(self, parser):
    self.msg = 'Keywords "of" and "except" must be followed by the set of characters to be included in the class.\nEmpty string can not be put into character class.'
    self.msg += '\n' + self.show_error_location(parser)

class IncompleteClassRangeError(Error):
  '''
  Exception raised when an expression ends on the keyword "from" or "to", indicating a range in a class
  '''
  def __init__(self, parser):
    self.msg = 'When specifying a range of characters in a character class, you must have both a "from" value and a "to" value.\nFor example: expr: any_char from "a" to "z";'
    self.msg += '\n' + self.show_error_location(parser)

class InvalidClassRangeError(Error):
  '''
  Exception raised when a class range indicated is somehow invalid
  To be valid, class ranges must be between single characters that are in order
  '''
  def __init__(self, parser):
    self.msg = 'Class range must be between single characters, and they must be in order.'
    self.msg += '\n' + self.show_error_location(parser)

class IncompleteOrError(Error):
  '''
  Exception raised when expression ends right after or symbol (|)
  '''
  def __init__(self, parser):
    self.msg = 'Invalid syntax after or.\nTo make an empty or alternative, remember to put the empty string in quotes and still end with a semicolon.'
    self.msg += '\n' + self.show_error_location(parser)

class MultipleOrError(Error):
  '''
  Exception raised when multiple expressions occur at the same nesting level as an or
  '''
  def __init__(self, parser):
    self.msg = '''Expressions involving the keyword or cannot be follow or be followed by other expressions.\nTo include or statements in larger expressions, nest them.\nFor example, this will not work: expr: "a" or "b"; expr: "c";\nNether will this: expr: "a"; expr: "b" or "c";\nBut, if you wanted to have either a or b followed by c, you could do this: expr: [ expr: "a" or "b";]; expr: "c";\nThe same logic applies for a followed by b or c.'''
    self.msg += '\n' + self.show_error_location(parser)

class ColonError(Error):
  '''
  Exception raised when there is a missing colon
  '''
  def __init__(self, parser):
    self.msg = 'expr needs a colon'
    self.msg += '\n' + self.show_error_location(parser)

class InvalidModifierError(Error):
  '''
  Exception raised when an expr value is followed by something other than a key word or end bracket
  '''
  def __init__(self, parser):
    self.msg = '''Invalid modifier for an expression.\nPossible Causes:\n- A missing semi-colon at the end of an expression\n- A misplaced "expr:" after the keyword "or"\n- An empty expression or expression with a special character that is not put in quotes.\n- Incorrect usage of or_of, or_except, and or_from: or_of and or_except are valid after both "of" and "from...to" expressions, but or_except can only follow "except" expressions\n- Modifying an unmodifiable expression, such as start_of_string or end_of_string'''
    self.msg += '\n' + self.show_error_location(parser)

class InvalidRepetitionsError(Error):
  '''
  Exception raised when keyword for is followed by an incorrect token
  '''
  def __init__(self, parser):
    self.msg = 'Invalid number of repetitions specified after key word "for"\nValid repetitions include integers or keywords such as zero_or_more or one_or_zero'
    self.msg += '\n' + self.show_error_location(parser)

class InvalidRepetitionRangeError(Error):
  '''
  Exception raised when keyword up_to is followed by an incorrect token
  '''
  def __init__(self, parser):
    self.msg = 'Invalid number of repetitions specified after key word "up_to"\nMust be followed by an integer greater than or equal to the first number, or else the infinity keyword.'
    self.msg += '\n' + self.show_error_location(parser)

if __name__ == '__main':
  pass
