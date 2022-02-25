import parsy
from parsy import whitespace, eof, any_char, regex, string

# Lexical Tokens
eol = string("\n")
question_prefix = string("Q:")
answer_prefix = string("A:")
lbrace = string("{")
rbrace = string("}")
paragraph_separator = eol.at_least(2) | whitespace + question_prefix | whitespace + answer_prefix
