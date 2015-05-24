import unittest
import regexeze_errors
import regexeze_states
import regexeze
import sys
import re
import argparse
from StringIO import StringIO

class RegexezeTestCase(unittest.TestCase):
  '''
  parent class for all test cases, with constants
  '''
  TEST_FILE_NAME = "test_files/test_file.rgxz"
  EMPTY_FILE_NAME = "test_files/empty_file.rgxz"
  TEST_ERROR_FILE_NAME = "test_files/test_error_file.rgxz"

  #translation of the file's pattern into python standard syntax
  FILE_TRANSLATION = '(hello){10}(how\\ are\\ you)'

class FileInputTestCase(RegexezeTestCase):
  '''
  Test case for reading from file
  '''
  def testSimpleFile(self):
    '''
    Positive test for reading from a file
    '''
    translation = regexeze.translate(pattern="", source=self.TEST_FILE_NAME)
    self.assertEquals(translation, self.FILE_TRANSLATION, 'Should be able to parse a simple file')

  def testEmptyFile(self):
    '''
    Positive test for reading empty file
    '''
    translation = regexeze.translate(pattern="", source=self.EMPTY_FILE_NAME)
    self.assertEquals(translation, '', "Translating an empty file should result in an empty string")

  def testNonexistentFile(self):
    '''
    Negative test for reading from a filename that does not exist
    '''
    self.assertRaises(IOError, regexeze.translate, '', 'notarealfile.file')

  def testFileWithErrors(self):
    '''
    Negative test for reading from a file that contains syntax errors
    '''
    self.assertRaises(regexeze_errors.IncompleteExpressionError, regexeze.translate,
                      '', self.TEST_ERROR_FILE_NAME)

class StdinTestCase(RegexezeTestCase):
  '''
  Test case for reading from stdin
  '''
  def setUp(self):
    #translation of the given input
    self.translation = ""

  def runWithStdinAsFile(self, file=""):
    '''
    Helper method for running translate with stdin as input, sending a file to stdin
    @param file: the filename of the file that will serve as mock stdin
    @type file: str
    '''
    with open(file, 'r') as sys.stdin:
      self.translation = regexeze.translate(pattern="", source=sys.stdin)

  def testSimpleStdin(self):
    '''
    Positive test: Test a simple expression from stdin
    '''
    self.runWithStdinAsFile(file=self.TEST_FILE_NAME)
    self.assertEquals(self.translation, self.FILE_TRANSLATION,
                      "Should be able to parse a simple expression from stdin")

  def testEmptyStdin(self):
    '''
    Positive test: empty stdin
    '''
    self.runWithStdinAsFile(file=self.EMPTY_FILE_NAME)
    self.assertEquals(self.translation, '',
                      "Empty expression in stdin results in empty string as translation")

  def testStdinError(self):
    '''
    Negative test: stdin input has error in it
    '''
    self.assertRaises(regexeze_errors.IncompleteExpressionError, self.runWithStdinAsFile,
                      self.TEST_ERROR_FILE_NAME)

class SyntaxTestCase(RegexezeTestCase):
  '''
  Parent class for testing syntax
  '''
  def setUp(self):
    self.pattern = ""
    self.correctTranslation = ""
    self.assertStatement = ""
    self.error = None

  def runPositiveSyntaxTest(self):
    '''
    Method for running a positive syntax test
    Translates the given pattern and matches it against the correctTranslation
    '''
    translation = regexeze.translate(self.pattern)
    self.assertEquals(translation, self.correctTranslation, self.assertStatement)

  def runNegativeSyntaxTest(self):
    '''
    Method for running a negative syntax test
    Attempts to compile the given pattern and asserts that it raises the proper error
    '''
    self.assertRaises(self.error, regexeze.compile, self.pattern)

