import shlex
import regex_states
import sys

class Storage(object):
  value = ''
  
  def setValue(self, value):
    self.value = value
    return value

class RegexParserMachine(object):
  '''
  A deterministic finite state machine for validating and parsing regex language
  @param state: the state of the machine
  @type state: regex_states.RegexState
  @param arg_string: the input to the regex parser - should be in proper syntax
  @type arg_string: string
  @param current_fragment: the current expr fragment being created
  @type current_fragment: string
  @param ret_val: the full regex to be returned
  @type ret_val: string
  @param approximate_location: the approximate position through the arg_string (simply for error reporting, showing where in the string the error is)
  @type approximate_location: int
  '''
  END_OF_INPUT = 'end_of_input'
  OPEN_PARENTHESIS = '('
  CLOSE_PARENTHESIS = ')'

  def __init__(self, arg_string=""):
    self.state = regex_states.NewExpression()
    self.arg_string = arg_string
    self.current_fragment = ""
    self.current_modifier = ""
    self.ret_val = ""
    self.approximate_location = 0
    self.recursive_stack = []
    self.tokenize(self.arg_string)

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

  def parse_stdin(self):
    pass

  def process_token(self, token):
    self.current_token = token
    self.state = regex_states.RegexStateFactory.get_next_state(self.state, token)
    self.state.do_action(self)
    if token != self.END_OF_INPUT:
      self.approximate_location += len(token)

  def end(self):
    self.process_token(self.END_OF_INPUT)

  def add_current_fragment(self):
    self.ret_val += self.current_fragment + self.CLOSE_PARENTHESIS + self.current_modifier
    self.current_fragment = ''
    self.current_modifier = ''

if __name__ == '__main__':
  my_rgpm = RegexParserMachine('')
  for line in sys.stdin:
    
    my_rgpm.parse()
  print my_rgpm.ret_val
