import regexeze_errors
import regexeze
import re

class RegexState(object):
  '''
  A state of the RegexParserMachine
  '''
  END_OF_EXPRESSIONS = 'EndOfExpressions'
  ANY_CHAR = 'AnyChar'
  START_EXPRESSION = 'StartExpression'
  CHECK_COLON = 'CheckColon'
  NEW_EXPRESSION = 'NewExpression'
  NEW_EXPRESSION_ERROR_STATE = 'NewExpressionErrorState'
  COLON_ERROR_STATE = 'ColonErrorState'
  PLAIN_TEXT = 'PlainText'
  CHECK_NUMBER_OF_TIMES = 'CheckNumberOfTimes'
  INVALID_MODIFIER_STATE = 'InvalidModifierState'
  BASE_ERROR_STATE = 'BaseErrorState'
  ZERO_OR_MORE = 'ZeroOrMore'
  INVALID_REPETITIONS_ERROR_STATE = 'InvalidRepetitionsErrorState'
  INCOMPLETE_EXPRESSION_ERROR_STATE = 'IncompleteExpressionErrorState'
  SET_GREEDY = 'SetGreedy'
  KEEP_GREEDY = 'KeepGreedy'
  SET_NOT_GREEDY = 'SetNotGreedy'
  KEEP_NOT_GREEDY = 'KeepNotGreedy'
  ONE_OR_MORE = 'OneOrMore'
  ZERO_OR_ONE = 'ZeroOrOne'
  M_REPETITIONS = 'MRepetitions'
  UP_TO = 'UpTo'
  INVALID_REPETITION_RANGE_ERROR_STATE = 'InvalidRepetitionRangeErrorState'
  M_UP_TO_N_REPETITIONS = 'MUpToNRepetitions'
  M_UP_TO_INFINITY_REPETITIONS = 'MUpToInfinityRepetitions'
  NEW_NESTED_EXPRESSION = 'NewNestedExpression'
  NESTED_EXPRESSION = 'NestedExpression'
  NESTED_EXPRESSION_DOWN_LEVEL = 'NestedExpressionDownLevel'
  NESTED_EXPRESSION_UP_LEVEL = 'NestedExpressionUpLevel'
  END_NESTED_EXPRESSION = 'EndNestedExpression'
  NEW_NESTED_EXPRESSION_ERROR_STATE = 'NewNestedExpressionErrorState'
  UNCLOSED_BRACKET_ERROR_STATE = 'UnclosedBracketErrorState'
  OR = 'Or'
  INCOMPLETE_OR_ERROR_STATE = 'IncompleteOrErrorState'
  MULTIPLE_OR_ERROR_STATE = 'MultipleOrErrorState'
  OPEN_CLASS = 'OpenClass'
  CLASS_STATE = 'ClassState'
  INCOMPLETE_CLASS_ERROR_STATE = 'IncompleteClassErrorState'
  OR_OF = 'OrOf'
  FROM = 'From'
  INCOMPLETE_CLASS_RANGE_ERROR_STATE = 'IncompleteClassRangeErrorState'
  INVALID_CLASS_RANGE_ERROR_STATE = 'InvalidClassRangeErrorState'
  TO = 'To'
  OPEN_CLASS_RANGE = 'OpenClassRange'
  OR_FROM = 'OrFrom'
  EXCEPT = 'Except'
  COMPLEMENT_CLASS_STATE = 'ComplementClassState'
  OR_EXCEPT = 'OrExcept'
  START_OF_STRING = 'StartOfString'
  END_OF_STRING = 'EndOfString'

  ZERO_OR_MORE_SYMBOL = '*'
  ZERO_OR_ONE_SYMBOL = '?'
  NOT_GREEDY_SYMBOL = '?'
  ANY_CHAR_SYMBOL = '.'
  ONE_OR_MORE_SYMBOL = '+'
  END_OF_EXPRESSION_SYMBOL = ';'
  M_REPETITIONS_FORMAT = '{{{0}}}'
  OPEN_CLASS_SYMBOL = '['
  CLOSE_CLASS_SYMBOL = ']'
  CLASS_RANGE_SYMBOL = '-'
  COMPLEMENT_CLASS_SYMBOL = '^'
  START_OF_STRING_SYMBOL = '^'
  END_OF_STRING_SYMBOL = '$'

  END_OF_INPUT_TOKEN = 'end_of_input'
  GREEDY_TOKEN = 'greedy'
  NOT_GREEDY_TOKEN = 'not_greedy'
  ZERO_OR_MORE_TOKEN = 'zero_or_more'
  ZERO_OR_ONE_TOKEN = 'zero_or_one'
  ONE_OR_MORE_TOKEN = 'one_or_more'
  UP_TO_TOKEN = 'up_to'
  EXPRESSION_TOKEN = 'expr'
  ANY_CHAR_TOKEN = 'any_char'
  INFINITY_TOKEN = 'infinity'
  NESTED_OPEN_TOKEN = '['
  NESTED_CLOSE_TOKEN = ']'
  COLON_TOKEN = ':'
  CHECK_NUMBER_OF_TIMES_TOKEN = 'for'
  OR_TOKEN = 'or'
  OF_TOKEN = 'of'
  OR_OF_TOKEN = 'or_of'
  FROM_TOKEN = 'from'
  TO_TOKEN = 'to'
  OR_FROM_TOKEN = 'or_from'
  EXCEPT_TOKEN = 'except'
  OR_EXCEPT_TOKEN = 'or_except'
  START_OF_STRING_TOKEN = 'start_of_string'
  END_OF_STRING_TOKEN = 'end_of_string'

  def __init__(self):
    self.transitions = {}

  def do_action(self, parser):
    '''
    If states perform actions on the parser machine, it will be implemented here
    '''
    pass

  def get_next(self, token):
    '''
    Get the next state based on the token
    @param token: the token (taken from the input) to be used for prompting the transition
    @type token: string
    @return: the next state object
    @rtype: RegexState
    '''
    if token in self.transitions:
      return self.transitions[token]
    else:
      return self.get_token_not_found_transition(token)

  def get_token_not_found_transition(self, token):
    '''
    If a token is not in the list of transitions, go to the proper state
    @return: a string corresponding to a state
    @rtype: string
    '''
    return self.BASE_ERROR_STATE