class BasicSyntaxTestCase(SyntaxTestCase):
  '''
  Test case for confirming the basic syntax of regexeze
  '''
  def testEmptyExpression(self):
    '''
    Positive test: expression that is completely empty translates to empty string
    '''
    self.assertStatement = 'Empty expression should result in empty string'
    self.runPositiveSyntaxTest()

  def testSimpleExpression(self):
    '''
    Positive test: basic correct expression
    '''
    self.pattern = "expr: 'a';"
    self.correctTranslation = "(a)"
    self.assertStatement = 'Simple pattern should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testIncorrectlyCapitalizedExpr(self):
    '''
    Negative test: tests the case sensitivity of the keyword expr
    '''
    self.pattern = "eXPr: any_char;"
    self.error = regexeze_errors.NewExpressionError
    self.runNegativeSyntaxTest()

  def testWrongKeywordExpr(self):
    '''
    Negative test: wrong keyword at start of expression
    '''
    self.pattern = "asf: any_char;"
    self.error = regexeze_errors.NewExpressionError
    self.runNegativeSyntaxTest()

  def testWrongKeywordExprAfterCorrectExpression(self):
    '''
    Negative test: wrong keyword at start of *second* expression
    '''
    self.pattern = "expr: a; asf"
    self.error = regexeze_errors.NewExpressionError
    self.runNegativeSyntaxTest()

  def testMissingColon(self):
    '''
    Negative test: missing colon after keyword "expr"
    '''
    self.pattern = 'expr "hello";'
    self.error = regexeze_errors.ColonError
    self.runNegativeSyntaxTest()

  def testIncompleteExpressionEmpty(self):
    '''
    Negative test: expression that ends prematurely after "expr:"
    '''
    self.pattern = 'expr: '
    self.error = regexeze_errors.IncompleteExpressionError
    self.runNegativeSyntaxTest()

  def testIncompleteExpressionNoSemicolon(self):
    '''
    Negative test: expression that has no semicolon
    '''
    self.pattern = 'expr: "a"'
    self.error = regexeze_errors.IncompleteExpressionError
    self.runNegativeSyntaxTest()

  def testTwoExpressionsInARow(self):
    '''
    Positive test: make sure two consecutive expressions can be parsed
    '''
    self.pattern = 'expr: a; expr: a;'
    self.correctTranslation = "(a)(a)"
    self.assertStatement = 'Two simple text expressions in a row should result in the two being concatenated'
    self.runPositiveSyntaxTest()

  def testCompleteEmptyExpression(self):
    '''
    Positive test: a valid expression with empty string as its value
    '''
    self.pattern = 'expr: "";'
    self.correctTranslation = '()'
    self.assertStatement = 'Complete empty expression should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testEmptyExpressionFollowedByExpression(self):
    '''
    Positive test: expression following expression with empty string as its value
    '''
    self.pattern = 'expr: ""; expr: a;'
    self.correctTranslation = '()(a)'
    self.assertStatement = 'Empty expression followed by normal expression should be parsed correctly'
    self.runPositiveSyntaxTest()

