#Regexeze 
A high level, human-readable interface for regular expressions.

##Features:
- (virtually) no need for escaping
- context and keywords help situate information, without overloading symbols
- no more inordinate weight afforded to seemingly inconsequential, small characters
- descriptive keywords help jog memory
- support for expanded layout, for even easier comprehension

##How it works:
Regular expressions consist of series of "expressions", which start with the keyword "expr" (pronounced "exper"?) followed by a colon. They end with semicolon (;).

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

###"any_char:"
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
* Let's say you want to match tags in a string, for example, "<sometag>This is html</sometag>".  You might do this:

```
expr: "<"; expr: any_char for one_or_more; expr: ">";
```

However, since the above expression is, by default greedy, it won't match the individual tags "<sometag>" and "</sometag>". Rather, it will match the whole string.  In its greediness, it ignores the first ">" looking for the second.  By making it *not_greedy*, we match only the first tag.

```
expr: "<"; expr: any_char for one_or_more not_greedy; expr: ">";
```

This will match "<sometag>" alone.

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

Once an expression has an *or* in it, it cannot be followed by another expression at the same level of nesting. Similarly, expressions with *or* in them cannot follow other expressions at the same level of nesting. This is to avoid confusin about the "reach" of the or.  So, the following are incorrect:

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

###"start_of_string" and "end_of_string"
The keywords *start_of_string* and *end_of_string* indicate that the expression will only match directly at the start or end.

For example:

*The following expression will match "Once upon a time" but not "Many stories begin with "Once upon a time"":

```
expr: start_of_string; expr: "Once upon a time";
```

*The following expression will match "happily ever after" but not "happily ever after til the end of time"

```
expr: "happily ever after"; expr: end_of_string;
```

>NOTE 8: *start_of_string* and *end_of_string* cannot be modified for number of repetitions, so the following will not work:

```
expr: start_of_string for zero_or_one; #ERROR
```

###Other special keywords
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
