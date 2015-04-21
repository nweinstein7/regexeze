Regexeze provides a high level, human-readable interface for regular expressions.

Features:
- no need for escaping
- readability - context and keywords help situate information

How it works:
Regular expressions consist of series of "expressions", which start with expr: and end with semicolon (;)
Always remember to end with a semicolon!
Quotes are recommended for all non keyword entries in expressions, but not required.

"expr:"
For example, this is a regular expression in regexeze:

  expr: "a";
    - this expression would match a single character "a"

  expr: ".";
    - this expression would match a single character "." (no need for escaping!)

"any_char:"
The any_char keyword matches any character when unmodified, or any character in a given set when modified:

  expr: any_char;
    - this matches any character, so any single character string would match this

  expr: any_char of "abc";
    - this matches any character in the set of a, b, or c, so "a", "b", and "c" would all match

  expr: any_char except "abc";
    - this matches any character except a, b, or c, so "d", "e", and "f" would all match, as well as many others!

  Other examples of any_char:
    - expr: any_char of "abc" or_of "def"; (matches any character in the set of a, b, c, d, e, or f)
    - expr: any_char from "a" to "c" or_from "h" to "k"; (matches any character in the range of a-c, or in the range of h-k)
    - expr: any_char except "abc" or_except "def"; (matches any character except those specified)

"for":
Expressions can also be modified to say how many times they should occur
  expr: "ab" for one_or_more;
    - this matches any string with the substring "ab" occurring one or more times, for example, "ab", "abab", or "ababab", but not "a"

  expr: "abc" for 2;
    - this matches any string with "abc" occurring exactly two times, so it only matches "abcabc"

  Other repetition modifiers:
    - for zero_or_more; (matches zero or more repetitions)
    - for zero_or_one (matches zero or one time)
    - for m up_to n (matches between m and n times)
       Examples:
         expr: "a" for 2 up_to 10;
         expr: "b" for 3 up_to infinity; (the infinity keyword does just what you'd expect)

Nesting:
Expressions can also be nested inside of other expressions

For example,
  expr: [ expr: "a"; expr: "b";] for 1;
    - this will match the string "ab" for exactly one repetition, so the only match is "ab"

  expr: [ expr: "a" for 2; expr: "b" for 3;] for 4;
    - this will match two a's and three b's repeated four times, so only "aabbbaabbbaabbbaabbb"

"or":
Nesting is particularly useful for or statements, which present two (or more) alternatives

For example:
  expr: "a" or "b";
    - this will match the string "a" or the string "b"

However, note that once an expression has an "or" in it, it cannot be followed by another expression, unless it is nested.
So, this is incorrect:
  expr: "a" or "b"; expr: "c"; [ERROR!]

However, if you want either a or b followed by c, do this:
  expr: [ expr: "a" or "b";]; expr: "c";
    - this will match a or b followed by c, so either "ac" or "bc"