class ValueKeywordSyntaxTestCase(SyntaxTestCase):
  '''
  Test case for "value keywords", i.e. keywords that can be used as values for expressions
  For example, "expr: any_char;" - any_char is a value keyword
  '''
  def testAnyChar(self):
    '''
    Positive test: keyword any_char
    '''
    self.pattern = 'expr: any_char;'
    self.correctTranslation = '(.)'
    self.assertStatement = 'The any_char keyword (unmodified) should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testNewLine(self):
    '''
    Positive test: keyword new_line
    '''
    self.pattern = 'expr: new_line;'
    self.correctTranslation = '(\n)'
    self.assertStatement = 'The new_line keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testTab(self):
    '''
    Positive test: keyword tab
    '''
    self.pattern = 'expr: tab;'
    self.correctTranslation = '(\t)'
    self.assertStatement = 'The tab keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testCarriageReturn(self):
    '''
    Positive test: keyword carriage_return
    '''
    self.pattern = 'expr: carriage_return;'
    self.correctTranslation = '(\r)'
    self.assertStatement = 'The carriage_return keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testVerticalSpace(self):
    '''
    Positive test: keyword vertical_space
    '''
    self.pattern = 'expr: vertical_space;'
    self.correctTranslation = '(\v)'
    self.assertStatement = 'The vertical_space keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testDigit(self):
    '''
    Positive test: keyword digit
    '''
    self.pattern = 'expr: digit;'
    self.correctTranslation = '(\d)'
    self.assertStatement = 'The digit keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testNonDigit(self):
    '''
    Positive test: keyword non_digit
    '''
    self.pattern = 'expr: non_digit;'
    self.correctTranslation = '(\D)'
    self.assertStatement = 'The non_digit keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testWhitespace(self):
    '''
    Positive test: keyword whitespace
    '''
    self.pattern = 'expr: whitespace;'
    self.correctTranslation = '(\s)'
    self.assertStatement = 'The whitespace keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testNonWhitespace(self):
    '''
    Positive test: keyword non_whitespace
    '''
    self.pattern = 'expr: non_whitespace;'
    self.correctTranslation = '(\S)'
    self.assertStatement = 'The non_whitespace keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testAlphanumeric(self):
    '''
    Positive test: keyword alphanumeric
    '''
    self.pattern = 'expr: alphanumeric;'
    self.correctTranslation = '(\w)'
    self.assertStatement = 'The alphanumeric keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

  def testNonAlphanumeric(self):
    '''
    Positive test: keyword non_alphanumeric
    '''
    self.pattern = 'expr: non_alphanumeric;'
    self.correctTranslation = '(\W)'
    self.assertStatement = 'The non_alphanumeric keyword should be parsed correctly'
    self.runPositiveSyntaxTest()

