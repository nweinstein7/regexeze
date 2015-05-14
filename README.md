#Regexeze 
A high level, human-readable interface for regular expressions.

##Features:
- (virtually) no need for escaping
- context and keywords help situate information, without overloading symbols
- no more inordinate weight afforded to seemingly inconsequential, small characters
- descriptive keywords help jog memory
- support for expanded layout, for even easier comprehension

##How it works:
###Usage:
- Parse regexes from stdin:
```
python regexeze.py
```

- Parse regexes from a string:
```
python regexeze -i "expr: 'a';"
```

- Parse regexes from file:
```
python regexeze -f test_file.txt
```

- Get usage help:
```
python regexeze.py --help
usage: regexeze.py [-h] [-i INPUT_STRING | -f FILENAME]

Parses a regular expression in regexeze. If no input string or file is
supplied, parses from command line.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_STRING, --input-string INPUT_STRING
                        A string of input
  -f FILENAME, --filename FILENAME
                        A file (or path to file) containing a regex
```

###Syntax:
Regular expressions consist of series of "expressions", which start with the keyword "expr" (pronounced "exper"?) and typically followed by a colon. They end with semicolon (;).

>NOTE 1: Always remember to end with a semicolon!

>NOTE 2: Quotes (either double (") or single (')) are recommended for all non-keyword entries in expressions, but not required.

##Overview of keywords:
###"expr:"
expr (see pronunciation suggestion above) starts every expression in regexeze followed by a colon.

For example:

* match the string "a"

```
expr: "a";
```


* match the string "."

```
expr: ".";
```

* match the string "ab"

```
expr: "ab";
```

* another way to match the string "ab" (by stringing together two expressions)

```
expr: "a"; expr: "b";
```

###"any_char":
The *any_char* keyword matches any character when unmodified, or any character in a given set when modified:

For example:

* match any single character, for example "a", "g", "1", "&", etc.

```
expr: any_char;
```

* match any character in the set of "a", "b", or "c", so "a", "b", and "c" would all match, and nothing else

``` 
expr: any_char of "abc";
```

* match any_char except a, b, or c, so "d", "j", "6", "#" would all match

```
expr: any_char except "abc";
```

* match any_char in the character range of a to c

```
expr: any_char from "a" to "c";
```

As you saw in the above examples, any_char supports these modifiers:
* *of*: indicates a set of characters
* *except*: indicates a set *complement*
* *from...to*: indicates a range of characters

These can also be strung together using special *or* keywords:
* *or_of*: indicates a continuation of a set of characters. For example, the following code matches "a", "b", "c", "d", "e", or "f"

```
expr: any_char of "abc" or_of "def";
```

* *or_from*: indicates another range. For example:

```
expr: any_char from "a" to "c" or_from "x" to "z";
```

* *or_except*: indicates a continuation of a complement set. For example:

```
expr: any_char except "abc" or_except "def" or_except "ghi";
```

>NOTE 3: or_from and or_of can be used interchangeably after "of" and "from". or_except can only be used after except. 

>NOTE 4: All special *or* keywords can be strung together infinitely.

###"for":
The *for* keyword modifies how many times an expression should occur.

For example:
* match any string with "a" followed by "ab" one or more times, for example, "aab", "aabab", or "aababab", but not "a"

```
expr: "a"; expr: "ab" for one_or_more;
```

* match any string with "abc" occurring exactly two times, so only matches "abcabc"

```
expr: "abc" for 2;
```

*for* supports this list of modifiers:
* *zero_or_more*: matches zero or more repetitions. For example:

```
expr: "a" for zero_or_more;
```

* *zero_or_one*: matches zero or one time - useful for "optional" characters, such as a hyphen between sections of a phone number. For example:

```
expr: "a" for zero_or_one;
```

* *m up_to n*: matches between m and n times. For example:

```
expr: "a" for 2 up_to 10;
```

* *m up_to infinity*: matches starting with m times, with no upper bound. For example:

```
expr: "b" for 3 up_to infinity;
```

###"greedy" and "not_greedy":
After indicating the number of repetitions using *for*, you can indicate whether that modifier is *greedy* or *not_greedy*. This determines whether it will try to match the "most possible" (greedy) or "fewest possible" (not greedy). You can specify *greedy* or *not_greedy* after any for statement, though greedy is the default for all.

For example:
* Let's say you want to match tags in a string, for example, "\<sometag\>This is html\</sometag\>".  You might do this:

```
expr: "<"; expr: any_char for one_or_more; expr: ">";
```

However, since the above expression is, by default greedy, it won't match the individual tags "\<sometag\>" and "\</sometag\>". Rather, it will match the whole string.  In its greediness, it ignores the first ">" looking for the second.  By making it *not_greedy*, we match only the first tag.

```
expr: "<"; expr: any_char for one_or_more not_greedy; expr: ">";
```

This will match "\<sometag\>" alone.

* This expression will match "aa" not "aaa":

```
expr: "a" for 2 up_to 3 not_greedy;
```

###Nesting:
Expressions can also be nested inside of other expressions. Nesting is indicated by square brackets ([]).

For example:
* match the string "ab" for exactly one repetition

```
expr: [ expr: "a"; expr: "b";] for 1;
```

* match the string "aabbbaabbbaabbbaabbb"

```
expr: [ expr: "a" for 2; expr: "b" for 3;] for 4;
```

>NOTE 5: Always remember to close brackets, and semi-colon rules still apply

>NOTE 6: Inside nested expressions, you can string together several expressions, except for the special case of or expressions (see below). Nested expressions can then be modified like other expressions.

###"or":
Nesting is particularly useful for *or* statements, which present two (or more) alternatives. 

>NOTE 7: Don't confuse *or* with *or_of*, *or_except*, and *or_from* - remember, those only apply after any_char to specify a set of characters.

For example:
* match the string "a" or the string "b"

```
expr: "a" or "b";
```

Once an expression has an *or* in it, it cannot be followed by another expression at the same level of nesting. Similarly, expressions with *or* in them cannot follow other expressions at the same level of nesting. This is to avoid confusion about the "reach" of the or.  So, the following are incorrect:

```
expr: "a" or "b"; expr: "c"; #ERROR
expr: "a"; expr: "b" or "c"; #ERROR
```

If you want either "a" or "b" followed by "c", do this:

```
expr: [ expr: "a" or "b";]; expr: "c";
```

For "a" followed by "b" or "c", do this:

```
expr: "a"; expr: [ expr: "b" or "c";];
```

###"start_of_string" and "end_of_string":
The keywords *start_of_string* and *end_of_string* indicate that the expression will only match directly at the start or end.

For example:

* The following expression will match "Once upon a time" but not "Many stories begin with "Once upon a time"":

```
expr: start_of_string; expr: "Once upon a time";
```

* The following expression will match "happily ever after" but not "happily ever after til the end of time"

```
expr: "happily ever after"; expr: end_of_string;
```

>NOTE 8: *start_of_string* and *end_of_string* cannot be modified for number of repetitions, so the following will not work:

```
expr: start_of_string for zero_or_one; #ERROR
```

###"set_flags:"
Regexeze allows the user to set all the same flags as the Python re module, with the exception of
VERBOSE, because regexeze is inherently "verbose".

To set flags, you replace "expr:" with "set_flags:"

For example:

```
set_flags: ignore_case, multiline; expr: 'a'; expr: end_of_string;
```

A *set_flags* expression can go anywhere a standard *expr* expression would go. As you can see in the above example, flags are separated by commas and end with a semicolon.  You can set flags as many times as you want in an expression, but they only count once. 

A *set_flags* expression does not "count" as a standard expression, and therefore can follow or be followed by an expression containing *or*. For example, the following will match 'a', 'b', 'A', or 'B':

```
expr: 'a' or 'b'; set_flags: ignore_case; # valid regexeze expression
```

List of flags:
* *ignore_case*: case-insensitive matching, so "A" and "a" are identical
* *locale*: if set, the keyword "alphanumeric" (see below)  will depend on whichever locale you are in - different places have different definitions of alphanumeric
* *multiline*: start_of_string and end_of_string will match at the end of *lines*, not just at the start and end of strings
* *any_char_all*: any_char matches everything *including* newlines (without this specified, any_char does not match newlines)
* *unicode*: similar to locale, this will make certain special keywords depend on the unicode set

###Other special keywords:
There are several other keywords/especial characters that can be used in both character sets and standard expressions.
* *new_line*: matches a newline character. For example, the following expression matches "a\nb", where \n is a newline:

```
expr: "a"; expr: new_line; expr: "b";
```

* *tab*: matches a tab character (\t). The following expression matches an optional tab:

```
expr: tab for zero_or_one;
```

* *carriage_return*: matches a carriage return character (\r). The following expression matches a carriage return or a newline:

```
expr: any_char of carriage_return or_of new_line;
```

* *page_break*: matches a pagebreak character (\f). For example, the following expression matches "\f", where \f is a pagebreak:

```
expr: page_break;
```

* *vertical_space*: matches a vertical space character (\v)

* *whitespace*: matches any whitespace character, such as \n, \r, \f, \t, or \v

* *non_whitespace*: matches anything but a whitespace character. Is equivalent to:

```
expr: any_char except whitespace;
```

* *digit*: matches any number character (0-9)

* *non_digit*: matches any non-number character

* *alphanumeric*: matches any alphanumeric (number or letter) character

* *non_alphanumeric*: matches any non-alphanumeric character

###Comments:
Regexeze supports comments with the pound sign (#). All text on the same line after a "#" will not be parsed.

For example:
```
expr: 'a'; #this is a comment
expr: 'b'; #this is another comment
```

>NOTE 9: Careful to put "#"'s in quotes when using them in expressions. Otherwise, the parser will think you are trying to make a comment, and throw an incomplete expression error.
```
expr: #; #ERROR
```
>Putting the "#" symbol in quotes will get the desired effect:
```
expr: "#"; #CORRECT: matches a single "#" symbol
```

###Group Names:
Nested expressions can be *named*.
This facilitates easier retrieval of the match of that nested expression.

For example, the following creates a group called areaCode:

```
expr: [ name: areaCode; expr: digit for 3; ];
```

No two nested groups can have the same name:

```
expr: [ name: areaCode; expr: digit for 3;];
expr: [ name: areaCode; expr: any_char from '0' to '9' for 3;]; #ERROR: two nested expressions with same group name
```

Expressions also cannot share names with regexeze keywords, to avoid confusion:
```
expr: [ name: any_char; expr: any_char; ]; #ERROR: group names can't be the same as certain regexeze keywords
```

Group names also allow for group *references*. Naming an expression group adds that name to the "namespace" of the expression, and from then on, it can be used as a keyword.  For example:

```
expr: [ name: quote; expr: any_char of "'" or_of '"';];
expr: alphanumeric for 0 up_to 10 not_greedy;
expr: quote;
```

"expr: quote" will match whatever the expr named quote matched, which in this case might be useful if you're not sure whether you'll get a single or double quotation mark. So, the above expression would match 'hello' or "hello".
