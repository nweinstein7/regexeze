import unittest
import regex_errors
import regex_states
import regex_interface
import sys

class test_regex_parser_machine(unittest.TestCase):
  def setUp(self):
    self.rpm = regex_interface.RegexParserMachine('')
    self.TEST_FILE_NAME = "test_files/test_file.txt"
    self.EMPTY_FILE_NAME = "test_files/empty_file.txt"
    self.TEST_ERROR_FILE_NAME = "test_files/test_error_file.txt"

  def test_init(self):
    '''
    Test the init function to make sure the parser machine has all correct initial variables
    '''
    self.assertTrue(isinstance(self.rpm.state, regex_states.NewExpression))
    self.assertEquals(self.rpm.arg_string, '', 'arg_string should start empty')
    self.assertEquals(self.rpm.ret_val, '', 'ret_val should start empty')
    self.assertEquals(self.rpm.current_fragment, '', 'current_fragment should start empty')
    self.assertEquals(self.rpm.approximate_location, 0, 'approximate location should start at 0')

  def test_parse(self):
    '''
    Test the parser for correct and incorrect entries
    '''
    #TEST IO
    #Test simple expression from file
    self.rpm = regex_interface.RegexParserMachine('')
    self.rpm.parse(self.TEST_FILE_NAME)
    self.assertEquals(self.rpm.ret_val, '(hello){10}(how are you)', 'Should be able to parse a simple multiline file')

    #Test empty file
    self.rpm = regex_interface.RegexParserMachine('')
    self.rpm.parse(self.EMPTY_FILE_NAME)
    self.assertEquals(self.rpm.ret_val, '', 'Empty file empty string')

    #Test errors in file reading
    self.rpm = regex_interface.RegexParserMachine('')
    self.assertRaises(regex_errors.IncompleteExpressionError, self.rpm.parse, "test_files/test_error_file.txt")
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #Test simple expression in stdin
    self.rpm = regex_interface.RegexParserMachine('')
    with open(self.TEST_FILE_NAME, 'r') as sys.stdin:
      self.rpm.parse(sys.stdin)
    self.assertEquals(self.rpm.ret_val, '(hello){10}(how are you)', 'Should be able to parse a simple multiline expression from stdin')

    #Test empty stdin
    self.rpm = regex_interface.RegexParserMachine('')
    with open(self.EMPTY_FILE_NAME, 'r') as sys.stdin:
      self.rpm.parse(sys.stdin)
    self.assertEquals(self.rpm.ret_val, '', 'Should be able to parse a simple multiline expression from stdin')

    #Test error from stdin
    self.rpm = regex_interface.RegexParserMachine('')
    with open(self.TEST_ERROR_FILE_NAME, 'r') as sys.stdin:
      self.assertRaises(regex_errors.IncompleteExpressionError, self.rpm.parse, sys.stdin)
      self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteExpressionErrorState),                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #TEST NEW EXPRESSION ERRORS
    #test expression that is completely empty
    self.rpm = regex_interface.RegexParserMachine('')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '', 'Empty expression should result in empty string')

    #test expression that starts with incorrectly capitalized keyword
    self.rpm = regex_interface.RegexParserMachine('eXPr: any_char')
    self.assertRaises(regex_errors.NewExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.NewExpressionErrorState),
                    'After incorrect keyword at new expression, should end up in NewExpressionErrorState')

    #test expression that starts with otherwise wrong keyword
    self.rpm = regex_interface.RegexParserMachine('asf: any_char;')
    self.assertRaises(regex_errors.NewExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.NewExpressionErrorState),
                    'After incorrect keyword at new expression, should end up in NewExpressionErrorState')

    #test incorrect expression after a first correct expression
    self.rpm = regex_interface.RegexParserMachine('expr: a; asf')
    self.assertRaises(regex_errors.NewExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.NewExpressionErrorState),
                    'After incorrect start of second expression, should end up in NewExpressionErrorState')
    
    #TEST MISSING COLON
    self.rpm = regex_interface.RegexParserMachine('expr any_char;')
    self.assertRaises(regex_errors.ColonError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.ColonErrorState),
                    'After missing colon, should end up in ColonErrorState')

    #TEST SIMPLE EXPRESSIONS
    #Test incomplete expressions (empty)
    self.rpm = regex_interface.RegexParserMachine('expr: ')
    self.assertRaises(regex_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #Test incomplete expressions (no semi-colon)
    self.rpm = regex_interface.RegexParserMachine('expr: "a"')
    self.assertRaises(regex_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteExpressionErrorState),
                    'When expression has no semicolon, should end up in IncompleteExpressionErrorState')

    #Test a simple, single letter expression
    self.rpm = regex_interface.RegexParserMachine('expr: a;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)', 'Simple text expression should result in that simple text in a group')

    #Test two simple expressions in a row
    self.rpm = regex_interface.RegexParserMachine('expr: a; expr: a;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)(a)', 'Two simple text expressions in a row should result in the two being concatenated')

    #Test complete empty expression
    self.rpm = regex_interface.RegexParserMachine('expr: "";')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '()', 'Complete empty expression should simply result in an empty group')

    #Test complete empty expression followed by normal expression
    self.rpm = regex_interface.RegexParserMachine('expr: ""; expr: a;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '()(a)', 'Empty expression followed by normal expression should result in empty group followed by the normal expression in a group')

    #Test any_char syntax
    self.rpm = regex_interface.RegexParserMachine('expr: any_char;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)', 'The any_char keyword (unmodified) should result in a period in a group')

    #TEST MODIFIERS
    #Test invalid modifier
    self.rpm = regex_interface.RegexParserMachine('expr: any_char asdfha')
    self.assertRaises(regex_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.InvalidModifierState), 'After an invalid modifier, should end up in InvalidModifierState')

    #Test invalid repetitions
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for asdfasdf')
    self.assertRaises(regex_errors.InvalidRepetitionsError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.InvalidRepetitionsErrorState), 'After an invalid number of repetitions specified, should end up in InvalidRepetitionsErrorState')

    #Test valid modifier missing semicolon
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for zero_or_more')
    self.assertRaises(regex_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteExpressionErrorState), 'Expression with modifier must end in semicolon')

    #Test zero_or_more_modifier - default not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for zero_or_more;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)*?', 'The any_char keyword modified zero_or_more should result in a period in a group followed by asterisk and question mark (defaults to not greedy)')

    #Test zero_or_more modifier with incorrect greedy/not-greedy modifier
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for zero_or_more afsadf;')
    self.assertRaises(regex_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.InvalidModifierState), 'After an invalid greedy/not-greedy modifier, should end up in InvalidModifierState')

    #Test zero_or_more modifier with greedy
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for zero_or_more greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)*', 'The any_char keyword modified zero_or_more greedy should result in a period in a group followed by asterisk')

    #Test zero_or_more modifier with greedy in two consecutive expressions
    self.rpm = regex_interface.RegexParserMachine('''expr: "a" for zero_or_more greedy; expr: "hello" for zero_or_more greedy;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)*(hello)*', 'The any_char keyword modified zero_or_more greedy should result in a period in a group followed by asterisk')

    #Test one_or_more_modifier - default not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for one_or_more;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)+?', 'The any_char keyword modified one_or_more should result in a period in a group followed by plus and question mark (defaults to not greedy)')

    #Test one_or_more modifier with greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for one_or_more greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)+', 'Expression modified one_or_more greedy should result in the expression in a group followed by plus')

    #Test zero_or_one modifier - default greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for zero_or_one;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)?', 'Expression modified zero_or_one should result in the expression in a group followed by question mark')

    #Test zero_or_one modifier - not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for zero_or_one not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)??', 'Expression modified zero_or_one not_greedy should result in the expression in a group followed by two question marks')

    #Test zero_or_one modifier - missing semicolon
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for zero_or_one not_greedy')
    self.assertRaises(regex_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteExpressionErrorState), 'Expression with greedy must end in semicolon')

    #Test zero_or_one modifier with superfluous *greedy* modifier
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for zero_or_one greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)?', 'Expression modified zero_or_one greedy should result in the expression in a group followed by a question mark')

    #Test one_or_more modifier with superfluous *not_greedy* modifier
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for one_or_more not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)+?', 'Expression modified zero_or_one not_greedy should result in the expression in a group followed by a plus and a question mark')

    #Test m repetitions modifier
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}', 'Expression modified by 1 should result in the expression in a group followed by 1 in brackets')

    #Test m repetitions modifier superfluous greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}', 'Expression modified by 1 greedy should result in the expression in a group followed by 1 in brackets')

    #Test m repetitions modifier superfluous not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}?', 'Expression modified by 1 not_greedy should result in the expression in a group followed by 1 in brackets followed by question mark')

    #Test m repetitions modifier followed by up_to then end of expression
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 up_to;')
    self.assertRaises(regex_errors.InvalidRepetitionRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer')

    #Test m repetitions modifier followed by up_to then non integer
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 up_to asdfasdf;')
    self.assertRaises(regex_errors.InvalidRepetitionRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer')

    #Test m up_to n repetitions
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 up_to 2;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}', 'Expression modified by 1 up_to 2 should result in the expression in a group followed by 1,2 in brackets')

    #Test m up_to n repetitions greedy (default - no change from above)
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 up_to 2 greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}', 'Expression modified by 1 up_to 2 greedy should result in the expression in a group followed by 1,2 in brackets')

    #Test m up_to n repetitions not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 up_to 2 not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}?', 'Expression modified by 1 up_to 2 not_greedy should result in the expression in a group followed by 1,2 in brackets followed by question mark')

    #Test m up_to infinity repetitions
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 10 up_to infinity;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){10,}', 'Expression modified by 1 up_to infinity should result in the expression in a group followed by 1, in brackets')


if __name__ == '__main__':
    unittest.main()