class ModifierSyntaxTestCase(SyntaxTestCase):
  '''
  Test case for modifiers
  '''
  def testInvalidModifier(self):
    '''
    Negative test: invalid modifier after the value of the expression
    '''
    self.pattern = 'expr: any_char asdfha'
    self.error = regexeze_errors.InvalidModifierError
    self.runNegativeSyntaxTest()

  def testInvalidRepetition(self):
    '''
    Negative test: invalid modifier after keyword "for"
    '''
    self.pattern = 'expr: any_char for asdfasdf;'
    self.error = regexeze_errors.InvalidRepetitionsError
    self.runNegativeSyntaxTest()

  def testMissingSemicolonAfterZeroOrMoreModifier(self):
    '''
    Negative test: missing semicolon after zero_or_more
    '''
    self.pattern = 'expr: any_char for zero_or_more'
    self.error = regexeze_errors.IncompleteExpressionError
    self.runNegativeSyntaxTest()

  def testZeroOrMoreModifier(self):
    '''
    Positive test: test zero_or_more modifier syntax
    '''
    self.pattern = 'expr: any_char for zero_or_more;'
    self.correctTranslation = '(.)*'
    self.assertStatement = 'Should be able to parse simple zero_or_more modifier'
    self.runPositiveSyntaxTest()

  def testIncorrectGreedyOrNotGreedyModifier(self):
    '''
    Negative test: invalid modifier after the value of the expression
    '''
    self.pattern = 'expr: any_char for zero_or_more afsadf;'
    self.error = regexeze_errors.InvalidModifierError
    self.runNegativeSyntaxTest()

  def testZeroOrMoreModifierNotGreedy(self):
    '''
    Positive test: test zero_or_more modifier - not greedy
    '''
    self.pattern = 'expr: any_char for zero_or_more not_greedy;'
    self.correctTranslation = '(.)*?'
    self.assertStatement = 'Should be able to parse not greedy zero_or_more modifier'
    self.runPositiveSyntaxTest()

  def testMultipleModifiedExpressions(self):
    '''
    Positive test: test multiple modified expressions
    '''
    self.pattern = 'expr: "a" for zero_or_more greedy; expr: "hello" for zero_or_more greedy;'
    self.correctTranslation = '(a)*(hello)*'
    self.assertStatement = 'Should be able to parse pattern containing multiple modified expressions'
    self.runPositiveSyntaxTest()

  def testMissingSemicolonAfterOneOrMoreModifier(self):
    '''
    Negative test: missing semicolon after one_or_more
    '''
    self.pattern = 'expr: any_char for one_or_more'
    self.error = regexeze_errors.IncompleteExpressionError
    self.runNegativeSyntaxTest()

  def testOneOrMoreModifier(self):
    '''
    Positive test: test one_or_more modifier
    '''
    self.pattern = 'expr: any_char for one_or_more;'
    self.correctTranslation = '(.)+'
    self.assertStatement = 'Should be able to parse simple one_or_more modifier'
    self.runPositiveSyntaxTest()

  def testOneOrMoreModifierNotGreedy(self):
    '''
    Positive test: test one_or_more modifier - not greedy
    '''
    self.pattern = 'expr: any_char for one_or_more not_greedy;'
    self.correctTranslation = '(.)+?'
    self.assertStatement = 'Should be able to parse not greedy one_or_more modifier'
    self.runPositiveSyntaxTest()

  def testZeroOrOneModifier(self):
    '''
    Positive test: test zero_or_one modifier
    '''
    self.pattern = 'expr: any_char for zero_or_one;'
    self.correctTranslation = '(.)?'
    self.assertStatement = 'Should be able to parse simple zero_or_one modifier'
    self.runPositiveSyntaxTest()

  def testZeroOrOneModifierNotGreedy(self):
    '''
    Positive test: test zero_or_one modifier - not greedy
    '''
    self.pattern = 'expr: any_char for zero_or_one not_greedy;'
    self.correctTranslation = '(.)??'
    self.assertStatement = 'Should be able to parse not greedy zero_or_one modifier'
    self.runPositiveSyntaxTest()

  def testMissingSemicolonAfterZeroOrOneModifier(self):
    self.pattern = 'expr: any_char for zero_or_one'
    self.error = regexeze_errors.IncompleteExpressionError
    self.runNegativeSyntaxTest()

  def testZeroOrMoreSuperfluousGreedy(self):
    '''
    Positive test: checks that the greedy key word can be used even when unnecessary after zero_or_more
    '''
    self.pattern = 'expr: any_char for zero_or_more greedy;'
    self.correctTranslation = '(.)*'
    self.assertStatement = 'Should be able to use "greedy" keyword after zero_or_more'
    self.runPositiveSyntaxTest()

  def testOneOrMoreSuperfluousGreedy(self):
    '''
    Positive test: checks that the greedy key word can be used even when unnecessary after one_or_more
    '''
    self.pattern = 'expr: any_char for one_or_more greedy;'
    self.correctTranslation = '(.)+'
    self.assertStatement = 'Should be able to use "greedy" keyword after one_or_more'
    self.runPositiveSyntaxTest()

  def testZeroOrOneSuperfluousGreedy(self):
    '''
    Positive test: checks that the greedy key word can be used even when unnecessary after one_or_one
    '''
    self.pattern = 'expr: any_char for zero_or_one greedy;'
    self.correctTranslation = '(.)?'
    self.assertStatement = 'Should be able to use "greedy" keyword after zero_or_one'
    self.runPositiveSyntaxTest()

  def testMRepetitionsModifier(self):
    '''
    Positive test: test the m repetitions modifier
    '''
    self.pattern = 'expr: "a" for 1;'
    self.correctTranslation = '(a){1}'
    self.assertStatement = 'Should be able to parse simple m reptitions modifier'
    self.runPositiveSyntaxTest()

  def testMRepetitionsSuperfluousGreedy(self):
    '''
    Positive test: test the m repetitions modifier with unnecessary greedy modifier
    '''
    self.pattern = 'expr: "a" for 1 greedy;'
    self.correctTranslation = '(a){1}'
    self.assertStatement = 'Should be able to use greedy after m repetitions modifier'
    self.runPositiveSyntaxTest()

  def testMRepetitionsModifierNotGreedy(self):
    '''
    Positive test: test the m repetitions modifier - not greedy
    '''
    self.pattern = 'expr: "a" for 1 not_greedy;'
    self.correctTranslation = '(a){1}?'
    self.assertStatement = 'Should be able to parse not greedy m repetitions modifier'
    self.runPositiveSyntaxTest()

  def testIncompleteUpto(self):
    '''
    Negative test: m repetitions with up_to keyword followed by end of expression
    '''
    self.pattern = 'expr: "a" for 1 up_to;'
    self.error = regexeze_errors.InvalidRepetitionRangeError
    self.runNegativeSyntaxTest()

  def testNonintegerUpto(self):
    '''
    Negative test: m repetitions with up_to keyword followed by non-integer
    '''
    self.pattern = 'expr: "a" for 1 up_to asdfasdf;'
    self.error = regexeze_errors.InvalidRepetitionRangeError
    self.runNegativeSyntaxTest()

  def testUptoLowerNumber(self):
    '''
    Negative test: m repetitions with up_to keyword followed by lower number
    '''
    self.pattern = 'expr: "a" for 2 up_to 1;'
    self.error = regexeze_errors.InvalidRepetitionRangeError
    self.runNegativeSyntaxTest()

  def testUptoEqualNumber(self):
    '''
    Positive test: m repetitions with up_to keyword followed by equal number
    '''
    self.pattern = 'expr: "a" for 1 up_to 1;'
    self.correctTranslation = '(a){1,1}'
    self.assertStatement = 'Should be able to parse m up_to n repetitions where m = n'
    self.runPositiveSyntaxTest()

  def testMUpToNRepetitions(self):
    '''
    Positive test: parse simple m up to n repetitions modifier
    '''
    self.pattern = 'expr: "a" for 1 up_to 2;'
    self.correctTranslation = '(a){1,2}'
    self.assertStatement = 'Should be able to parse m up_to n repetitions'
    self.runPositiveSyntaxTest()

  def testMUpToNRepetitionsSuperfluousGreedy(self):
    '''
    Positive test: parse m up to n repetitions with unnecessary greedy keyword
    '''
    self.pattern = 'expr: "a" for 1 up_to 2 greedy;'
    self.correctTranslation = '(a){1,2}'
    self.assertStatement = 'Should be able to parse m up_to n repetitions specifying greedy'
    self.runPositiveSyntaxTest()

  def testMUpToNRepetitionsNotGreedy(self):
    '''
    Positive test: parse m up to n repetitions not greedy
    '''
    self.pattern = 'expr: "a" for 1 up_to 2 not_greedy;'
    self.correctTranslation = '(a){1,2}?'
    self.assertStatement = 'Should be able to parse m up_to n reptitions not greedy'
    self.runPositiveSyntaxTest()

  def testMUpToInfinityRepetitions(self):
    '''
    Positive test: infinity keyword
    '''
    self.pattern = 'expr: "a" for 10 up_to infinity;'
    self.correctTranslation = '(a){10,}'
    self.assertStatement = 'Should be able to parse number range of repetitions, where the upper bound is unlimited (infinity keyword)'
    self.runPositiveSyntaxTest()