class PotentiallyFinalRegexState(RegexState):
  '''
  Generic parent state for any state which could theoretically be followed by a semi-colon (new expression) or end of input
  '''
  def __init__(self):
    super(PotentiallyFinalRegexState, self).__init__()
    self.transitions[self.END_OF_EXPRESSION_SYMBOL] = self.NEW_EXPRESSION
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_EXPRESSION_ERROR_STATE

  def get_token_not_found_transition(self, token):
    if token == self.OR_TOKEN and self.n_expressions > 0:
      return self.MULTIPLE_OR_ERROR_STATE
    elif token == self.OR_TOKEN:
      return self.OR
    return self.INVALID_MODIFIER_STATE

  def do_action(self, parser):
    self.n_expressions = parser.n_expressions

class ModifiablePotentiallyFinalRegexState(PotentiallyFinalRegexState):
  '''
  Generic parent state for potentially final states which can segue into check number of times states
  '''
  def __init__(self):
    super(ModifiablePotentiallyFinalRegexState, self).__init__()
    self.transitions[self.CHECK_NUMBER_OF_TIMES_TOKEN] = self.CHECK_NUMBER_OF_TIMES

  def do_action(self, parser):
    super(ModifiablePotentiallyFinalRegexState, self).do_action(parser)

class BaseErrorState(RegexState):
  '''
  State for generic errors (placeholder - ideally, every eventuality will have a specific error)
  '''
  def do_action(self, parser):
    raise regexeze_errors.Error(parser)

