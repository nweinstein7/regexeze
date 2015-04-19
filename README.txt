BRAINSTORM
. (Dot):  any_char
^ (Carat): start
$ (Dollar sign): end
* (star): for zero_or_more
+ (plus): for one_or_more
? (question mark): for zero_or_one
{m} (repeat m times): for m
{m,n} (match for as few as m, as many as n times): for m up_to n
| (pipe): or
[] (brackets - class, match any of them): of (after any_char)
                                          also supports or, e.g. "expr: any_char of 'a' or 'b' or 'c';"
[a-c] (dash - range of chars): from 'a' until 'b' (after any_char)
[^5] (carat inside a class - complement of the class): except (after any_char)

KEYWORDS:
any_char
start
end
for
up_to
infinity
zero_or_more
one_or_more
zero_or_one
or
expr
decimal
non_decimal
whitespace
non_whitespace
alphanumeric
non_alphanumeric
except
of
from
until
greedy

ca*t
expr: 'c'; expr: 'a' for zero_or_more; expr: 't';

a[bcd]*b
expr: 'a', expr: any_char of 'bcd' for zero_or_more,
expr: 'a', expr: 'b' or 'c' or 'd' for zero_or_more, expr: 'b'

a[^bcd]*b
expr: 'a', expr: any_char except 'bcd' for zero_or_more, expr: b

home-?brew
expr: 'home', expr: '-' for zero_or_one, expr: 'brew'

Deterministic Finite State Machine for Validating Regexes of this Type:
>(NEW_EXPRESSION)
  ->expr-> (START_EXPRESSION)
    ->any_char-> (ANY_CHAR)
      -> (SET_PRIMARY_SYMBOL_ANY_CHAR) SYMBOL=.
        ->,-> (APPEND ${SYMBOL})
          -> (NEW_EXPRESSION)
        ->for-> (CHECK_NUMBER_OF_TIMES)
          ->zero_or_more-> (APPEND ${SYMBOL}*)
            -> (END_EXPRESSION)
              ->,-> (NEW_EXPRESSION)
              ->EOF-> (END_OF_EXPRESSIONS)
              ->not , or EOF-> (FAIL)
          ->one_or_more-> (APPEND ${SYMBOL}+)
            -> (END_EXPRESSION)
              ->,-> (NEW_EXPRESSION)
              ->EOF-> (END_OF_EXPRESSIONS)
              ->not , or EOF-> (FAIL)
          ->zero_or_one-> (APPEND ${SYMBOL}?)
            -> (END_EXPRESSION)
              ->,-> (NEW_EXPRESSION)
              ->EOF-> (END_OF_EXPRESSIONS)
              ->not , or EOF-> (FAIL)
          ->int-> (CHECK_NUMERICAL_NUMBER_OF_TIMES)
            ->up_to-> (CHECK_UPPER_LIMIT)
              ->int-> (APPEND ${SYMBOL}{m,n})
                -> (CHECK_GREEDY_NUMBER_OF_TIMES)
                  ->,-> (NEW_EXPRESSION)
                  ->for-> (GREEDY_NUMBER_OF_TIMES)
                    ->one_or_zero-> (APPEND ?)
                      -> (END_EXPRESSION)
                        ->,-> (NEW_EXPRESSION)
                        ->EOF-> (END_OF_EXPRESSIONS)
                        ->not , or EOF-> (FAIL)
                    ->not one_or_zero-> (FAIL)
                  ->EOF-> (END_OF_EXPRESSIONS)
              ->not int-> FAIL
            ->,-> (APPEND ${SYMBOL}{m})
            ->EOF-> (APPEND ${SYMBOL}{m})
              ->(END_OF_EXPRESSIONS)
            ->not , or up_to or EOF-> (FAIL)
          ->not int or zero_or_more or one_or_more or zero_or_one-> (FAIL)
        ->of-> (OPEN_CLASS)
          ->any string-> (SET_CLASS) SYMBOL=string
            -> (SET_SYMBOL_OPEN_CLASS) SYMBOL='['+${SYMBOL}
              ->,->(SET_SYMBOL_CLOSE_CLASS) SYMBOL=${SYMBOL}+']'
                -> (APPEND ${SYMBOL})
                  -> (NEW_EXPRESSION)
              ->or->(CLASS_OR)
                ->any string-> (ADD_TO_CLASS) SYMBOL=${SYMBOL}+string
                  -,->(SET_SYMBOL_CLOSE_CLASS) SYMBOL=${SYMBOL} + ']'
                    -> (APPEND ${SYMBOL}
                      -> (NEW_EXPRESSION)
                  ->or->(CLASS_OR)
                  ->for->(CHECK_NUMBER_OF_TIMES)
                  ->not ',' or 'or' or 'for' or EOF->(FAIL)
                ->EOF->(FAIL)
              ->for->(CHECK_NUMBER_OF_TIMES)
              ->EOF->(SET_SYMBOL_CLOSE_CLASS) SYMBOL=${SYMBOL}+']'
                -> (APPEND ${SYMBOL})
                  -> (END_OF_EXPRESSIONS)
              ->not ',' or 'or' or 'for' or EOF-> (FAIL)
          ->decimal
          ->non_decimal
          ->whitespace
          ->non_whitespace
          ->alphanumeric
          ->non_alphanumeric
        ->except-> (OPEN_COMPLEMENT_CLASS)
          ->any string-> (SET_COMPLEMENT_CLASS) SYMBOL=string
        ->else-> FAIL
  ->EOF-> (END_OF_EXPRESSIONS)
  ->not expr or EOF-> (FAIL)

NESTING
Nested expressions start with square brackets [
main parser goes into "nested" state
-- push into stack every time token == '['
-- pop from stack every time token == ']'
if token == ']' and stack == empty, leave nested state
Treat nested state just like plain_text state - put it in parentheses and modify it as necessary
'[' to anything other than expr is treated as plain text
Examples:
expr: [expr: hello; expr: hello; expr: hello;];
((hello)(hello)(hello))

-:-> (START_EXPRESSION)
  ->[-> (NEW_NESTED_EXPRESSION) parser stack: [
    ->expr-> (NESTED_EXPRESSION) child process token
      ->any token that is valid for child-> (NESTED_EXPRESSION) child process token
      ->EOF-> incomplete nesting exception
      ->[-> (NESTED_EXPRESSION) child process token parser stack: [[
      ->]-> if parser stack is empty, go to END_NESTED EXPRESSION
            else, back to NESTED_EXPRESSION child process token parser stack: [

expr: [expr: [expr: 'a';]]

expr: [expr: [expr: a for zero_or_more; expr: b for one_or_more;];];
(((a)*(b)+))

While in nested state, create a CHILD PARSER to whom you pass through each token
At end, take child parser's ret_val as expr

OR:
expr: 'a' or 'b';
(a|b)
expr: 'a' for zero_or_more or 'b' for zero_or_more;
(a)*|(b)* 

TODO:
1. Nesting
2. Or
3. Classes
  - typical classes (of)
  - complement classes (except)
  - range (from ... until)
  - escaping inside classes
  - or with classes (multiple items in class)
4. Special characters (alphanumeric, decimal, whitespace)
5. Start, end
6. Group names
7. Escaping in text
8. Documentation
9. Show error location is buggy :/ 