class CharacterClassSyntaxTestCase(SyntaxTestCase):
  '''
  Test case for testing the character class syntax, which consists of the keyword "any_char"
  followed by keywords "of", "from", and "except", additionally followed by keywords
  "to", "or_of", "or_from", and "or_except"
  '''
  def testSimpleClass(self):
    '''
    Positive test case: test basic character class
    '''
    self.pattern = "expr: any_char of 'abc';"
    self.correctTranslation = '([abc])'
    self.assertStatement = 'Should be able to parse a simple character class expression.'
    self.runPositiveSyntaxTest()

  def testIncompleteCharacterClassPattern(self):
    '''
    Negative test: character class which ends right after "of" keyword
    '''
    self.pattern = "expr: any_char of"
    self.error = regexeze_errors.IncompleteClassError
    self.runNegativeSyntaxTest()

  def testEmptyCharacterClass(self):
    '''
    Negative test: empty character classes are prohibited by the syntax
    '''
    self.pattern = 'expr: any_char of "";'
    self.error = regexeze_errors.IncompleteClassError
    self.runNegativeSyntaxTest()

  def testCharacterClassWithSpecialCharacters(self):
    '''
    Positive test: special characters should work in a character class
    '''
    self.pattern = r'''expr: any_char of '.*$@^\';'''
    self.correctTranslation = r'([\.\*\$\@\^\\])'
    self.assertStatement = 'Should be able to parse a simple class expression with non alphanumeric chars'
    self.runPositiveSyntaxTest()

  def testCharacterClassWithValueKeyword(self):
    '''
    Positive test: character classes can contain regexeze value keywords such as new_line and tab
    '''
    self.pattern = 'expr: any_char of new_line;'
    self.correctTranslation = '([\n])'
    self.assertStatement = 'Should be able to parse a class expression with value keyword'
    self.runPositiveSyntaxTest()

  def testOrOf(self):
    '''
    Positive test: basic functionality of the "or_of" keyword
    '''
    self.pattern = '''expr: any_char of 'abc' or_of 'def';'''
    self.correctTranslation = '([abcdef])'
    self.assertStatement = 'Should be able to parse simple or_of expression'
    self.runPositiveSyntaxTest()

  def testOrOfSequence(self):
    '''
    Positive test: multiple "or_of"s in a row are syntactically acceptable
    (They combine to make a longer character class)
    '''
    self.pattern = '''expr: any_char of 'abc' or_of 'def' or_of 'ghi';'''
    self.correctTranslation = '([abcdefghi])'
    self.assertStatement = 'Should be able to parse complex class expression consisting of several or_of statements in a row.'
    self.runPositiveSyntaxTest()

  def testIncompleteOrOf(self):
    '''
    Negative test: pattern that ends after keyword "or_of"
    '''
    self.pattern = '''expr: any_char of 'abc' or_of'''
    self.error = regexeze_errors.IncompleteClassError
    self.runNegativeSyntaxTest()

  def testOrOfEmpty(self):
    '''
    Negative test: "or_of" keyword that leads into an empty token
    Classes cannot be empty, thus or_of cannot lead into an empty string
    '''
    self.pattern = '''expr: any_char of 'abc' or_of ""'''
    self.error = regexeze_errors.IncompleteClassError
    self.runNegativeSyntaxTest()

  def testClassRange(self):
    '''
    Positive test: test the syntax for a character class defined by a range between two characters
    '''
    self.pattern = '''expr: any_char from 'a' to 'z';'''
    self.correctTranslation = '([a-z])'
    self.assertStatement = 'Should be able to parse a simple class range.'
    self.runPositiveSyntaxTest()

  def testClassRangeSameChar(self):
    '''
    Positive test: a class range between a character and itself is syntactically acceptable
    '''
    self.pattern = '''expr: any_char from 'a' to 'a';'''
    self.correctTranslation = '([a-a])'
    self.assertStatement = 'Should be able to parse a simple class range bounded by the same char.'
    self.runPositiveSyntaxTest()

  def testClassRangeSpecialCharacters(self):
    '''
    Positive test: class range bounded by non-alphanumeric characters
    '''
    self.pattern = '''expr: any_char from '$' to '@';'''
    self.correctTranslation = '([\$-\@])'
    self.assertStatement = 'Should be able to parse a class range with special characters.'
    self.runPositiveSyntaxTest()

  def testInvalidClassRangeTooManyCharactersInFromValue(self):
    '''
    Negative test: class range where the "from" value is more than one character
    '''
    self.pattern = '''expr: any_char from 'abc' to 'z';'''
    self.error = regexeze_errors.InvalidClassRangeError
    self.runNegativeSyntaxTest()

  def testInvalidClassRangeTooManyCharactersInToValue(self):
    '''
    Negative test: class range where the "to" value is more than one character
    '''
    self.pattern = '''expr: any_char from 'a' to 'xyz';'''
    self.error = regexeze_errors.InvalidClassRangeError
    self.runNegativeSyntaxTest()

  def testInvalidClassRangeWrongOrder(self):
    '''
    Negative test: class range where the "from" value comes alphabetically after the "to" value
    '''
    self.pattern = '''expr: any_char from 'z' to 'a';'''
    self.error = regexeze_errors.InvalidClassRangeError
    self.runNegativeSyntaxTest()

  def testIncompleteClassRangeEndAfterFrom(self):
    '''
    Negative test: class range where input ends after "from" keyword
    '''
    self.pattern = '''expr: any_char from'''
    self.error = regexeze_errors.IncompleteClassRangeError
    self.runNegativeSyntaxTest()

  def testIncompleteClassRangeEndAfterFromValue(self):
    '''
    Negative test: class range with "from" keyword and value, but no "to" keyword or "to" value
    '''
    self.pattern = '''expr: any_char from "z"'''
    self.error = regexeze_errors.IncompleteClassRangeError
    self.runNegativeSyntaxTest()

  def testIncompleteClassRangeInvalidKeywordInPlaceOfTo(self):
    '''
    Negative test: class range that has gibberish keyword instead of "to" keyword
    '''
    self.pattern = '''expr: any_char from "a" asdf "z";'''
    self.error = regexeze_errors.IncompleteClassRangeError
    self.runNegativeSyntaxTest()

  def testIncompleteClassRangeEndAfterTo(self):
    '''
    Negative test: class range where input ends after "to" keyword
    '''
    self.pattern = '''expr: any_char from "z" to'''
    self.error = regexeze_errors.IncompleteClassRangeError
    self.runNegativeSyntaxTest()

  def testOrFrom(self):
    '''
    Positive test: simple use of or_from keyword to denote continuation of character class
    '''
    self.pattern = '''expr: any_char from "a" to "c" or_from "d" to "g";'''
    self.correctTranslation = '([a-cd-g])'
    self.assertStatement = 'Should be able to parse two class ranges connected using or_from.'
    self.runPositiveSyntaxTest()

  def testOrFromSpecialChars(self):
    '''
    Positive test: or_from keyword with non-alphanumeric character range
    '''
    self.pattern = '''expr: any_char from 'a' to 'c' or_from '$' to '@';'''
    self.correctTranslation = '([a-c\$-\@])'
    self.assertStatement = 'Should be able to parse two class ranges including special characters connected using or_from.'
    self.runPositiveSyntaxTest()