class NotGreedyNumberOfRepetitionsState(PotentiallyFinalRegexState):
  '''
  State in which a certain number of repetitions have been selected
  (Default not greedy!)
  '''
  def __init__(self):
    super(NotGreedyNumberOfRepetitionsState, self).__init__()
    self.symbol = ''
    self.transitions[self.GREEDY_TOKEN] = self.SET_GREEDY
    self.transitions[self.NOT_GREEDY_TOKEN] = self.KEEP_NOT_GREEDY

  def do_action(self, parser):
    super(NotGreedyNumberOfRepetitionsState, self).do_action(parser)
    parser.current_modifier = self.symbol + self.NOT_GREEDY_SYMBOL

class GreedyNumberOfRepetitionsState(PotentiallyFinalRegexState):
  '''
  State in which a certain number of repetitions have been selected
  (Default greedy!)
  '''
  def __init__(self):
    super(GreedyNumberOfRepetitionsState, self).__init__()
    self.symbol = ''
    self.transitions[self.NOT_GREEDY_TOKEN] = self.SET_NOT_GREEDY
    self.transitions[self.GREEDY_TOKEN] = self.KEEP_GREEDY

  def do_action(self, parser):
    super(GreedyNumberOfRepetitionsState, self).do_action(parser)
    parser.current_modifier = self.symbol

class EndOfExpressions(RegexState):
  def __init__(self):
    pass

class NewExpressionErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.NewExpressionError(parser)

class NewNestedExpressionErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.NewNestedExpressionError(parser)

class UnclosedBracketErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.UnclosedBracketError(parser)

class IncompleteExpressionErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.IncompleteExpressionError(parser)

class IncompleteClassErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.IncompleteClassError(parser)

class IncompleteClassRangeErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.IncompleteClassRangeError(parser)

class InvalidClassRangeErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.InvalidClassRangeError(parser)

class IncompleteOrErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.IncompleteOrError(parser)

class MultipleOrErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.MultipleOrError(parser)

class ColonErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.ColonError(parser)

class InvalidModifierState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.InvalidModifierError(parser)

class InvalidRepetitionsErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.InvalidRepetitionsError(parser)

class InvalidRepetitionRangeErrorState(RegexState):
  def do_action(self, parser):
    raise regexeze_errors.InvalidRepetitionRangeError(parser)

class StartExpression(RegexState):
  def __init__(self):
    super(StartExpression, self).__init__()
    self.transitions[self.ANY_CHAR_TOKEN] = self.ANY_CHAR
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_EXPRESSION_ERROR_STATE
    self.transitions[self.NESTED_OPEN_TOKEN] = self.NEW_NESTED_EXPRESSION
    self.transitions[self.START_OF_STRING_TOKEN] = self.START_OF_STRING
    self.transitions[self.END_OF_STRING_TOKEN] = self.END_OF_STRING

  def get_token_not_found_transition(self, token):
    return self.PLAIN_TEXT

  def do_action(self, parser):
    parser.child = regexeze.RegexParserMachine('')

