import regex_errors

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

  ZERO_OR_MORE_SYMBOL = '*'
  ZERO_OR_ONE_SYMBOL = '?'
  NOT_GREEDY_SYMBOL = '?'
  ANY_CHAR_SYMBOL = '.'
  ONE_OR_MORE_SYMBOL = '+'
  END_OF_EXPRESSION_SYMBOL = ';'
  M_REPETITIONS_FORMAT = '{{{0}}}'

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
  Generic parent state for any state which could theoretically be followed by a comma (new expression) or end of input
  '''
  def __init__(self):
    super(PotentiallyFinalRegexState, self).__init__()
    self.transitions[self.END_OF_EXPRESSION_SYMBOL] = self.NEW_EXPRESSION
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_EXPRESSION_ERROR_STATE

  def get_token_not_found_transition(self, token):
    return self.INVALID_MODIFIER_STATE

class BaseErrorState(RegexState):
  '''
  State for generic errors (placeholder - ideally, every eventuality will have a specific error)
  '''
  def do_action(self, parser):
    raise regex_errors.Error(parser)

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
    parser.current_modifier = self.symbol

class EndOfExpressions(RegexState):
  def __init__(self):
    pass

class NewExpressionErrorState(RegexState):
  def do_action(self, parser):
    raise regex_errors.NewExpressionError(parser)

class IncompleteExpressionErrorState(RegexState):
  def do_action(self, parser):
    raise regex_errors.IncompleteExpressionError(parser)

class ColonErrorState(RegexState):
  def do_action(self, parser):
    raise regex_errors.ColonError(parser)

class InvalidModifierState(RegexState):
  def do_action(self, parser):
    raise regex_errors.InvalidModifierError(parser)

class InvalidRepetitionsErrorState(RegexState):
  def do_action(self, parser):
    raise regex_errors.InvalidRepetitionsError(parser)

class InvalidRepetitionRangeErrorState(RegexState):
  def do_action(self, parser):
    raise regex_errors.InvalidRepetitionRangeError(parser)

class SetGreedy(PotentiallyFinalRegexState):
  '''
  Tells the number of repetitions to be greedy
  '''
  def __init__(self):
    super(SetGreedy, self).__init__()

  def do_action(self, parser):
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
    parser.current_modifier = parser.current_modifier + self.NOT_GREEDY_SYMBOL

class KeepNotGreedy(PotentiallyFinalRegexState):
  '''
  Keeps the number of repetitions not to greedy when that is default
  '''
  def __init__(self):
    super(KeepNotGreedy, self).__init__()

class ZeroOrMore(NotGreedyNumberOfRepetitionsState):
  '''
  State in which zero_or_more repetitions have been selected
  '''
  def __init__(self):
    super(ZeroOrMore, self).__init__()
    self.symbol = self.ZERO_OR_MORE_SYMBOL

class OneOrMore(NotGreedyNumberOfRepetitionsState):
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

  def do_action(self, parser):
    parser.current_modifier = parser.current_modifier[1:-1]

class MUpToNRepetitions(GreedyNumberOfRepetitionsState):
  '''
  State in which between m and n repetitions have been selected
  '''
  def __init__(self):
    super(MUpToNRepetitions, self).__init__()

  def do_action(self, parser):
    self.symbol = parser.current_modifier + "," + parser.current_token
    parser.current_modifier = self.M_REPETITIONS_FORMAT.format(self.symbol)

class MUpToInfinityRepetitions(GreedyNumberOfRepetitionsState):
  '''
  State in which between m and infinite repetitions have been selected
  '''
  def __init__(self):
    super(MUpToInfinityRepetitions, self).__init__()

  def do_action(self, parser):
    self.symbol = parser.current_modifier + ","
    parser.current_modifier = self.M_REPETITIONS_FORMAT.format(self.symbol)

class MRepetitions(GreedyNumberOfRepetitionsState):
  '''
  State in which m repetitions have been selected
  '''
  def __init__(self):
    super(MRepetitions, self).__init__()
    self.transitions[self.UP_TO_TOKEN] = self.UP_TO

  def do_action(self, parser):
    parser.current_modifier = self.M_REPETITIONS_FORMAT.format(parser.current_token)

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

class AnyChar(PotentiallyFinalRegexState):

  def __init__(self):
    super(AnyChar, self).__init__()
    self.transitions['for'] = self.CHECK_NUMBER_OF_TIMES

  def do_action(self, parser):
    parser.current_fragment = parser.OPEN_PARENTHESIS + self.ANY_CHAR_SYMBOL

class PlainText(PotentiallyFinalRegexState):
  '''
  State in which the current fragment consists of plain text (no keyword)
  '''
  def __init__(self):
    super(PlainText, self).__init__()
    self.transitions['for'] = self.CHECK_NUMBER_OF_TIMES

  def do_action(self, parser):
    parser.current_fragment = parser.OPEN_PARENTHESIS + parser.current_token

class StartExpression(RegexState):
  def __init__(self):
    super(StartExpression, self).__init__()
    self.transitions[self.ANY_CHAR_TOKEN] = self.ANY_CHAR
    self.transitions[self.END_OF_INPUT_TOKEN] = self.INCOMPLETE_EXPRESSION_ERROR_STATE

  def get_token_not_found_transition(self, token):
    return self.PLAIN_TEXT

class CheckColon(RegexState):
  def __init__(self):
    super(CheckColon, self).__init__()
    self.transitions[':'] = self.START_EXPRESSION

  def get_token_not_found_transition(self, token):
    return self.COLON_ERROR_STATE

class NewExpression(RegexState):
  def __init__(self):
    super(NewExpression, self).__init__()
    self.transitions[self.EXPRESSION_TOKEN] = self.CHECK_COLON
    self.transitions[self.END_OF_INPUT_TOKEN] = self.END_OF_EXPRESSIONS

  def get_token_not_found_transition(self, token):
    return self.NEW_EXPRESSION_ERROR_STATE

  def do_action(self, parser):
    parser.add_current_fragment()

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
                       RegexState.M_UP_TO_INFINITY_REPETITIONS: MUpToInfinityRepetitions()}

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
     return RegexStateFactory.STATE_DICTIONARY[state.get_next(token)]