class test_regex_parser_machine(RegexezeTestCase):
  def setUp(self):
    self.regexObject = regexeze.RegexezeObject('')

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
    #TEST SIMPLE EXPRESSIONS
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

class RegexezeSubparserTest(RegexezeTestCase):
  '''
  Test case for testing the command line subparsers
  '''
  def setUp(self):
    self.args = argparse.Namespace()
    self.out = StringIO()
    self.saved_stdout = sys.stdout
    sys.stdout = self.out

    #simple pattern to be tested
    self.pattern = 'expr: "a";'

    #the function that this test calls
    self.function = None

  def runFunction(self, args):
    '''
    Runs the function with the given args
    @param args: the arguments to use
    @type args: argparse.Namespace
    '''
    self.function(args)
    self.output = self.out.getvalue().strip()

  def testPattern(self):
    '''
    Test what happens when subparser is given a pattern
    '''
    self.args.pattern = self.pattern
    self.args.filename = ""
    self.runFunction(self.args)

  def testFilename(self):
    '''
    Tests what happens when subparser is given a filename
    '''
    self.args.pattern = ""
    self.args.filename = self.TEST_FILE_NAME
    self.runFunction(self.args)

  def testStdin(self):
    '''
    Tests when subparser takes input from stdin
    '''
    self.args.pattern = ""
    self.args.filename = ""

    with open(self.TEST_FILE_NAME, 'r') as sys.stdin:
      self.function(self.args)
    self.output = self.out.getvalue().strip()

  def tearDown(self):
    sys.stdout = self.saved_stdout

