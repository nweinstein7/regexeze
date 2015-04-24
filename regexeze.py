import shlex
import regexeze_states
import sys
import re
import argparse

class RegexParserMachine(object):
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
  @type child: RegexParserMachine
  @param after_or: whether the parser has hit an or (in which case it should proceed to another expression after semicolon, because that would be confusing)
  @type after_or: bool
  @param current_start_range: for character ranges, must know the start range in order to determine the order
  @type current_start_range: char
  @param n_expressions: number of complete expressions so far (necessary for determining whether or can occur)
  @type n_expressions: int
  @param m_repetitions: the lower bound of the repetition interval indicated
  @type m_repetitions: int
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

  def add_or(self):
    self.ret_val += self.OR_SYMBOL

  def process_current_token_as_plain_text(self):
    '''
    Sets the current fragment to an open parenthesis followed by the current token
    '''
    self.current_fragment = self.OPEN_PARENTHESIS + re.escape(self.current_token)

def main(input_string=None, filename=None):
  '''
  Main method for the program
  @param input_string: a string to be parsed
  @type input_string: str
  @param filename: name of file to be parsed
  @type filename: str
  '''
  my_rpm = RegexParserMachine('')
  if input_string:
    my_rpm = RegexParserMachine(input_string);
    my_rpm.parse()
  elif filename:
    my_rpm.parse(filename)
  else:
    my_rpm.parse(sys.stdin)
  print my_rpm.ret_val

if __name__ == '__main__':
  argparser = argparse.ArgumentParser(description='Parses a regular expression in regexeze. If no input string or file is supplied, parses from command line.')
  group = argparser.add_mutually_exclusive_group()
  group.add_argument('-i', '--input-string', dest='input_string', type=str, help='A string of input')
  group.add_argument('-f', '--filename', dest='filename', type=str, help='A file (or path to file) containing a regex')

  args = argparser.parse_args()
  main(args.input_string, args.filename)
