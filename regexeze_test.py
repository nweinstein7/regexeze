import unittest
import regexeze_errors
import regexeze_states
import regexeze
import sys
import re

class test_regex_parser_machine(unittest.TestCase):
  def setUp(self):
    self.regexObject = regexeze.RegexezeObject('')
    self.TEST_FILE_NAME = "test_files/test_file.txt"
    self.EMPTY_FILE_NAME = "test_files/empty_file.txt"
    self.TEST_ERROR_FILE_NAME = "test_files/test_error_file.txt"

  def test_init(self):
    '''
    Test the init function to make sure the parser machine has all correct initial variables
    '''
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.NewExpression))
    self.assertEquals(self.regexObject.arg_string, '', 'arg_string should start empty')
    self.assertEquals(self.regexObject.ret_val, '', 'ret_val should start empty')
    self.assertEquals(self.regexObject.current_fragment, '', 'current_fragment should start empty')
    self.assertEquals(self.regexObject.approximate_location, 0, 'approximate location should start at 0')

  def test_parse(self):
    '''
    Test the parser for correct and incorrect entries
    '''
    #TEST IO
    #Test simple expression from file
    self.regexObject = regexeze.RegexezeObject('')
    self.regexObject.parse(self.TEST_FILE_NAME)
    self.assertEquals(self.regexObject.ret_val, '(hello){10}(how\\ are\\ you)', 'Should be able to parse a simple multiline file')

    #Test empty file
    self.regexObject = regexeze.RegexezeObject('')
    self.regexObject.parse(self.EMPTY_FILE_NAME)
    self.assertEquals(self.regexObject.ret_val, '', 'Empty file empty string')

    #Test nonexistent file
    self.regexObject = regexeze.RegexezeObject('')
    self.assertRaises(IOError, self.regexObject.parse, "not_a_real_file.file")

    #Test errors in file reading
    self.regexObject = regexeze.RegexezeObject('')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse, "test_files/test_error_file.txt")
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #Test simple expression in stdin
    self.regexObject = regexeze.RegexezeObject('')
    with open(self.TEST_FILE_NAME, 'r') as sys.stdin:
      self.regexObject.parse(sys.stdin)
    self.assertEquals(self.regexObject.ret_val, '(hello){10}(how\\ are\\ you)', 'Should be able to parse a simple multiline expression from stdin')

    #Test empty stdin
    self.regexObject = regexeze.RegexezeObject('')
    with open(self.EMPTY_FILE_NAME, 'r') as sys.stdin:
      self.regexObject.parse(sys.stdin)
    self.assertEquals(self.regexObject.ret_val, '', 'Should be able to parse a simple multiline expression from stdin')

    #Test error from stdin
    self.regexObject = regexeze.RegexezeObject('')
    with open(self.TEST_ERROR_FILE_NAME, 'r') as sys.stdin:
      self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse, sys.stdin)
      self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState),
                                 'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #TEST NEW EXPRESSION ERRORS
    #test expression that is completely empty
    self.regexObject = regexeze.RegexezeObject('')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '', 'Empty expression should result in empty string')

    #test expression that starts with incorrectly capitalized keyword
    self.regexObject = regexeze.RegexezeObject('eXPr: any_char')
    self.assertRaises(regexeze_errors.NewExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.NewExpressionErrorState),
                    'After incorrect keyword at new expression, should end up in NewExpressionErrorState')

    #test expression that starts with otherwise wrong keyword
    self.regexObject = regexeze.RegexezeObject('asf: any_char;')
    self.assertRaises(regexeze_errors.NewExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.NewExpressionErrorState),
                    'After incorrect keyword at new expression, should end up in NewExpressionErrorState')

    #test incorrect expression after a first correct expression
    self.regexObject = regexeze.RegexezeObject('expr: a; asf')
    self.assertRaises(regexeze_errors.NewExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.NewExpressionErrorState),
                    'After incorrect start of second expression, should end up in NewExpressionErrorState')

    #TEST MISSING COLON
    self.regexObject = regexeze.RegexezeObject('expr "hello";')
    self.assertRaises(regexeze_errors.ColonError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.ColonErrorState),
                    'After missing colon, should end up in ColonErrorState')

    #TEST SIMPLE EXPRESSIONS
    #Test incomplete expressions (empty)
    self.regexObject = regexeze.RegexezeObject('expr: ')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input prematurely, should end up in IncompleteExpressionErrorState')

    #Test incomplete expressions (no semi-colon)
    self.regexObject = regexeze.RegexezeObject('expr: "a"')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression has no semicolon, should end up in IncompleteExpressionErrorState')

    #Test a simple, single letter expression
    self.regexObject = regexeze.RegexezeObject('expr: a;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)', 'Simple text expression should result in that simple text in a group')

    #Test two simple expressions in a row
    self.regexObject = regexeze.RegexezeObject('expr: a; expr: a;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)(a)', 'Two simple text expressions in a row should result in the two being concatenated')

    #Test complete empty expression
    self.regexObject = regexeze.RegexezeObject('expr: "";')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '()', 'Complete empty expression should simply result in an empty group')

    #Test complete empty expression followed by normal expression
    self.regexObject = regexeze.RegexezeObject('expr: ""; expr: a;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '()(a)', 'Empty expression followed by normal expression should result in empty group followed by the normal expression in a group')

    #Test any_char syntax
    self.regexObject = regexeze.RegexezeObject('expr: any_char;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(.)', 'The any_char keyword (unmodified) should result in a period in a group')

    #Test new_line syntax
    self.regexObject = regexeze.RegexezeObject('expr: new_line;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\n)', 'The new_line keyword should result in a newline expression')

    #Test tab syntax
    self.regexObject = regexeze.RegexezeObject('expr: tab;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\t)', 'tab keyword')

    #Test carriage_return syntax
    self.regexObject = regexeze.RegexezeObject('expr: carriage_return;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\r)', 'carriage_return keyword')

    #Test vertical_space syntax
    self.regexObject = regexeze.RegexezeObject('expr: vertical_space;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\v)', 'vertical_space keyword')

    #Test digit syntax
    self.regexObject = regexeze.RegexezeObject('expr: digit;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\d)', 'digit keyword')

    #Test non_digit syntax
    self.regexObject = regexeze.RegexezeObject('expr: non_digit;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\D)', 'non_digit keyword')

    #Test whitespace syntax
    self.regexObject = regexeze.RegexezeObject('expr: whitespace;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\s)', 'whitespace keyword')

    #Test non_whitespace syntax
    self.regexObject = regexeze.RegexezeObject('expr: non_whitespace;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\S)', 'non_whitespace keyword')

    #Test alphanumeric syntax
    self.regexObject = regexeze.RegexezeObject('expr: alphanumeric;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\w)', 'alphanumeric keyword')

    #Test non_alphanumeric syntax
    self.regexObject = regexeze.RegexezeObject('expr: non_alphanumeric;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\W)', 'non_alphanumeric keyword')

    #TEST GROUP NAMES
    #test simple group name
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: "1";];')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(1))', 'Simple group name')

    #test multiple group names
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: "1";]; expr: [ name: two;expr: "2";];')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(1))(?P<two>(2))', 'Two group names in sequence')

    #test group names interspersed with regular group names
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: "1"; ]; expr: "2"; expr: [ name: three; expr: "3";]; expr: "4";')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(1))(2)(?P<three>(3))(4)', 'Named groups interspersed with standard expressions')

    #test colon after name token
    self.regexObject = regexeze.RegexezeObject('expr: [ name hello;];')
    self.assertRaises(regexeze_errors.ColonError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.ColonErrorState), 'Should enforce colon after name token')

    #test invalid group name - preexisting group
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: "1";]; expr: [ name: one; expr: "1";];')
    self.assertRaises(regexeze_errors.InvalidGroupNameError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidGroupNameState), 'Group names can not have the same name as a previous group')

    #test invalid group name - collision with regexeze keyword
    self.regexObject = regexeze.RegexezeObject('expr: [name: alphanumeric; expr: alphanumeric;];')
    self.assertRaises(regexeze_errors.InvalidGroupNameError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidGroupNameState), 'Group names can not have the same name as a regexeze keyword')

    #test nested group name
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: [ name: two; expr: [ name: three; expr: "3"; ];];];')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(?P<two>(?P<three>(3))))', 'Deeply nested group names')

    #test nested group name followed by group collision
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: [ name: two; expr: [ name: three; expr: "3"; ];];]; expr: [ name: three; expr: 3;];')
    self.assertRaises(regexeze_errors.InvalidGroupNameError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidGroupNameState), 'Namespace should carry from lower nesting level to higher')

    #test nested group name that collides with parent
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: [ name: one; expr: "1"; ];];')
    self.assertRaises(regexeze_errors.InvalidGroupNameError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.child.state, regexeze_states.InvalidGroupNameState), 'Namespace should carry from higher nesting level to lower')

    #test or with group names
    self.regexObject = regexeze.RegexezeObject("expr: [ name: one; expr: 'a';] or [ name: two;  expr: 'b';];")
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val,'(?P<one>(a))|(?P<two>(b))', 'Should be able to use group names after or')

    #test invalid group name after or
    self.regexObject = regexeze.RegexezeObject("expr: [ name: one; expr: 'a';] or [ name: two; expr: 'b'; expr: [ name: two; expr: 'b';];];")
    self.assertRaises(regexeze_errors.InvalidGroupNameError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.child.state, regexeze_states.InvalidGroupNameState), 'Namespace should carry over after or')

    self.regexObject = regexeze.RegexezeObject("expr: [ name: one; expr: 'a';] or [ name: one; expr: 'b';];")
    self.assertRaises(regexeze_errors.InvalidGroupNameError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidGroupNameState), 'Namespace should carry over after or')

    #test repeated name
    self.regexObject = regexeze.RegexezeObject("expr: [ name: one; name: two; expr: 'a'; ] ;")
    self.assertRaises(regexeze_errors.NewNestedExpressionError, self.regexObject.parse)

    #TEST GROUP REFS
    #test simple group ref
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: "1";]; expr: one;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(1))(?P=one)', 'Simple group ref')

    #test nested group ref - higher to lower
    self.regexObject = regexeze.RegexezeObject('expr: [ name: one; expr: one; ];')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(?P=one))', 'Child group can reference its parent, though this is a degenerate case')

    #test nested group ref - lower to higher
    self.regexObject = regexeze.RegexezeObject('expr: [ expr: [name: one; expr: "1";]; ]; expr: one;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '((?P<one>(1)))(?P=one)', 'Expression outside of nested expression can reference previous nested expression')

    #test group ref before definition - should be treated as plain text
    self.regexObject = regexeze.RegexezeObject('expr: one; expr: [ name: one; expr: "1";];')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(one)(?P<one>(1))', 'Expression outside of nested expression can reference previous nested expression')

    #test group ref with modifier
    self.regexObject = regexeze.RegexezeObject('expr: [name: one; expr: "1";]; expr: one for zero_or_one;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(1))(?P=one)?', 'group refs should be modifiable')

    #test self referential group ref
    self.regexObject = regexeze.RegexezeObject('expr: [name: one; expr: one;];')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?P<one>(?P=one))', 'a named group should be able to contain a reference to itself, though this is a degenerate case')

    #TEST MODIFIERS
    #Test invalid modifier
    self.regexObject = regexeze.RegexezeObject('expr: any_char asdfha')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState), 'After an invalid modifier, should end up in InvalidModifierState')

    #Test invalid repetitions
    self.regexObject = regexeze.RegexezeObject('expr: any_char for asdfasdf')
    self.assertRaises(regexeze_errors.InvalidRepetitionsError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidRepetitionsErrorState), 'After an invalid number of repetitions specified, should end up in InvalidRepetitionsErrorState')

    #Test valid modifier missing semicolon
    self.regexObject = regexeze.RegexezeObject('expr: any_char for zero_or_more')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState), 'Expression with modifier must end in semicolon')

    #Test zero_or_more_modifier - default greedy
    self.regexObject = regexeze.RegexezeObject('expr: any_char for zero_or_more;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(.)*', 'Should be able to parse simple zero or one (*) modifier')

    #Test zero_or_more modifier with incorrect greedy/not-greedy modifier
    self.regexObject = regexeze.RegexezeObject('expr: any_char for zero_or_more afsadf;')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState), 'After an invalid greedy/not-greedy modifier, should end up in InvalidModifierState')

    #Test zero_or_more modifier - not greedy
    self.regexObject = regexeze.RegexezeObject('expr: any_char for zero_or_more not_greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(.)*?', 'Should be able to parse a not greedy zero_or_more (*) modifier')

    #Test two consecutive modified expressions
    self.regexObject = regexeze.RegexezeObject('''expr: "a" for zero_or_more greedy; expr: "hello" for zero_or_more greedy;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)*(hello)*', 'Should be able to parse two consecutive modified statements')

    #Test one_or_more_modifier - default greedy
    self.regexObject = regexeze.RegexezeObject('expr: any_char for one_or_more;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(.)+', 'Should be able to parse the one_or_more (+) modifier')

    #Test one_or_more modifier with not greedy
    self.regexObject = regexeze.RegexezeObject('expr: "a" for one_or_more not_greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)+?', 'Should be able to parse one_or_more_modifier not greedy')

    #Test zero_or_one modifier - default greedy
    self.regexObject = regexeze.RegexezeObject('expr: "a" for zero_or_one;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)?', 'Expression modified zero_or_one should result in the expression in a group followed by question mark')

    #Test zero_or_one modifier - not greedy
    self.regexObject = regexeze.RegexezeObject('expr: "a" for zero_or_one not_greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)??', 'Expression modified zero_or_one not_greedy should result in the expression in a group followed by two question marks')

    #Test zero_or_one modifier - missing semicolon
    self.regexObject = regexeze.RegexezeObject('expr: "a" for zero_or_one not_greedy')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState), 'Expression with greedy must end in semicolon')

    #Test zero_or_one modifier with superfluous *greedy* modifier
    self.regexObject = regexeze.RegexezeObject('expr: "a" for zero_or_one greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)?', 'Should be able to supply greedy/not_greedy regardless of the default greediness')

    #Test one_or_more modifier with superfluous *greedy* modifier
    self.regexObject = regexeze.RegexezeObject('expr: "a" for one_or_more greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)+', 'Should be able to supply greedy/not_greedy regardless of the default greediness')

    #Test m repetitions modifier
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){1}', 'Should be able to parse simple m repetitions modifier')

    #Test m repetitions modifier superfluous greedy
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){1}', 'Should be able to supply greedy/not_greedy regardless of default')

    #Test m repetitions modifier not greedy
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 not_greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){1}?', 'Should be able to parse m repetitions not greedy')

    #Test m repetitions modifier followed by up_to then end of expression
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 up_to;')
    self.assertRaises(regexeze_errors.InvalidRepetitionRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer')

    #Test m repetitions modifier followed by up_to then non integer
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 up_to asdfasdf;')
    self.assertRaises(regexeze_errors.InvalidRepetitionRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer')

    #Test m repetitions modifier followed by up_to then non lower number
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 2 up_to 1;')
    self.assertRaises(regexeze_errors.InvalidRepetitionRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidRepetitionRangeErrorState), 'Keyword up_to must be followed by an integer greater than or equal to previous number')

    #Test m repetitions modifier followed by up_to then equal number
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 up_to 1;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){1,1}', 'Should be able to parse m up_to n repetitions where m = n')

    #Test m up_to n repetitions
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 up_to 2;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){1,2}', 'Should be able to parse m up_to n repetitions')

    #Test m up_to n repetitions greedy (default - no change from above)
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 up_to 2 greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){1,2}', 'Should be able to parse m up_to n repetitions specifying greedy')

    #Test m up_to n repetitions not greedy
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 1 up_to 2 not_greedy;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){1,2}?', 'Should be able to parse m up_to n reptitions not greedy')

    #Test m up_to infinity repetitions
    self.regexObject = regexeze.RegexezeObject('expr: "a" for 10 up_to infinity;')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a){10,}', 'Should be able to parse number range of repetitions, where the upper bound is unlimited (infinity keyword)')

    #TEST NESTING
    #Simple nesting (1 layer)
    self.regexObject = regexeze.RegexezeObject('''expr: [expr: 'a';];''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '((a))', 'Simple nested expression should end up with expression inside two sets of parentheses')

    #Complex nesting (3 layer)
    self.regexObject = regexeze.RegexezeObject('''expr: [expr: [expr: 'abc' for zero_or_more greedy;]; expr: 'hello';] for 1;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(((abc)*)(hello)){1}', 'Complex nested expressions should be parsed correctly')

    #Deep nesting (5 layer)
    self.regexObject = regexeze.RegexezeObject('''expr: [expr: [expr: [expr: [expr: 'abc';];];];];''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(((((abc)))))', 'Deeply nested expressions should be parsed correctly')

    #Ending before brackets are closed
    self.regexObject = regexeze.RegexezeObject('''expr: [expr: 'a';''')
    self.assertRaises(regexeze_errors.UnclosedBracketError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.UnclosedBracketErrorState), 'Expression cannot end in the middle of a nested expression')

    #Using an open square bracket ([) as an expression
    self.regexObject = regexeze.RegexezeObject('''expr: [ for zero_or_one;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(\\[)?', 'Should still be able to use [ as an expression')

    #TEST OR
    #Simple or expression
    self.regexObject = regexeze.RegexezeObject('''expr: 'a' or 'b';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)|(b)', 'Should be able to parse a simple or statement')

    #Or with modifiers
    self.regexObject = regexeze.RegexezeObject('''expr: 'a' for zero_or_one greedy or 'b' for one_or_more;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)?|(b)+', 'Should be able to parse or with modifiers')

    #Or with nested components
    self.regexObject = regexeze.RegexezeObject('''expr: [expr: 'a' for zero_or_one greedy;] or [ expr: 'b' for one_or_more;];''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '((a)?)|((b)+)', 'Should be able to parse or between two nested expressions')

    #Or fully nested
    self.regexObject = regexeze.RegexezeObject('''expr: [expr: 'a' for zero_or_one greedy or 'b' for one_or_more;];''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '((a)?|(b)+)', 'Should be able to limit the reach of or by grouping it using a nested expression')

    #Or invalid syntax - using expr: after or
    self.regexObject = regexeze.RegexezeObject('''expr: [expr: 'a' for zero_or_one greedy or expr: 'b' for one_or_more;];''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.child.state, regexeze_states.InvalidModifierState), 'Using expr after or is treated as an invalid modifier state, because it thinks "expr:" is the input and "b" is the modifier.')

    #Incomplete or
    self.regexObject = regexeze.RegexezeObject('''expr: 'a' for zero_or_one greedy or''')
    self.assertRaises(regexeze_errors.IncompleteOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteOrErrorState), 'If the expression ends on an or, should result in an incomplete or error.')

    #Expression after or
    self.regexObject = regexeze.RegexezeObject('''expr: 'a' or 'b'; expr: 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    #Or after expression
    self.regexObject = regexeze.RegexezeObject('''expr: 'a'; expr: 'b' or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    self.regexObject = regexeze.RegexezeObject('''expr: 'a' for 1 up_to infinity; expr: any_char or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    self.regexObject = regexeze.RegexezeObject('''expr: start_of_string; expr: start_of_string or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    self.regexObject = regexeze.RegexezeObject('''expr: any_char except "abc"; expr: any_char of "def" or 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.MultipleOrErrorState), 'There can be only one expression containing or - should use nesting for or statements if you want more than one.')

    #Multiple ors in a row
    self.regexObject = regexeze.RegexezeObject('''expr: 'a' or 'b' or 'c' or 'd';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(a)|(b)|(c)|(d)', 'Should be able to have any number of ors in a row')

    #TEST CLASSES
    #Test simple class
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([abc])', 'Should be able to parse a simple class expression.')

    #Test incomplete class statement
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword of should result in error.')

    #Test empty class statement
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'Empty input to character class should result in an error..')

    #Test simple class statement with special chars
    self.regexObject = regexeze.RegexezeObject(r'''expr: any_char of '.*$@^\';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, r'([\.\*\$\@\^\\])', 'Should be able to parse a simple class expression with non alphanumeric chars')

    #Test simple class statement with keywords
    self.regexObject = regexeze.RegexezeObject(r'''expr: any_char of new_line;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([\n])', 'Should be able to parse a simple class expression.')

    #Test simple or_of
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc' or_of 'def';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([abcdef])', 'Should be able to parse simple or_of expression')

    #Test or_of in sequence
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc' or_of 'def' or_of 'ghi';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([abcdefghi])', 'Should be able to parse complex class expression consisting of several or_of statements in a row.')

    #Test incomplete or_of statement
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc' or_of''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword or_of should result in error.')

    #Test or_of statement with empty class
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc' or_of ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'Empty input to character class should result in error.')

    #Test simple class range
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'a' to 'z';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([a-z])', 'Should be able to parse a simple class range.')

    #Test simple class range between single char
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'a' to 'a';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([a-a])', 'Should be able to parse a simple class range bounded by the same char.')

    #Test class range with special characters
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from '$' to '@';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([\$-\@])', 'Should be able to parse a class range with special characters.')

    #Test invalid class range - more than one char in from
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'abc' to 'z';""''')
    self.assertRaises(regexeze_errors.InvalidClassRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidClassRangeErrorState), 'More than one char in the from value should cause an InvalidClassRange error')

    #Test invalid class range - more than one char in to
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'a' to 'xyz';""''')
    self.assertRaises(regexeze_errors.InvalidClassRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidClassRangeErrorState), 'More than one char in the to value should cause an InvalidClassRange error')

    #Test invalid class range - wrong order
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'z' to 'a';""''')
    self.assertRaises(regexeze_errors.InvalidClassRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidClassRangeErrorState), 'Incorrect order should result in InvalidClassRangeError')

    #Test incomplete class range
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from""''')
    self.assertRaises(regexeze_errors.IncompleteClassRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassRangeErrorState), 'Ending after from should result in incomplete class range error')

    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'z'""''')
    self.assertRaises(regexeze_errors.IncompleteClassRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassRangeErrorState), 'Ending after from value should result in IncompleteClassRangeError')

    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'z' to""''')
    self.assertRaises(regexeze_errors.IncompleteClassRangeError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassRangeErrorState), 'Ending after to should result in IncompleteClassRangeError')

    #Test or_from (simple)
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'a' to 'c' or_from 'd' to 'g';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([a-cd-g])', 'Should be able to parse two class ranges connected using or_from.')

    #Test or_from (special chars)
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'a' to 'c' or_from '$' to '@';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([a-c\$-\@])', 'Should be able to parse two class ranges including special characters connected using or_from.')

    #Test multiple or_from in a row
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'a' to 'c' or_from '$' to '@' or_from 'd' to 'f' or_from 'k' to 'z';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([a-c\$-\@d-fk-z])', 'Should be able to parse multiple character ranges strung together using or_from')

    #Test of to or_from
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc' or_from 'd' to 'f';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([abcd-f])', 'Should be able to transition from "of" to "or_from"')

    #Test of to or_except
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc' or_except 'def' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState), 'Wrong type of or after "of" leads to invalid modifier state')

    #Test from/to to or_of
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'd' to 'f' or_of 'xyz';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([d-fxyz])', 'Should be able to transition from "from/to" to "or_of"')

    #Test or_from interleaved with or_of
    self.regexObject = regexeze.RegexezeObject('''expr: any_char of 'abc' or_from 'c' to 'e' or_from '$' to '@' or_of 'def' or_from 'k' to 'z';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([abcc-e\$-\@defk-z])', 'Should be able to go from of to or_from to or_of to or_from')

    #Test from with  or_except
    self.regexObject = regexeze.RegexezeObject('''expr: any_char from 'a' to 'z' or_except 'abc' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState), 'Wrong type of or after "from...to" leads to invalid modifier state')

    #Test simple except
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except 'abc';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([^abc])', 'Should be able to parse a simple complement class expression.')

    #Test incomplete complement class statement
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword except should result in error.')

    #Test empty complement class statement
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'Empty input to complement character class should result in an error..')

    #Test simple class statement with special chars
    self.regexObject = regexeze.RegexezeObject(r'''expr: any_char except '^';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, r'([^\^])', 'Should be able to parse a simple class expression.')

    #Test simple or_except
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except 'abc' or_except 'def';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([^abcdef])', 'Should be able to parse complex class expression consist of several or_of statements in a row.')

    #Test or_except in sequence
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except 'abc' or_except 'def' or_except 'ghi';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '([^abcdefghi])', 'Should be able to parse complex class expression consist of several or_except statements in a row.')

    #Test incomplete or_except statement
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except 'abc' or_except''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'End of input directly after keyword or_except should result in error.')

    #Test or_except statement with empty class
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except 'abc' or_except ""''')
    self.assertRaises(regexeze_errors.IncompleteClassError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteClassErrorState), 'Empty input to character class should result in error.')

    #Test except statement with with or_of
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except 'abc' or_of 'def' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState), 'Wrong type of or after except leads to invalid modifier state')

    #Test except statement with with or_from
    self.regexObject = regexeze.RegexezeObject('''expr: any_char except 'abc' or_from 'def' ""''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState), 'Wrong type of or after except leads to invalid modifier state')

    #TEST START OF STRING AND END OF STRING
    #Test simple start of string/end of string
    self.regexObject = regexeze.RegexezeObject('''expr: start_of_string; expr: 'abc'; expr: end_of_string;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(^)(abc)($)', 'Should be able to parse simple start_of_string/end_of_string.')

    #Test incomplete start_of_string/end_of_string
    self.regexObject = regexeze.RegexezeObject('''expr: start_of_string''')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input after start_of_string, should end up in IncompleteExpressionErrorState')

    self.regexObject = regexeze.RegexezeObject('''expr: end_of_string''')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState),
                    'When expression reaches end of input after end_of_string, should end up in IncompleteExpressionErrorState')

    #Test invalid modifier after start_of_string/end_of_string
    self.regexObject = regexeze.RegexezeObject('''expr: start_of_string for 10;''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState),
                    'Should not be able to modify start_of_string')

    self.regexObject = regexeze.RegexezeObject('''expr: end_of_string for 10''')
    self.assertRaises(regexeze_errors.InvalidModifierError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidModifierState),
                    'Should not be able to modify end_of_string')

    #TEST FLAGS
    #test basic positive use of flags
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case, locale, multiline, any_char_all, unicode; expr: 'a';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?iLmsu)(a)', "Flag keywords should be handled properly")

    #test basic negative use of flags
    #missing colon
    self.regexObject = regexeze.RegexezeObject('''set_flags ignore_case, locale, multiline, any_char_all, unicode; expr: 'a';''')
    self.assertRaises(regexeze_errors.FlagsColonError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.FlagsColonErrorState),
                    'Should enforce colon after set_flags keyword')

    #incorrect flag
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case, hello, multiline, any_char_all, unicode; expr: 'a';''')
    self.assertRaises(regexeze_errors.InvalidFlagError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidFlagState),
                    'Flags should be valid')

    #flags not comma-separated
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case dotall, multiline, any_char_all, unicode; expr: 'a';''')
    self.assertRaises(regexeze_errors.InvalidFlagError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.InvalidFlagState),
                    'Flags should be comma separated')

    #no semicolon after flags
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case''')
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.IncompleteExpressionErrorState),
                    'Flags should be followed by semi-colon')

    #test flag edge cases
    #empty expression with flags
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case, locale, multiline, any_char_all, unicode;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?iLmsu)', "An expression can be empty except for flags")

    #repeated flags - acceptable
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case, ignore_case, ignore_case; expr: 'a';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?iii)(a)', "Flags can be repeated indefinitely")

    #repeated flag settings - acceptable
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case; expr: 'a'; set_flags: multiline;''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?i)(a)(?m)', "Flags can be set anywhere in an expression")

    #flags can be set before or statements
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case; expr: 'a' or 'b';''')
    self.regexObject.parse()
    self.assertEquals(self.regexObject.ret_val, '(?i)(a)|(b)', "Flags can coexist with or's")

    #multiple ors on same nesting level still error with flags
    self.regexObject = regexeze.RegexezeObject('''set_flags: ignore_case; expr: 'a' or 'b'; expr: 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.MultipleOrErrorState), 'Flags do not interfere with or nesting rules')

    self.regexObject = regexeze.RegexezeObject('''expr: 'a' or 'b'; set_flags: ignore_case; expr: 'c';''')
    self.assertRaises(regexeze_errors.MultipleOrError, self.regexObject.parse)
    self.assertTrue(isinstance(self.regexObject.state, regexeze_states.MultipleOrErrorState), 'Flags do not interfere with or nesting rules')

    #TEST ACCURACY OF REGEXES
    #test special characters
    self.regexObject = regexeze.RegexezeObject('''expr: "$\." for one_or_more;''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('$\.$\.').group(0), '$\.$\.', "Should be able to use ret_val as a regular expression to match a string containing special characters")

    #test new_line
    self.regexObject = regexeze.RegexezeObject('''expr: "a"; expr: new_line; expr: "b";''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('a\nb').group(0), 'a\nb', "Should be able to use ret_val as a regular expression to match a string with newline")

    #test new_line (negative)
    self.assertIsNone(matcher.match('a1b'), "Regex with newline should not match string without newline")

    #test digit
    self.regexObject = regexeze.RegexezeObject('''expr: "a"; expr: digit; expr: "b";''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('a1b').group(0), 'a1b', "Should be able to use ret_val as a regular expression to match a string with digit")

    #test digit (negative)
    self.assertIsNone(matcher.match('aab'), "Regex with digit should not match string with non-digit")

    #test non_digit
    self.regexObject = regexeze.RegexezeObject('''expr: "a"; expr: non_digit; expr: "b";''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('a b').group(0), 'a b', "Should be able to use ret_val as a regular expression to match a string with non_digit")

    #test non_digit (negative)
    self.assertIsNone(matcher.match('a1b'), "Regex with non_digit should not match string with digit")

    #test whitespace
    self.regexObject = regexeze.RegexezeObject('''expr: "a"; expr: whitespace; expr: "b";''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('a b').group(0), 'a b', "Should be able to use ret_val as a regular expression to match a string with whitespace")

    #test whitespace (negative)
    self.assertIsNone(matcher.match('a1b'), "Should be able to use ret_val as a regular expression to match a string with whitespace")

    #test non_whitespace
    self.regexObject = regexeze.RegexezeObject('''expr: "a"; expr: non_whitespace; expr: "b";''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('a1b').group(0), 'a1b', "Should be able to use ret_val as a regular expression to match a string with non_whitespace")

    #test non_whitespace (negative)
    self.assertIsNone(matcher.match('a b'), "Should be able to use ret_val as a regular expression to match a string with non_whitespace")

    #test carriage_return
    self.regexObject = regexeze.RegexezeObject('''expr: "a"; expr: carriage_return; expr: "b";''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('a\rb').group(0), 'a\rb', "Should be able to use ret_val as a regular expression to match a string with carriage_return")

    #test carriage_return (negative)
    self.assertIsNone(matcher.match('a b'), "Expression with carriage_return should not match a string without a carriage return")

    #test rest of keywords
    self.regexObject = regexeze.RegexezeObject('''expr: page_break; expr: vertical_space; expr: alphanumeric; expr: non_alphanumeric;''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('\f\va.').group(0), '\f\va.', "Should be able to use ret_val as a regular expression to match a string with assorted keyword characters")

    #test class matching with keywords
    self.regexObject = regexeze.RegexezeObject(r'''expr: any_char of new_line or_of tab or_of digit;''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('\n').group(0), '\n', "Should be able to match a character set including keyword new_line")
    self.assertEquals(matcher.match('\t').group(0), '\t', "Should be able to match a character set including keyword tab")
    self.assertEquals(matcher.match('1').group(0), '1', "Should be able to match a character set including keyword digit")

    #test class matching with keywords (negative)
    self.assertIsNone(matcher.match('a'), "Should not match characters that aren't in a character class with keywords")

    #test complement class matching with keywords
    self.regexObject = regexeze.RegexezeObject(r'''expr: any_char except whitespace or_except digit;''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('.').group(0), '.', "Should be able to match a complement character set including keywords")
    self.assertEquals(matcher.match('a').group(0), 'a', "Should be able to match a complement character set including keywords")

    #test complement class matching with keywords (negative)
    self.assertIsNone(matcher.match(' '), "Should not match characters in complement character class with keywords")
    self.assertIsNone(matcher.match('1'), "Should not match characters in complement character class with keywords")

    #test class matching with keywords and slashes
    self.regexObject = regexeze.RegexezeObject(r'''expr: any_char of '\' or_of new_line;''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match('\n').group(0), '\n', "Should be able to match a character set including keyword new_line and slash")
    self.assertEquals(matcher.match('\\').group(0), '\\', "Should be able to match a character set including keyword new_line and slash")

    self.regexObject = regexeze.RegexezeObject(r'''expr: any_char of '\' or_of whitespace;''')
    self.regexObject.parse()
    matcher = re.compile(self.regexObject.ret_val)
    self.assertEquals(matcher.match(' ').group(0), ' ', "Should be able to match a character set including keyword new_line and slash")
    self.assertEquals(matcher.match('\\').group(0), '\\', "Should be able to match a character set including keyword new_line and slash")

  def test_compile(self):
    '''
    Tests the compile method
    '''
    #test compiling a simple regexeze object
    regexezeObject = regexeze.compile("expr: 'a';")
    self.assertEquals('(a)', regexezeObject.ret_val, "compile should be able to compile a simple regexeze object")

  def test_search(self):
    '''
    Tests the search method
    '''
    #test searching for a simple regexeze match in a string
    self.assertIsNotNone(regexeze.search("expr: 'd';", "dog"), "searching for a simple match should work")

    #test searching for a regex that does not match
    self.assertIsNone(regexeze.search("expr: 'The End.'; expr: end_of_string;", "The End. Just kidding."), "Search should return None when no match is found")

  def test_match(self):
    '''
    Tests the match method
    '''
    #test matching with a simple regexeze pattern
    self.assertIsNotNone(regexeze.match("expr: digit for 3;", "123"))

    #test matching with a simple regexeze pattern and string that doesn't match
    self.assertIsNone(regexeze.match("expr: digit for 3;", "12"))

if __name__ == '__main__':
    unittest.main()