class RegexezeTargetStringSubparserTest(RegexezeSubparserTest):
  '''
  Test case for testing subparsers that take in a target string
  '''
  def setUp(self):
    super(RegexezeTargetStringSubparserTest, self).setUp()
    self.target_string = "a"
    self.args.target_string = self.target_string

    #create target string to match the test file
    self.testFileTargetString = "hellohellohellohellohellohellohellohellohellohellohow are you"

  def testFilename(self):
    self.args.target_string = self.testFileTargetString
    super(RegexezeTargetStringSubparserTest, self).testFilename()

  def testStdin(self):
    self.args.target_string = self.testFileTargetString
    super(RegexezeTargetStringSubparserTest, self).testStdin()

class TranslateSubparserTest(RegexezeSubparserTest):
  '''
  Test case for testing the translate subparser
  '''
  def setUp(self):
    super(TranslateSubparserTest, self).setUp()
    self.function = regexeze.translateMain

  def testPattern(self):
    super(TranslateSubparserTest, self).testPattern()
    self.assertEquals(self.output, '(a)',
                      "passing only a pattern to translateMain should translate the pattern")

  def testFilename(self):
    super(TranslateSubparserTest, self).testFilename()
    self.assertEquals(self.output, '(hello){10}(how\\ are\\ you)',
                      "passing filename should translate pattern in the file")

  def testStdin(self):
    super(TranslateSubparserTest, self).testStdin()
    self.assertEquals(self.output, '(hello){10}(how\\ are\\ you)',
                      "with absence of filename and pattern, should translate from stdin")

