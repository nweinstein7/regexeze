import argparse

class RegexezeSubparser(object):
  '''
  Parent class for any regexeze subparser
  '''
  TRANSLATE = 'translate'
  TRANSLATE_DESCRIPTION = 'Translate from regexeze to standard Python regex. If no pattern or file is supplied, takes pattern from stdin.'
  MATCH = 'match'
  MATCH_DESCRIPTION = 'Matches a target string to a pattern. If pattern is supplied, matches pattern. If file is supplied, matches pattern inside file. Otherwise, matches from stdin.'
  MATCH_TARGET_STRING_DESCRIPTION = 'A string for matching.'

  def __init__(self, title = '', description = ''):
    self.title = title
    self.description = description
    self.help = description
    self.cmd = title
    self.parser = argparse.ArgumentParser()

  def setup(self):
    '''
    Sets up this subparser after being added to group of subparsers
    '''
    self.add_pattern_and_file_support()
    self.parser.set_defaults(cmd=self.cmd)

  def add_pattern_and_file_support(self):
    '''
    Adds support for taking a pattern from a string and taking a pattern from a file
    '''
    inputMechanismGroup = self.parser.add_mutually_exclusive_group()
    inputMechanismGroup.add_argument('-p', '--pattern', dest='pattern', type=str, help='A pattern in regexeze.')
    inputMechanismGroup.add_argument('-f', '--filename', dest='filename', type=str, help='A file (or path to file) containing a regexeze expression.')

class TargetStringSubparser(RegexezeSubparser):
  '''
  Parent class for regexeze subparsers that require a target string
  '''
  def __init__(self, title = '', description = '', target_string_help = ''):
    super(TargetStringSubparser, self).__init__(title, description)
    self.target_string_help = target_string_help

  def setup(self):
    super(TargetStringSubparser, self).setup()
    self.set_target_string()

  def set_target_string(self):
    targetStringGroup = self.parser.add_argument_group()
    targetStringGroup.add_argument('-t', '--target-string', dest='target_string', type=str, help=self.target_string_help, required=True)

class RegexezeArgparser(object):
  '''
  Main argument parser for the regexeze command line tool
  '''
  DESCRIPTION = 'Parses a regular expression in regexeze. If no input string or file is supplied, parses from command line.'

  def __init__(self):
    self.parser = argparse.ArgumentParser(description=self.DESCRIPTION)
    self.subparsers = self.parser.add_subparsers(title="Commands")
    self.add_custom_subparsers()

  def parse_args(self):
    return self.parser.parse_args()

  def add_regexeze_subparser(self, subparser):
    '''
    Adds a subparser
    @param subparser: the subparser to be added
    @type subparser: RegexezeSubparser
    '''
    subparser.parser = self.subparsers.add_parser(subparser.title, description=subparser.description, help=subparser.help)
    subparser.setup()

  def add_custom_subparsers(self):
    '''
    Adds all special subparsers needed for command line tool
    '''
    #translate parser
    translateParser = RegexezeSubparser(RegexezeSubparser.TRANSLATE, RegexezeSubparser.TRANSLATE_DESCRIPTION)
    self.add_regexeze_subparser(translateParser)

    #match parser
    matchParser = TargetStringSubparser(RegexezeSubparser.MATCH, RegexezeSubparser.MATCH_DESCRIPTION, RegexezeSubparser.MATCH_TARGET_STRING_DESCRIPTION)
    self.add_regexeze_subparser(matchParser)