class Or(StartExpression):
  '''
  Inserts a pipe between two alternatives
  '''
  def __init__(self):
    super(Or, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_OR_ERROR_STATE

  def do_action(self, parser):
    parser.add_current_fragment()
    parser.add_or()
    parser.child = regexeze.RegexParserMachine('')
    parser.after_or = True


class SetGreedy(PotentiallyFinalRegexState):
  '''
  Tells the number of repetitions to be greedy
  '''
  def __init__(self):
    super(SetGreedy, self).__init__()

  def do_action(self, parser):
    super(SetGreedy, self).do_action(parser)
    parser.current_modifier = parser.current_modifier[:-1]

class KeepGreedy(PotentiallyFinalRegexState):
  '''
  Keeps the number of repetitions greedy when that is the default
  '''
  def __init__(self):
    super(KeepGreedy, self).__init__()

class SetNotGreedy(PotentiallyFinalRegexState):
  '''
  Tells the number of repetitions not to be greedy
  '''
  def __init__(self):
    super(SetNotGreedy, self).__init__()

  def do_action(self, parser):
    super(SetNotGreedy, self).do_action(parser)
    parser.current_modifier = parser.current_modifier + self.NOT_GREEDY_SYMBOL

class KeepNotGreedy(PotentiallyFinalRegexState):
  '''
  Keeps the number of repetitions not to greedy when that is default
  '''
  def __init__(self):
    super(KeepNotGreedy, self).__init__()

class ZeroOrMore(GreedyNumberOfRepetitionsState):
  '''
  State in which zero_or_more repetitions have been selected
  '''
  def __init__(self):
    super(ZeroOrMore, self).__init__()
    self.symbol = self.ZERO_OR_MORE_SYMBOL

class OneOrMore(GreedyNumberOfRepetitionsState):
  '''
  State in which one_or_more repetitions have been selected
  '''
  def __init__(self):
    super(OneOrMore, self).__init__()
    self.symbol = self.ONE_OR_MORE_SYMBOL

class ZeroOrOne(GreedyNumberOfRepetitionsState):
  '''
  State in which zero_or_one repetitions have been selected
  '''
  def __init__(self):
    super(ZeroOrOne, self).__init__()
    self.symbol = self.ZERO_OR_ONE_SYMBOL

class UpTo(RegexState):
  '''
  State triggered by the up_to keyword - in between upper and lower range of {m,n} modifier
  Strips the {m} modifier of its curly braces for further modification
  '''
  def __init__(self):
    super(UpTo, self).__init__()
    self.transitions[self.INFINITY_TOKEN] = self.M_UP_TO_INFINITY_REPETITIONS

  def get_token_not_found_transition(self, token):
    if token.isdigit():
      return self.M_UP_TO_N_REPETITIONS
    else:
      return self.INVALID_REPETITION_RANGE_ERROR_STATE

class MUpToNRepetitions(GreedyNumberOfRepetitionsState):
  '''
  State in which between m and n repetitions have been selected
  '''
  def __init__(self):
    super(MUpToNRepetitions, self).__init__()
    self.symbol = self.M_REPETITIONS_FORMAT

  def do_action(self, parser):
    super(MUpToNRepetitions, self).do_action(parser)
    parser.current_modifier_fragment = parser.current_modifier_fragment + "," + parser.current_token
    parser.current_modifier = self.symbol.format(parser.current_modifier_fragment)

class MUpToInfinityRepetitions(GreedyNumberOfRepetitionsState):
  '''
  State in which between m and infinite repetitions have been selected
  '''
  def __init__(self):
    super(MUpToInfinityRepetitions, self).__init__()
    self.symbol = self.M_REPETITIONS_FORMAT

  def do_action(self, parser):
    parser.current_modifier_fragment = parser.current_modifier_fragment + ","
    parser.current_modifier = self.symbol.format(parser.current_modifier_fragment)

class MRepetitions(GreedyNumberOfRepetitionsState):
  '''
  State in which m repetitions have been selected
  '''
  def __init__(self):
    super(MRepetitions, self).__init__()
    self.transitions[self.UP_TO_TOKEN] = self.UP_TO
    self.symbol = self.M_REPETITIONS_FORMAT

  def do_action(self, parser):
    super(MRepetitions, self).do_action(parser)
    parser.current_modifier_fragment = parser.current_token
    parser.current_modifier = self.symbol.format(parser.current_modifier_fragment)

class CheckNumberOfTimes(RegexState):
  '''
  State in which keyword for has been used to indicate number of repetitions
  '''
  def __init__(self):
    super(CheckNumberOfTimes, self).__init__()
    self.transitions[self.ZERO_OR_MORE_TOKEN] = self.ZERO_OR_MORE
    self.transitions[self.ONE_OR_MORE_TOKEN] = self.ONE_OR_MORE
    self.transitions[self.ZERO_OR_ONE_TOKEN] = self.ZERO_OR_ONE

  def get_token_not_found_transition(self, token):
    if token.isdigit():
      return self.M_REPETITIONS
    return self.INVALID_REPETITIONS_ERROR_STATE

class OrFrom(RegexState):
  '''
  State in which a class has been continued using the keyword or_from, indicating a new range of chars
  '''
  def __init__(self):
    super(OrFrom, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_ERROR_STATE

  def get_token_not_found_transition(self, token):
    if len(token) == 1:
      return self.OPEN_CLASS_RANGE
    else:
      return self.INVALID_CLASS_RANGE_ERROR_STATE

  def do_action(self, parser):
    parser.current_fragment = parser.current_fragment[:-1]

class OrExcept(RegexState):
  '''
  State in which a complement class has been continued using the keyword or_except
  '''
  def __init__(self):
    super(OrExcept, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_ERROR_STATE

  def do_action(self, parser):
    parser.current_fragment = parser.current_fragment[:-1]

  def get_token_not_found_transition(self, token):
    if token == '':
      return self.INCOMPLETE_CLASS_ERROR_STATE
    return self.COMPLEMENT_CLASS_STATE

class OrOf(RegexState):
  '''
  State in which a class has been continued using the keyword or_of
  '''
  def __init__(self):
    super(OrOf, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_ERROR_STATE

  def do_action(self, parser):
    parser.current_fragment = parser.current_fragment[:-1]

  def get_token_not_found_transition(self, token):
    if token == '':
      return self.INCOMPLETE_CLASS_ERROR_STATE
    return self.CLASS_STATE

class ClassState(ModifiablePotentiallyFinalRegexState):
  '''
  State in which a class value has been indicated (or in which a class range has been ended)
  '''
  def __init__(self):
    super(ClassState, self).__init__()
    self.transitions[self.OR_OF_TOKEN] = self.OR_OF
    self.transitions[self.OR_FROM_TOKEN] = self.OR_FROM

  def do_action(self, parser):
    super(ClassState, self).do_action(parser)
    parser.end_class()

class ComplementClassState(ModifiablePotentiallyFinalRegexState):
  '''
  State in which a complement class value has been indicated
  '''
  def __init__(self):
    super(ComplementClassState, self).__init__()
    self.transitions[self.OR_EXCEPT_TOKEN] = self.OR_EXCEPT

  def do_action(self, parser):
    super(ComplementClassState, self).do_action(parser)
    parser.end_class()

class To(RegexState):
  '''
  State in which the keyword "to" has been invoked, indicating the upper limit of a character range in a class
  '''
  def __init__(self):
    super(To, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_RANGE_ERROR_STATE

  def get_token_not_found_transition(self, token):
    if len(token) == 1 and token >= self.start_range:
      return self.CLASS_STATE
    else:
      return self.INVALID_CLASS_RANGE_ERROR_STATE

  def do_action(self, parser):
    #Get the start of the range from the current_fragment string
    self.start_range = parser.current_start_range

class OpenClassRange(RegexState):
  '''
  State in which a start of a character range has been indicated
  '''
  def __init__(self):
    super(OpenClassRange, self).__init__()
    self.transitions[self.TO_TOKEN] = self.TO
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_RANGE_ERROR_STATE

  def do_action(self, parser):
    parser.current_start_range = parser.current_token
    parser.current_fragment += re.escape(parser.current_token) + self.CLASS_RANGE_SYMBOL

  def get_token_not_found_transition(self, token):
    return self.INVALID_CLASS_RANGE_ERROR_STATE

class Except(RegexState):
  '''
  State after keyword "except" indicating a complement class
  '''
  def __init__(self):
    super(Except, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_ERROR_STATE

  def do_action(self, parser):
    parser.current_fragment = parser.OPEN_PARENTHESIS + self.OPEN_CLASS_SYMBOL + self.COMPLEMENT_CLASS_SYMBOL

  def get_token_not_found_transition(self, token):
    if token == '':
      return self.INCOMPLETE_CLASS_ERROR_STATE
    return self.COMPLEMENT_CLASS_STATE

class From(RegexState):
  '''
  State after keyword "from" has been invoked indicating a class containing a range between characters
  '''
  def __init__(self):
    super(From, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_RANGE_ERROR_STATE

  def get_token_not_found_transition(self, token):
    if len(token) == 1:
      return self.OPEN_CLASS_RANGE
    else:
      return self.INVALID_CLASS_RANGE_ERROR_STATE

  def do_action(self, parser):
    parser.current_fragment = parser.OPEN_PARENTHESIS + self.OPEN_CLASS_SYMBOL

class OpenClass(RegexState):
  '''
  State after keyword "of" has been invoked to indicate a class
  '''
  def __init__(self):
    super(OpenClass, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_CLASS_ERROR_STATE

  def do_action(self, parser):
    parser.current_fragment = parser.OPEN_PARENTHESIS + self.OPEN_CLASS_SYMBOL

  def get_token_not_found_transition(self, token):
    if token == '':
      return self.INCOMPLETE_CLASS_ERROR_STATE
    return self.CLASS_STATE

class AnyChar(ModifiablePotentiallyFinalRegexState):

  def __init__(self):
    super(AnyChar, self).__init__()
    self.transitions[self.OF_TOKEN] = self.OPEN_CLASS
    self.transitions[self.FROM_TOKEN] = self.FROM
    self.transitions[self.EXCEPT_TOKEN] = self.EXCEPT

  def do_action(self, parser):
    super(AnyChar, self).do_action(parser)
    parser.current_fragment = parser.OPEN_PARENTHESIS + self.ANY_CHAR_SYMBOL

class StartOfString(PotentiallyFinalRegexState):
  '''
  State in which the current fragment consists of the start of string symbol (^)
  '''
  def __init__(self):
    super(StartOfString, self).__init__()

  def do_action(self, parser):
    super(StartOfString, self).do_action(parser)
    parser.current_fragment = parser.OPEN_PARENTHESIS + self.START_OF_STRING_SYMBOL

class EndOfString(PotentiallyFinalRegexState):
  '''
  State in which the current fragment consists of the end of string symbol ($)
  '''
  def __init__(self):
    super(EndOfString, self).__init__()

  def do_action(self, parser):
    super(EndOfString, self).do_action(parser)
    parser.current_fragment = parser.OPEN_PARENTHESIS + self.END_OF_STRING_SYMBOL

class PlainText(ModifiablePotentiallyFinalRegexState):
  '''
  State in which the current fragment consists of plain text (no keyword)
  '''
  def __init__(self):
    super(PlainText, self).__init__()

  def do_action(self, parser):
    super(PlainText, self).do_action(parser)
    parser.process_current_token_as_plain_text()

class EndNestedExpression(ModifiablePotentiallyFinalRegexState):
  '''
  State after a nested expression
  '''
  def __init__(self):
    super(EndNestedExpression, self).__init__()

  def do_action(self, parser):
    super(EndNestedExpression, self).do_action(parser)
    parser.child.end()
    parser.current_fragment = parser.OPEN_PARENTHESIS + parser.child.ret_val

class NestedExpression(RegexState):
  '''
  State of being in a nested expression (inside square brackets)
  @param nested_level: the depth of the nesting
  @type nested_level: int
  '''
  def __init__(self, nested_level=0):
    super(NestedExpression, self).__init__()
    self.nested_level = nested_level

  def do_action(self, parser):
    parser.child.process_token(parser.current_token)

  def get_next(self, token):
    if token == self.END_OF_INPUT_TOKEN:
      return self.UNCLOSED_BRACKET_ERROR_STATE
    if token == self.NESTED_CLOSE_TOKEN and self.nested_level == 0:
      return self.END_NESTED_EXPRESSION
    elif token == self.NESTED_CLOSE_TOKEN and self.nested_level > 0:
      return self.NESTED_EXPRESSION_DOWN_LEVEL
    elif token == self.NESTED_OPEN_TOKEN:
      return self.NESTED_EXPRESSION_UP_LEVEL
    return self.NESTED_EXPRESSION

class NewNestedExpression(ModifiablePotentiallyFinalRegexState):
  '''
  State of starting an expression nested within current expression (after open square bracket)
  Note that this state can also transition into a typical expression, if the open square bracket is to be treated as regular plain text input (thus, modifiable)
  '''
  def __init__(self):
    super(NewNestedExpression, self).__init__()
    self.transitions[self.EXPRESSION_TOKEN] = self.NESTED_EXPRESSION
    self.transitions[self.NESTED_CLOSE_TOKEN] = self.END_NESTED_EXPRESSION
    self.transitions[self.END_OF_INPUT_TOKEN] = self.UNCLOSED_BRACKET_ERROR_STATE

  def do_action(self, parser):
    super(NewNestedExpression, self).do_action(parser)
    parser.process_current_token_as_plain_text()

  def get_token_not_found_transition(self, token):
    return self.NEW_NESTED_EXPRESSION_ERROR_STATE

class CheckColon(RegexState):
  def __init__(self):
    super(CheckColon, self).__init__()
    self.transitions[self.COLON_TOKEN] = self.START_EXPRESSION

  def get_token_not_found_transition(self, token):
    return self.COLON_ERROR_STATE

class NewExpression(RegexState):
  '''
  State at the very beginning of expression, or after a semi-colon
  @param after_or: whether this new expression is coming after an or (in which case it should only go to end_of_input)
  @type after_or: bool
  '''
  def __init__(self):
    super(NewExpression, self).__init__()
    self.transitions[self.END_OF_INPUT_TOKEN] = self.END_OF_EXPRESSIONS
    self.after_or = False

  def get_token_not_found_transition(self, token):
    if token == self.EXPRESSION_TOKEN and self.after_or:
      return self.MULTIPLE_OR_ERROR_STATE
    elif token == self.EXPRESSION_TOKEN:
      return self.CHECK_COLON
    return self.NEW_EXPRESSION_ERROR_STATE

  def do_action(self, parser):
    parser.n_expressions += 1
    parser.add_current_fragment()
    self.after_or = parser.after_or

class RegexStateFactory(object):
  '''
  Produces a state based on a string (hydrates them)
  '''
  STATE_DICTIONARY = { RegexState.NEW_EXPRESSION: NewExpression(),
                       RegexState.CHECK_COLON: CheckColon(),
                       RegexState.START_EXPRESSION: StartExpression(),
                       RegexState.ANY_CHAR: AnyChar(),
                       RegexState.END_OF_EXPRESSIONS: EndOfExpressions(),
                       RegexState.NEW_EXPRESSION_ERROR_STATE: NewExpressionErrorState(), 
                       RegexState.COLON_ERROR_STATE: ColonErrorState(),
                       RegexState.PLAIN_TEXT: PlainText(),
                       RegexState.CHECK_NUMBER_OF_TIMES: CheckNumberOfTimes(),
                       RegexState.INVALID_MODIFIER_STATE: InvalidModifierState(),
                       RegexState.BASE_ERROR_STATE: BaseErrorState(),
                       RegexState.ZERO_OR_MORE: ZeroOrMore(),
                       RegexState.INVALID_REPETITIONS_ERROR_STATE: InvalidRepetitionsErrorState(),
                       RegexState.SET_GREEDY: SetGreedy(),
                       RegexState.KEEP_GREEDY: KeepGreedy(),
                       RegexState.INCOMPLETE_EXPRESSION_ERROR_STATE: IncompleteExpressionErrorState(),
                       RegexState.ONE_OR_MORE: OneOrMore(),
                       RegexState.SET_NOT_GREEDY: SetNotGreedy(),
                       RegexState.KEEP_NOT_GREEDY: KeepNotGreedy(),
                       RegexState.ZERO_OR_ONE: ZeroOrOne(),
                       RegexState.M_REPETITIONS: MRepetitions(),
                       RegexState.UP_TO: UpTo(),
                       RegexState.INVALID_REPETITION_RANGE_ERROR_STATE: InvalidRepetitionRangeErrorState(),
                       RegexState.M_UP_TO_N_REPETITIONS: MUpToNRepetitions(),
                       RegexState.M_UP_TO_INFINITY_REPETITIONS: MUpToInfinityRepetitions(),
                       RegexState.END_NESTED_EXPRESSION: EndNestedExpression(),
                       RegexState.NESTED_EXPRESSION: NestedExpression(),
                       RegexState.NEW_NESTED_EXPRESSION: NewNestedExpression(),
                       RegexState.NEW_NESTED_EXPRESSION_ERROR_STATE: NewNestedExpressionErrorState(),
                       RegexState.OR: Or(),
                       RegexState.INCOMPLETE_OR_ERROR_STATE: IncompleteOrErrorState(),
                       RegexState.MULTIPLE_OR_ERROR_STATE: MultipleOrErrorState(),
                       RegexState.OPEN_CLASS: OpenClass(),
                       RegexState.CLASS_STATE: ClassState(),
                       RegexState.INCOMPLETE_CLASS_ERROR_STATE: IncompleteClassErrorState(),
                       RegexState.OR_OF: OrOf(),
                       RegexState.FROM: From(),
                       RegexState.INCOMPLETE_CLASS_RANGE_ERROR_STATE: IncompleteClassRangeErrorState(),
                       RegexState.INVALID_CLASS_RANGE_ERROR_STATE: InvalidClassRangeErrorState(),
                       RegexState.TO: To(),
                       RegexState.OPEN_CLASS_RANGE: OpenClassRange(),
                       RegexState.OR_FROM: OrFrom(),
                       RegexState.EXCEPT: Except(),
                       RegexState.OR_EXCEPT: OrExcept(),
                       RegexState.COMPLEMENT_CLASS_STATE: ComplementClassState(),
                       RegexState.START_OF_STRING: StartOfString(),
                       RegexState.END_OF_STRING: EndOfString()}

  @staticmethod
  def get_next_state(state, token):
     '''
     Hydrates the next state of a regex state
     @param state: the current state
     @type state: RegexState
     @param token: token to use as the key to the next transition
     @type token: string
     @return: the next state
     @rtype: RegexState
     '''
     if isinstance(state, NestedExpression):
       return RegexStateFactory.get_next_nested_state(state, token)
     return RegexStateFactory.STATE_DICTIONARY[state.get_next(token)]

  @staticmethod
  def get_next_nested_state(state, token):
     '''
     Hydrates the next state for recursive nested expression states
     @param state: the current state
     @type state: RegexState
     @param token: token to use as the key to the next transition
     @type token: string
     @return: the next state
     @rtype: RegexState
     '''
     if not isinstance(state, NestedExpression):
       return BaseErrorState()

     next_key = state.get_next(token)
     if next_key == RegexState.UNCLOSED_BRACKET_ERROR_STATE:
       return UnclosedBracketErrorState()
     if next_key == RegexState.END_NESTED_EXPRESSION:
       return EndNestedExpression()
     elif next_key == RegexState.NESTED_EXPRESSION_DOWN_LEVEL:
       return NestedExpression(state.nested_level-1)
     elif next_key == RegexState.NESTED_EXPRESSION_UP_LEVEL:
       return NestedExpression(state.nested_level+1)
     return NestedExpression(state.nested_level)