class MatchSubparserTest(RegexezeTargetStringSubparserTest):
  '''
  Test case for testing the match subparser
  '''
  def setUp(self):
    super(MatchSubparserTest, self).setUp()
    self.function = regexeze.matchMain
    self.testFileOutput = ("Match successful\n\nAll groups:\n\tFull match: "
                           "hellohellohellohellohellohellohellohellohellohellohow "
                           "are you\n\tGroup 1: hello\n\tGroup 2: how are you\n\nNamed groups:")

  def testPattern(self):
    super(MatchSubparserTest, self).testPattern()
    self.assertEquals(self.output, 'Match successful\n\nAll groups:\n\tFull match: a\n\tGroup 1: a\n\nNamed groups:', "passing a pattern should trigger regexeze to match the target string against the pattern")

  def testFilename(self):
    super(MatchSubparserTest, self).testFilename()
    self.assertEquals(self.output, self.testFileOutput,
                      "passing filename should trigger regexeze to match the target string against the pattern in the file")

  def testStdin(self):
    super(MatchSubparserTest, self).testStdin()
    self.assertEquals(self.output, self.testFileOutput,
                      "in absence of filename and pattern, should match against from stdin")

#list of all test cases
TEST_CASES = [test_regex_parser_machine,\
              FileInputTestCase,\
              StdinTestCase,\
              TranslateSubparserTest,\
              MatchSubparserTest,\
              BasicSyntaxTestCase,\
              ValueKeywordSyntaxTestCase,\
              ModifierSyntaxTestCase,\
              CharacterClassSyntaxTestCase]

def runAllTests():
  #load test cases into a test suite
  testSuites = [unittest.TestLoader().loadTestsFromTestCase(testCase) for testCase in TEST_CASES]
  fullTestSuite = unittest.TestSuite(testSuites)

  #run tests
  unittest.TextTestRunner(verbosity=2).run(fullTestSuite)

if __name__ == '__main__':
  runAllTests()
