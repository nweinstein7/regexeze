import unittest
import regexeze_errors
import regexeze_states
import regexeze
import sys
import re

class test_regex_parser_machine(unittest.TestCase):
  def setUp(self):
    self.rpm = regexeze.RegexParserMachine('')
    self.TEST_FILE_NAME = "test_files/test_file.txt"
    self.EMPTY_FILE_NAME = "test_files/empty_file.txt"
    self.TEST_ERROR_FILE_NAME = "test_files/test_error_file.txt"

  def test_init(self):
    '''
    Test the init function to make sure the parser machine has all correct initial variables
    '''
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.NewExpression))
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
    self.rpm = regexeze.RegexParserMachine('')
    self.rpm.parse(self.TEST_FILE_NAME)
    self.assertEquals(self.rpm.ret_val, '(hello){10}(how\\ are\\ you)', 'Should be able to parse a simple multiline file')

    #Test empty file
    self.rpm = regexeze.RegexParserMachine('')
    self.rpm.parse(self.EMPTY_FILE_NAME)
    self.assertEquals(self.rpm.ret_val, '', 'Empty file empty string')

    #Test nonexistent file
    self.rpm = regexeze.RegexParserMachine('')
    self.assertRaises(IOError, self.rpm.parse, "not_a_real_file.file")

    #Test errors in file reading
    self.rpm = regexeze.RegexParserMachine('')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse, "test_files/test_error_file.txt")
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #Test simple expression in stdin
    self.rpm = regexeze.RegexParserMachine('')
    with open(self.TEST_FILE_NAME, 'r') as sys.stdin:
      self.rpm.parse(sys.stdin)
    self.assertEquals(self.rpm.ret_val, '(hello){10}(how\\ are\\ you)', 'Should be able to parse a simple multiline expression from stdin')

    #Test empty stdin
    self.rpm = regexeze.RegexParserMachine('')
    with open(self.EMPTY_FILE_NAME, 'r') as sys.stdin:
      self.rpm.parse(sys.stdin)
    self.assertEquals(self.rpm.ret_val, '', 'Should be able to parse a simple multiline expression from stdin')

    #Test error from stdin
    self.rpm = regexeze.RegexParserMachine('')
    with open(self.TEST_ERROR_FILE_NAME, 'r') as sys.stdin:
      self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse, sys.stdin)
      self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState),                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #TEST NEW EXPRESSION ERRORS
    #test expression that is completely empty
    self.rpm = regexeze.RegexParserMachine('')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '', 'Empty expression should result in empty string')

    #test expression that starts with incorrectly capitalized keyword
    self.rpm = regexeze.RegexParserMachine('eXPr: any_char')
    self.assertRaises(regexeze_errors.NewExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.NewExpressionErrorState),
                    'After incorrect keyword at new expression, should end up in NewExpressionErrorState')

    #test expression that starts with otherwise wrong keyword
    self.rpm = regexeze.RegexParserMachine('asf: any_char;')
    self.assertRaises(regexeze_errors.NewExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.NewExpressionErrorState),
                    'After incorrect keyword at new expression, should end up in NewExpressionErrorState')

    #test incorrect expression after a first correct expression
    self.rpm = regexeze.RegexParserMachine('expr: a; asf')
    self.assertRaises(regexeze_errors.NewExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.NewExpressionErrorState),
                    'After incorrect start of second expression, should end up in NewExpressionErrorState')

    #TEST MISSING COLON
    self.rpm = regexeze.RegexParserMachine('expr any_char;')
    self.assertRaises(regexeze_errors.ColonError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.ColonErrorState),
                    'After missing colon, should end up in ColonErrorState')

    #TEST SIMPLE EXPRESSIONS
    #Test incomplete expressions (empty)
    self.rpm = regexeze.RegexParserMachine('expr: ')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #Test incomplete expressions (no semi-colon)
    self.rpm = regexeze.RegexParserMachine('expr: "a"')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression has no semicolon, should end up in IncompleteExpressionErrorState')

    #Test a simple, single letter expression
    self.rpm = regexeze.RegexParserMachine('expr: a;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)', 'Simple text expression should result in that simple text in a group')

    #Test two simple expressions in a row
    self.rpm = regexeze.RegexParserMachine('expr: a; expr: a;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)(a)', 'Two simple text expressions in a row should result in the two being concatenated')

    #Test complete empty expression
    self.rpm = regexeze.RegexParserMachine('expr: "";')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '()', 'Complete empty expression should simply result in an empty group')

    #Test complete empty expression followed by normal expression
    self.rpm = regexeze.RegexParserMachine('expr: ""; expr: a;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '()(a)', 'Empty expression followed by normal expression should result in empty group followed by the normal expression in a group')

    #Test any_char syntax
    self.rpm = regexeze.RegexParserMachine('expr: any_char;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)', 'The any_char keyword (unmodified) should result in a period in a group')

    #Test new_line syntax
    self.rpm = regexeze.RegexParserMachine('expr: new_line;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\n)', 'The new_line keyword should result in a newline expression')

    #Test tab syntax
    self.rpm = regexeze.RegexParserMachine('expr: tab;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\t)', 'tab keyword')

    #Test carriage_return syntax
    self.rpm = regexeze.RegexParserMachine('expr: carriage_return;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\r)', 'carriage_return keyword')

    #Test vertical_space syntax
    self.rpm = regexeze.RegexParserMachine('expr: vertical_space;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\v)', 'vertical_space keyword')

    #Test digit syntax
    self.rpm = regexeze.RegexParserMachine('expr: digit;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\d)', 'digit keyword')

    #Test non_digit syntax
    self.rpm = regexeze.RegexParserMachine('expr: non_digit;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\D)', 'non_digit keyword')

    #Test whitespace syntax
    self.rpm = regexeze.RegexParserMachine('expr: whitespace;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\s)', 'whitespace keyword')

    #Test non_whitespace syntax
    self.rpm = regexeze.RegexParserMachine('expr: non_whitespace;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\S)', 'non_whitespace keyword')

    #Test alphanumeric syntax
    self.rpm = regexeze.RegexParserMachine('expr: alphanumeric;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\w)', 'alphanumeric keyword')

    #Test non_alphanumeric syntax
    self.rpm = regexeze.RegexParserMachine('expr: non_alphanumeric;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\W)', 'non_alphanumeric keyword')

    #TEST MODIFIERS
    #Test invalid modifier
    self.rpm = regexeze.RegexParserMachine('expr: any_char asdfha')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState), 'After an invalid modifier, should end up in InvalidModifierState')

    #Test invalid repetitions
    self.rpm = regexeze.RegexParserMachine('expr: any_char for asdfasdf')
    self.assertRaises(regexeze_errors.InvalidRepetitionsError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidRepetitionsErrorState), 'After an invalid number of repetitions specified, should end up in InvalidRepetitionsErrorState')

    #Test valid modifier missing semicolon
    self.rpm = regexeze.RegexParserMachine('expr: any_char for zero_or_more')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState), 'Expression with modifier must end in semicolon')

    #Test zero_or_more_modifier - default greedy
    self.rpm = regexeze.RegexParserMachine('expr: any_char for zero_or_more;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)*', 'Should be able to parse simple zero or one (*) modifier')

    #Test zero_or_more modifier with incorrect greedy/not-greedy modifier
    self.rpm = regexeze.RegexParserMachine('expr: any_char for zero_or_more afsadf;')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState), 'After an invalid greedy/not-greedy modifier, should end up in InvalidModifierState')

    #Test zero_or_more modifier - not greedy
    self.rpm = regexeze.RegexParserMachine('expr: any_char for zero_or_more not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)*?', 'Should be able to parse a not greedy zero_or_more (*) modifier')

    #Test two consecutive modified expressions
    self.rpm = regexeze.RegexParserMachine('''expr: "a" for zero_or_more greedy; expr: "hello" for zero_or_more greedy;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)*(hello)*', 'Should be able to parse two consecutive modified statements')

    #Test one_or_more_modifier - default greedy
    self.rpm = regexeze.RegexParserMachine('expr: any_char for one_or_more;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(.)+', 'Should be able to parse the one_or_more (+) modifier')

    #Test one_or_more modifier with not greedy
    self.rpm = regexeze.RegexParserMachine('expr: "a" for one_or_more not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)+?', 'Should be able to parse one_or_more_modifier not greedy')

    #Test zero_or_one modifier - default greedy
    self.rpm = regexeze.RegexParserMachine('expr: "a" for zero_or_one;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)?', 'Expression modified zero_or_one should result in the expression in a group followed by question mark')

    #Test zero_or_one modifier - not greedy
    self.rpm = regexeze.RegexParserMachine('expr: "a" for zero_or_one not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)??', 'Expression modified zero_or_one not_greedy should result in the expression in a group followed by two question marks')

    #Test zero_or_one modifier - missing semicolon
    self.rpm = regexeze.RegexParserMachine('expr: "a" for zero_or_one not_greedy')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState), 'Expression with greedy must end in semicolon')

    #Test zero_or_one modifier with superfluous *greedy* modifier
    self.rpm = regexeze.RegexParserMachine('expr: "a" for zero_or_one greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)?', 'Should be able to supply greedy/not_greedy regardless of the default greediness')

    #Test one_or_more modifier with superfluous *greedy* modifier
    self.rpm = regexeze.RegexParserMachine('expr: "a" for one_or_more greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)+', 'Should be able to supply greedy/not_greedy regardless of the default greediness')

    #Test m repetitions modifier
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}', 'Should be able to parse simple m repetitions modifier')

    #Test m repetitions modifier superfluous greedy
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}', 'Should be able to supply greedy/not_greedy regardless of default')

    #Test m repetitions modifier not greedy
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1}?', 'Should be able to parse m repetitions not greedy')

    #Test m repetitions modifier followed by up_to then end of expression
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 up_to;')
    self.assertRaises(regexeze_errors.InvalidRepetitionRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer')

    #Test m repetitions modifier followed by up_to then non integer
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 up_to asdfasdf;')
    self.assertRaises(regexeze_errors.InvalidRepetitionRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer')

    #Test m repetitions modifier followed by up_to then non lower number
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 2 up_to 1;')
    self.assertRaises(regexeze_errors.InvalidRepetitionRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer greater than or equal to previous number')

    #Test m repetitions modifier followed by up_to then equal number
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 up_to 1;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,1}', 'Should be able to parse m up_to n repetitions where m = n')

    #Test m up_to n repetitions
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 up_to 2;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}', 'Should be able to parse m up_to n repetitions')

    #Test m up_to n repetitions greedy (default - no change from above)
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 up_to 2 greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}', 'Should be able to parse m up_to n repetitions specifying greedy')

    #Test m up_to n repetitions not greedy
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 1 up_to 2 not_greedy;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){1,2}?', 'Should be able to parse m up_to n reptitions not greedy')

    #Test m up_to infinity repetitions
    self.rpm = regexeze.RegexParserMachine('expr: "a" for 10 up_to infinity;')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a){10,}', 'Should be able to parse number range of repetitions, where the upper bound is unlimited (infinity keyword)')

    #TEST NESTING
    #Simple nesting (1 layer)
    self.rpm = regexeze.RegexParserMachine('''expr: [expr: 'a';];''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '((a))', 'Simple nested expression should end up with expression inside two sets of parentheses')

    #Complex nesting (3 layer)
    self.rpm = regexeze.RegexParserMachine('''expr: [expr: [expr: 'abc' for zero_or_more greedy;]; expr: 'hello';] for 1;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(((abc)*)(hello)){1}', 'Complex nested expressions should be parsed correctly')

    #Deep nesting (5 layer)
    self.rpm = regexeze.RegexParserMachine('''expr: [expr: [expr: [expr: [expr: 'abc';];];];];''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(((((abc)))))', 'Deeply nested expressions should be parsed correctly')

    #Ending before brackets are closed
    self.rpm = regexeze.RegexParserMachine('''expr: [expr: 'a';''')
    self.assertRaises(regexeze_errors.UnclosedBracketError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.UnclosedBracketErrorState), 'Expression cannot end in the middle of a nested expression')

    #Using an open square bracket ([) as an expression
    self.rpm = regexeze.RegexParserMachine('''expr: [ for zero_or_one;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(\\[)?', 'Should still be able to use [ as an expression')

    #TEST OR
    #Simple or expression
    self.rpm = regexeze.RegexParserMachine('''expr: 'a' or 'b';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)|(b)', 'Should be able to parse a simple or statement')

    #Or with modifiers
    self.rpm = regexeze.RegexParserMachine('''expr: 'a' for zero_or_one greedy or 'b' for one_or_more;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)?|(b)+', 'Should be able to parse or with modifiers')

    #Or with nested components
    self.rpm = regexeze.RegexParserMachine('''expr: [expr: 'a' for zero_or_one greedy;] or [ expr: 'b' for one_or_more;];''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '((a)?)|((b)+)', 'Should be able to parse or between two nested expressions')

    #Or fully nested
    self.rpm = regexeze.RegexParserMachine('''expr: [expr: 'a' for zero_or_one greedy or 'b' for one_or_more;];''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '((a)?|(b)+)', 'Should be able to limit the reach of or by grouping it using a nested expression')

    #Or invalid syntax - using expr: after or
    self.rpm = regexeze.RegexParserMachine('''expr: [expr: 'a' for zero_or_one greedy or expr: 'b' for one_or_more;];''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.child.state, regexeze_states.InvalidModifierState), 'Using expr after or is treated as an invalid modifier state, because it thinks "expr:" is the input and "b" is the modifier.')

    #Incomplete or
    self.rpm = regexeze.RegexParserMachine('''expr: 'a' for zero_or_one greedy or''')
    self.assertRaises(regexeze_errors.IncompleteOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteOrErrorState), 'If the expression ends on an or, should result in an incomplete or error.')

    #Expression after or
    self.rpm = regexeze.RegexParserMachine('''expr: 'a' or 'b'; expr: 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    #Or after expression
    self.rpm = regexeze.RegexParserMachine('''expr: 'a'; expr: 'b' or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    self.rpm = regexeze.RegexParserMachine('''expr: 'a' for 1 up_to infinity; expr: any_char or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    self.rpm = regexeze.RegexParserMachine('''expr: start_of_string; expr: start_of_string or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    self.rpm = regexeze.RegexParserMachine('''expr: any_char except "abc"; expr: any_char of "def" or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    #Multiple ors in a row
    self.rpm = regexeze.RegexParserMachine('''expr: 'a' or 'b' or 'c' or 'd';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(a)|(b)|(c)|(d)', 'Should be able to have any number of ors in a row')

    #TEST CLASSES
    #Test simple class
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([abc])', 'Should be able to parse a simple class expression.')

    #Test incomplete class statement
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword of should result in error.')

    #Test empty class statement
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'Empty input to character class should result in an error..')

    #Test simple class statement with special chars
    self.rpm = regexeze.RegexParserMachine(r'''expr: any_char of '.*$@^\';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, r'([\.\*\$\@\^\\])', 'Should be able to parse a simple class expression with non alphanumeric chars')

    #Test simple class statement with keywords
    self.rpm = regexeze.RegexParserMachine(r'''expr: any_char of new_line;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([\n])', 'Should be able to parse a simple class expression.')

    #Test simple or_of
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc' or_of 'def';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([abcdef])', 'Should be able to parse simple or_of expression')

    #Test or_of in sequence
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc' or_of 'def' or_of 'ghi';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([abcdefghi])', 'Should be able to parse complex class expression consisting of several or_of statements in a row.')

    #Test incomplete or_of statement
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc' or_of''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword or_of should result in error.')

    #Test or_of statement with empty class
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc' or_of ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'Empty input to character class should result in error.')

    #Test simple class range
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'a' to 'z';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([a-z])', 'Should be able to parse a simple class range.')

    #Test simple class range between single char
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'a' to 'a';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([a-a])', 'Should be able to parse a simple class range bounded by the same char.')

    #Test class range with special characters
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from '$' to '@';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([\$-\@])', 'Should be able to parse a class range with special characters.')

    #Test invalid class range - more than one char in from
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'abc' to 'z';""''')
    self.assertRaises(regexeze_errors.InvalidClassRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidClassRangeErrorState), 'More than one char in the from value should cause an InvalidClassRange error')

    #Test invalid class range - more than one char in to
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'a' to 'xyz';""''')
    self.assertRaises(regexeze_errors.InvalidClassRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidClassRangeErrorState), 'More than one char in the to value should cause an InvalidClassRange error')

    #Test invalid class range - wrong order
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'z' to 'a';""''')
    self.assertRaises(regexeze_errors.InvalidClassRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidClassRangeErrorState), 'Incorrect order should result in InvalidClassRangeError')

    #Test incomplete class range
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from""''')
    self.assertRaises(regexeze_errors.IncompleteClassRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassRangeErrorState), 'Ending after from should result in incomplete class range error')

    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'z'""''')
    self.assertRaises(regexeze_errors.IncompleteClassRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassRangeErrorState), 'Ending after from value should result in IncompleteClassRangeError')

    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'z' to""''')
    self.assertRaises(regexeze_errors.IncompleteClassRangeError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassRangeErrorState), 'Ending after to should result in IncompleteClassRangeError')

    #Test or_from (simple)
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'a' to 'c' or_from 'd' to 'g';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([a-cd-g])', 'Should be able to parse two class ranges connected using or_from.')

    #Test or_from (special chars)
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'a' to 'c' or_from '$' to '@';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([a-c\$-\@])', 'Should be able to parse two class ranges including special characters connected using or_from.')

    #Test multiple or_from in a row
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'a' to 'c' or_from '$' to '@' or_from 'd' to 'f' or_from 'k' to 'z';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([a-c\$-\@d-fk-z])', 'Should be able to parse multiple character ranges strung together using or_from')

    #Test of to or_from
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc' or_from 'd' to 'f';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([abcd-f])', 'Should be able to transition from "of" to "or_from"')

    #Test of to or_except
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc' or_except 'def' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState), 'Wrong type of or after "of" leads to invalid modifier state')

    #Test from/to to or_of
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'd' to 'f' or_of 'xyz';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([d-fxyz])', 'Should be able to transition from "from/to" to "or_of"')

    #Test or_from interleaved with or_of
    self.rpm = regexeze.RegexParserMachine('''expr: any_char of 'abc' or_from 'c' to 'e' or_from '$' to '@' or_of 'def' or_from 'k' to 'z';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([abcc-e\$-\@defk-z])', 'Should be able to go from of to or_from to or_of to or_from')

    #Test from with  or_except
    self.rpm = regexeze.RegexParserMachine('''expr: any_char from 'a' to 'z' or_except 'abc' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState), 'Wrong type of or after "from...to" leads to invalid modifier state')

    #Test simple except
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except 'abc';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([^abc])', 'Should be able to parse a simple complement class expression.')

    #Test incomplete complement class statement
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword except should result in error.')

    #Test empty complement class statement
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'Empty input to complement character class should result in an error..')

    #Test simple class statement with special chars
    self.rpm = regexeze.RegexParserMachine(r'''expr: any_char except '^';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, r'([^\^])', 'Should be able to parse a simple class expression.')

    #Test simple or_except
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except 'abc' or_except 'def';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([^abcdef])', 'Should be able to parse complex class expression consist of several or_of statements in a row.')

    #Test or_except in sequence
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except 'abc' or_except 'def' or_except 'ghi';''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '([^abcdefghi])', 'Should be able to parse complex class expression consist of several or_except statements in a row.')

    #Test incomplete or_except statement
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except 'abc' or_except''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword or_except should result in error.')

    #Test or_except statement with empty class
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except 'abc' or_except ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteClassErrorState), 'Empty input to character class should result in error.')

    #Test except statement with with or_of
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except 'abc' or_of 'def' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState), 'Wrong type of or after except leads to invalid modifier state')

    #Test except statement with with or_from
    self.rpm = regexeze.RegexParserMachine('''expr: any_char except 'abc' or_from 'def' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState), 'Wrong type of or after except leads to invalid modifier state')

    #TEST START OF STRING AND END OF STRING
    #Test simple start of string/end of string
    self.rpm = regexeze.RegexParserMachine('''expr: start_of_string; expr: 'abc'; expr: end_of_string;''')
    self.rpm.parse()
    self.assertEquals(self.rpm.ret_val, '(^)(abc)($)', 'Should be able to parse simple start_of_string/end_of_string.')

    #Test incomplete start_of_string/end_of_string
    self.rpm = regexeze.RegexParserMachine('''expr: start_of_string''')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input after start_of_string, should end up in IncompleteExpressionErrorState')

    self.rpm = regexeze.RegexParserMachine('''expr: end_of_string''')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input after end_of_string, should end up in IncompleteExpressionErrorState')

    #Test invalid modifier after start_of_string/end_of_string
    self.rpm = regexeze.RegexParserMachine('''expr: start_of_string for 10;''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState),
                    'Should not be able to modify start_of_string')

    self.rpm = regexeze.RegexParserMachine('''expr: end_of_string for 10''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.rpm.parse)
    self.assertTrue(isinstance(self.rpm.state, regexeze_states.InvalidModifierState),
                    'Should not be able to modify end_of_string')


    #TEST ACCURACY OF REGEXES
    #test special characters
    self.rpm = regexeze.RegexParserMachine('''expr: "$\." for one_or_more;''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('$\.$\.').group(0), '$\.$\.', "Should be able to use ret_val as a regular expression to match a string containing special characters")

    #test new_line
    self.rpm = regexeze.RegexParserMachine('''expr: "a"; expr: new_line; expr: "b";''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('a\nb').group(0), 'a\nb', "Should be able to use ret_val as a regular expression to match a string with newline")

    #test new_line (negative)
    self.assertIsNone(matcher.match('a1b'), "Regex with newline should not match string without newline")

    #test digit
    self.rpm = regexeze.RegexParserMachine('''expr: "a"; expr: digit; expr: "b";''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('a1b').group(0), 'a1b', "Should be able to use ret_val as a regular expression to match a string with digit")

    #test digit (negative)
    self.assertIsNone(matcher.match('aab'), "Regex with digit should not match string with non-digit")

    #test non_digit
    self.rpm = regexeze.RegexParserMachine('''expr: "a"; expr: non_digit; expr: "b";''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('a b').group(0), 'a b', "Should be able to use ret_val as a regular expression to match a string with non_digit")

    #test non_digit (negative)
    self.assertIsNone(matcher.match('a1b'), "Regex with non_digit should not match string with digit")

    #test whitespace
    self.rpm = regexeze.RegexParserMachine('''expr: "a"; expr: whitespace; expr: "b";''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('a b').group(0), 'a b', "Should be able to use ret_val as a regular expression to match a string with whitespace")

    #test whitespace (negative)
    self.assertIsNone(matcher.match('a1b'), "Should be able to use ret_val as a regular expression to match a string with whitespace")

    #test non_whitespace
    self.rpm = regexeze.RegexParserMachine('''expr: "a"; expr: non_whitespace; expr: "b";''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('a1b').group(0), 'a1b', "Should be able to use ret_val as a regular expression to match a string with non_whitespace")

    #test non_whitespace (negative)
    self.assertIsNone(matcher.match('a b'), "Should be able to use ret_val as a regular expression to match a string with non_whitespace")

    #test carriage_return
    self.rpm = regexeze.RegexParserMachine('''expr: "a"; expr: carriage_return; expr: "b";''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('a\rb').group(0), 'a\rb', "Should be able to use ret_val as a regular expression to match a string with carriage_return")

    #test carriage_return (negative)
    self.assertIsNone(matcher.match('a b'), "Expression with carriage_return should not match a string without a carriage return")

    #test rest of keywords
    self.rpm = regexeze.RegexParserMachine('''expr: page_break; expr: vertical_space; expr: alphanumeric; expr: non_alphanumeric;''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('\f\va.').group(0), '\f\va.', "Should be able to use ret_val as a regular expression to match a string with assorted keyword characters")

    #test class matching with keywords
    self.rpm = regexeze.RegexParserMachine(r'''expr: any_char of new_line or_of tab or_of digit;''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('\n').group(0), '\n', "Should be able to match a character set including keyword new_line")
    self.assertEquals(matcher.match('\t').group(0), '\t', "Should be able to match a character set including keyword tab")
    self.assertEquals(matcher.match('1').group(0), '1', "Should be able to match a character set including keyword digit")

    #test class matching with keywords (negative)
    self.assertIsNone(matcher.match('a'), "Should not match characters that aren't in a character class with keywords")

    #test complement class matching with keywords
    self.rpm = regexeze.RegexParserMachine(r'''expr: any_char except whitespace or_except digit;''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('.').group(0), '.', "Should be able to match a complement character set including keywords")
    self.assertEquals(matcher.match('a').group(0), 'a', "Should be able to match a complement character set including keywords")

    #test complement class matching with keywords (negative)
    self.assertIsNone(matcher.match(' '), "Should not match characters in complement character class with keywords")
    self.assertIsNone(matcher.match('1'), "Should not match characters in complement character class with keywords")

    #test class matching with keywords and slashes
    self.rpm = regexeze.RegexParserMachine(r'''expr: any_char of '\' or_of new_line;''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match('\n').group(0), '\n', "Should be able to match a character set including keyword new_line and slash")
    self.assertEquals(matcher.match('\\').group(0), '\\', "Should be able to match a character set including keyword new_line and slash")

    self.rpm = regexeze.RegexParserMachine(r'''expr: any_char of '\' or_of whitespace;''')
    self.rpm.parse()
    matcher = re.compile(self.rpm.ret_val)
    self.assertEquals(matcher.match(' ').group(0), ' ', "Should be able to match a character set including keyword new_line and slash")
    self.assertEquals(matcher.match('\\').group(0), '\\', "Should be able to match a character set including keyword new_line and slash")

if __name__ == '__main__':
    unittest.main()
