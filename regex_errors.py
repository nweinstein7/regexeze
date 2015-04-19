import regex_interface

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
    self.msg = 'Invalid modifier for an expression. Expressions must end in semi-colon.'
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
    self.msg = 'Invalid number of repetitions specified after key word "up_to"\nMust be followed by an integer or the infinity keyword.'
    self.msg += '\n' + self.show_error_location(parser)

if __name__ == '__main':
  pass
