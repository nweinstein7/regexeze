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

    #Test zero_or_more_modifier - default greedy
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for zero_or_more;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)*', 'Should be able to parse simple zero or one (*) modifier')

    #Test zero_or_more modifier with incorrect greedy/not-greedy modifier
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for zero_or_more afsadf;')
    self.assertRaises(regex_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.InvalidModifierState), 'After an invalid greedy/not-greedy modifier, should end up in InvalidModifierState')

    #Test zero_or_more modifier - not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for zero_or_more not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)*?', 'Should be able to parse a not greedy zero_or_more (*) modifier')

    #Test two consecutive modified expressions
    self.rpm = regex_interface.RegexParserMachine('''expr: "a" for zero_or_more greedy; expr: "hello" for zero_or_more greedy;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)*(hello)*', 'Should be able to parse two consecutive modified statements')

    #Test one_or_more_modifier - default greedy
    self.rpm = regex_interface.RegexParserMachine('expr: any_char for one_or_more;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)+', 'Should be able to parse the one_or_more (+) modifier')

    #Test one_or_more modifier with not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for one_or_more not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)+?', 'Should be able to parse one_or_more_modifier not greedy')

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
    self.assertEquals(self.rpm.ret_val, '(a)?', 'Should be able to supply greedy/not_greedy regardless of the default greediness')

    #Test one_or_more modifier with superfluous *greedy* modifier
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for one_or_more greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)+', 'Should be able to supply greedy/not_greedy regardless of the default greediness')

    #Test m repetitions modifier
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}', 'Should be able to parse simple m repetitions modifier')

    #Test m repetitions modifier superfluous greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}', 'Should be able to supply greedy/not_greedy regardless of default')

    #Test m repetitions modifier not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}?', 'Should be able to parse m repetitions not greedy')

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
    self.assertEquals(self.rpm.ret_val, '(a){1,2}', 'Should be able to parse m up_to n repetitions')

    #Test m up_to n repetitions greedy (default - no change from above)
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 up_to 2 greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}', 'Should be able to parse m up_to n repetitions specifying greedy')

    #Test m up_to n repetitions not greedy
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 1 up_to 2 not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}?', 'Should be able to parse m up_to n reptitions not greedy')

    #Test m up_to infinity repetitions
    self.rpm = regex_interface.RegexParserMachine('expr: "a" for 10 up_to infinity;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){10,}', 'Should be able to parse number range of reptitions, where the upper bound is unlimited (infinity keyword)')

    #TEST NESTING
    #Simple nesting (1 layer)
    self.rpm = regex_interface.RegexParserMachine('''expr: [expr: 'a';];''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '((a))', 'Simple nested expression should end up with expression inside two sets of parentheses')

    #Complex nesting (2 layer)
    self.rpm = regex_interface.RegexParserMachine('''expr: [expr: [expr: 'abc' for zero_or_more greedy;]; expr: 'hello';] for 1;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(((abc)*)(hello)){1}', 'Complex nested expressions should be parsed correctly')

    #Ending before brackets are closed
    self.rpm = regex_interface.RegexParserMachine('''expr: [expr: 'a';''')
    self.assertRaises(regex_errors.UnclosedBracketError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.UnclosedBracketErrorState), 'Expression cannot end in the middle of a nested expression')

    #Using an open square bracket ([) as an expression
    self.rpm = regex_interface.RegexParserMachine('''expr: [ for zero_or_one;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([)?', 'Should still be able to use [ as an expression')

    #TEST OR
    #Simple or expression
    self.rpm = regex_interface.RegexParserMachine('''expr: 'a' or 'b';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)|(b)', 'Should be able to parse a simple or statement')

    #Or with modifiers
    self.rpm = regex_interface.RegexParserMachine('''expr: 'a' for zero_or_one greedy or 'b' for one_or_more;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)?|(b)+', 'Should be able to parse or with modifiers')

    #Or with nested components
    self.rpm = regex_interface.RegexParserMachine('''expr: [expr: 'a' for zero_or_one greedy;] or [ expr: 'b' for one_or_more;];''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '((a)?)|((b)+)', 'Should be able to parse or between two nested expressions')

    #Or fully nested
    self.rpm = regex_interface.RegexParserMachine('''expr: [expr: 'a' for zero_or_one greedy or 'b' for one_or_more;];''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '((a)?|(b)+)', 'Should be able to limit the reach of or by grouping it using a nested expression')

    #Or invalid syntax - using expr: after or
    self.rpm = regex_interface.RegexParserMachine('''expr: [expr: 'a' for zero_or_one greedy or expr: 'b' for one_or_more;];''')
    self.assertRaises(regex_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.child.state, regex_states.InvalidModifierState), 'Using expr after or is treated as an invalid modifier state, because it thinks "expr:" is the input and "b" is the modifier.')

    #Incomplete or
    self.rpm = regex_interface.RegexParserMachine('''expr: 'a' for zero_or_one greedy or''')
    self.assertRaises(regex_errors.IncompleteOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteOrErrorState), 'If the expression ends on an or, should result in an incomplete or error.')

    #Expression after or
    self.rpm = regex_interface.RegexParserMachine('''expr: 'a' or 'b'; expr: 'c';''')
    self.assertRaises(regex_errors.ExpressionAfterOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.ExpressionAfterOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    #Multiple ors in a row
    self.rpm = regex_interface.RegexParserMachine('''expr: 'a' or 'b' or 'c' or 'd';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)|(b)|(c)|(d)', 'Should be able to have any number of ors in a row')

    #TEST CLASSES
    #Test simple class
    self.rpm = regex_interface.RegexParserMachine('''expr: any_char of 'abc';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([abc])', 'Should be able to parse a simple class expression.')

    #Test incomplete class statement
    self.rpm = regex_interface.RegexParserMachine('''expr: any_char of''')
    self.assertRaises(regex_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteClassErrorState), 'End of input directly after keyword of should result in error.')

    #Test empty class statement
    self.rpm = regex_interface.RegexParserMachine('''expr: any_char of ""''')
    self.assertRaises(regex_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteClassErrorState), 'Empty input to character class should result in an error..')

    #Test or_of with classes
    self.rpm = regex_interface.RegexParserMachine('''expr: any_char of 'abc' or_of 'def' or_of 'ghi';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([abcdefghi])', 'Should be able to parse complex class expression consist of several or_of statements in a row.')

    #Test incomplete or_of statement
    self.rpm = regex_interface.RegexParserMachine('''expr: any_char of 'abc' or_of''')
    self.assertRaises(regex_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteClassErrorState), 'End of input directly after keyword or_of should result in error.')

    #Test or_of statement with empty class
    self.rpm = regex_interface.RegexParserMachine('''expr: any_char of 'abc' or_of ""''')
    self.assertRaises(regex_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regex_states.IncompleteClassErrorState), 'Empty input to character class should result in error.')


if __name__ == '__main__':
    unittest.main()
