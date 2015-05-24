import shlex
import regexeze_states
import sys
import re
import regexeze_argparser

class RegexezeObject(object):
  '''
  A deterministic finite state machine for validating and parsing regex language
  @param state: the state of the machine
  @type state: regexeze_states.RegexState
  @param arg_string: the input to the regex parser - should be in proper syntax
  @type arg_string: string
  @param current_fragment: the current expr fragment being created
  @type current_fragment: string
  @param current_modifier: the current modifier being added to the expr
  @type current_modifier: string
  @param current_modifier_fragment: for multipart modifiers, the current piece of modifier being stored
  @type current_modifier_fragment: string
  @param ret_val: the full regex to be returned
  @type ret_val: string
  @param approximate_location: the approximate position through the arg_string (simply for error reporting, showing where in the string the error is)
  @type approximate_location: int
  @param child: the child machine used to parse nested expressions
  @type child: RegexezeObject
  @param after_or: whether the parser has hit an or (in which case it should proceed to another expression after semicolon, because that would be confusing)
  @type after_or: bool
  @param current_start_range: for character ranges, must know the start range in order to determine the order
  @type current_start_range: char
  @param n_expressions: number of complete expressions so far (necessary for determining whether or can occur)
  @type n_expressions: int
  @param m_repetitions: the lower bound of the repetition interval indicated
  @type m_repetitions: int
  @param namespace: the official namespace of groups defined
  @type namespace: dict string -> string
  '''
  END_OF_INPUT = 'end_of_input'
  OPEN_PARENTHESIS = '('
  CLOSE_PARENTHESIS = ')'
  OR_SYMBOL = '|'
  CLOSE_CLASS_SYMBOL = ']'

  def __init__(self, arg_string=""):
    self.state = regexeze_states.NewExpression()
    self.arg_string = arg_string
    self.current_fragment = ""
    self.current_modifier = ""
    self.current_modifier_fragment = ""
    self.ret_val = ""
    self.approximate_location = 0
    self.recursive_stack = []
    self.tokenize(self.arg_string)
    self.child = None
    self.after_or = False
    self.n_expressions = 0
    self.current_start_range = ""
    self.m_repetitions = 0
    self.namespace = {}

  def parse(self, source=""):
   '''
   Parses input according to regex syntax
   If arg_string is empty and source is stdin, parses from command line stdin
   If arg_string is empty and source is filename, parses from filename
   '''
   #stdin
   if source == sys.stdin:
     for line in sys.stdin:
       self.arg_string += line
       self.tokenize(line)
       for token in self.tokenizer:
         self.process_token(token)
     self.end()
   #file
   elif source != "":
     with open(source) as input_file:
       for line in input_file:
         self.arg_string += line
         self.tokenize(line)
         for token in self.tokenizer:
           self.process_token(token)
     self.end()
   #arg string
   else:
     for token in self.tokenizer:
       self.process_token(token)
     self.end()

  def tokenize(self, input):
    self.tokenizer = shlex.shlex(input, posix=True)

  def process_token(self, token):
    self.current_token = token
    self.state = regexeze_states.RegexStateFactory.get_next_state(self.state, token)
    self.state.do_action(self)
    if token != self.END_OF_INPUT:
      self.approximate_location += len(token)

  def end(self):
    self.process_token(self.END_OF_INPUT)

  def add_current_fragment(self):
    self.ret_val += self.current_fragment + self.CLOSE_PARENTHESIS + self.current_modifier
    self.current_fragment = ''
    self.current_modifier = ''
    self.OPEN_PARENTHESIS = '('

  def add_or(self):
    self.ret_val += self.OR_SYMBOL

  def process_current_token_as_plain_text(self):
    '''
    Sets the current fragment to an open parenthesis followed by the current token
    '''
    self.current_fragment = self.OPEN_PARENTHESIS + re.escape(self.current_token)

#wrapper methods that produce same functionality as python re module, only with regexeze syntax
def compile(pattern="", source=""):
  '''
  Compile a regexeze expression into a regexeze object
  @param pattern: the pattern, in regexeze syntax, to be compiled
  @type pattern: str
  @return: the compiled regexeze object
  @rtype: RegexezeObject
  @param source: the source of the pattern - filename, stdin, or blank meaning the pattern string
  @type source: str
  '''
  regexezeObject = RegexezeObject(pattern)
  regexezeObject.parse(source)
  return regexezeObject

def translate(pattern="", source=""):
  '''
  Translate a pattern from regexeze to standard Python re syntax
  @param pattern: the pattern, in regexeze syntax, to be compiled
  @type pattern: str
  @param source: the source of the pattern - filename, stdin, or blank meaning the pattern string
  @type source: str
  @return: the regexeze pattern in standard Python syntax
  @rtype: str
  '''
  return compile(pattern, source).ret_val

def search(pattern="", target_string="", source=""):
  '''
  Search a string for the pattern
  @param pattern: the pattern, in regexeze syntax, to use for searching
  @type pattern: str
  @param target_string: the string to be searched
  @type target_string: str
  @return: the match object resulting from the search
  @rtype: re.MatchObject
  @param source: the source of the pattern - filename, stdin, or blank meaning the pattern string
  @type source: str
  '''
  regexezeObject = compile(pattern, source)
  return re.search(regexezeObject.ret_val, target_string)

def match(pattern="", target_string="", source=""):
  '''
  Match a string to the regexeze expression pattern
  @param pattern: the pattern, in regexeze syntax, to use for matching
  @type pattern: str
  @param target_string: the string to be matched
  @type target_string: str
  @return: the match object resulting from the match
  @rtype: re.MatchObject
  @param source: the source of the pattern - filename, stdin, or blank meaning the pattern string
  @type source: str
  '''
  regexezeObject = compile(pattern, source)
  return re.match(regexezeObject.ret_val, target_string)

def translateMain(args):
  '''
  Method called when user selects translate mode when running from command line
  @param args: the arguments accepted
  @type args: argparse namespace
  '''
  pattern = args.pattern
  filename = args.filename

  regexezeObject = RegexezeObject('')
  if pattern:
    regexezeObject = RegexezeObject(pattern);
    regexezeObject.parse()
  elif filename:
    regexezeObject.parse(filename)
  else:
    regexezeObject.parse(sys.stdin)
  print regexezeObject.ret_val

def matchMain(args):
  '''
  Method called when user selects match mode when running from command line
  @param args: the arguments accepted
  @type args: argparse Namespace
  '''
  pattern = args.pattern
  filename = args.filename
  target_string = args.target_string
  matchObject = None
  if pattern:
    matchObject = match(pattern, target_string)
  elif filename:
    matchObject = match("", target_string, filename)
  else:
    matchObject = match("", target_string, sys.stdin)
  if matchObject:
    print "Match successful\n"
    print "All groups:"
    print "\tFull match: {0}".format(matchObject.group(0))
    for n, group in enumerate(matchObject.groups(), start=1):
      print "\tGroup {0}: {1}".format(n, group)
      n+=1
    print "\nNamed groups:"
    for groupName in matchObject.groupdict().keys():
      print "\t{0}: {1}".format(groupName, matchObject.groupdict()[groupName])
  else:
    print "No match"

#function map from sub parsers to functions
FUNCTION_MAP = { 'translate' : translateMain,
                 'match' : matchMain }
def main(args):
  '''
  Main method for the module
  @param args: the arguments accepted
  @type args: argparse namespace
  '''
  FUNCTION_MAP[args.cmd](args)

if __name__ == '__main__':
  argparser = regexeze_argparser.RegexezeArgparser()

  args = argparser.parse_args()
  main(args)
