#!/usr/bin/python
# CODE ANALYSER written by Antoine Stempfer #
# This script is used to help students of Epitech to check their c files #

import sys
import os
import re

class colors:
    clear = '\033[0;74m'
    error = '\033[1;31m'
    good = '\033[0;32m'
    warning = '\033[1;33m'
    bold = '\033[1m'

def log(message, color=colors.clear):
    print(color + message + colors.clear);

def log_error(error_type, location="in file", advice=None, line=None):
    log("\n/!\\ AN ERROR HAS BEEN FOUND /!\\", colors.error)
    log("Error Details:")
    log("   Error type: %s" % error_type)
    log("   Error location: %s" % location)
    if line is not None:
        log("   |-> Line: %s " % line[:-1])
    if advice is not None:
        log("   Advice: " + advice)
    log("--------------------------------\n")
    global error_count
    error_count += 1    

def open_source_file(path):
    if not os.path.isfile(path):
        print("Fatal: the provided file does not exist")
        return None
    if not path.endswith(".c"):
        log_error("Illegal file extension", "File name", "Rename file to <file name>.c")
        return None
    f = open(path)
    return f

def parse_tabs(line):
    while "\t" in line:
        line = line.replace("\t", " " * (8 - line.index("\t") % 8), 1)
    return line

def scan_file(f):
    unparsed_lines = [l for l in f]
    lines = [parse_tabs(l) for l in unparsed_lines]
    check_header(lines)
    line_number = 9
    function_count = 0
    identation = 0
    while line_number < len(lines):
        line = lines[line_number]
        if len(unparsed_lines[line_number]) > 80:
            log_error("Illegal line length (> 80)", "line %i" % (line_number + 1), "Rename your variables with shorter names or refactor your expression", line)
        if line.endswith(" \n"):
            log_error("White space at the end of a line", "line %i" % (line_number + 1), "Remove the whitespace", line)
        if re.match("^(\w+\s*){2,}\(([^!@#$+%^]+)?\)\s*(?!;)", line):
            function_count += 1 
            if "{" in line:
                log_error("Illegal bracket position", "line %i" % (line_number + 1), "Place the bracket on the next line", line)
            else:
                check_method(lines, line_number + 1)
            if function_count > 5:
                log_error("Illegal number of functions (> 5)", "line %i (whole function)" % (line_number + 1), "Remove or merge some functions", line)
        if not line.lstrip().startswith("#"):
            if re.match(".*(?<=(\w|\)|}))(=|<|>|<=|>=|\+|-|/|%|\+=|-=|/=|\*=|%=|\|\||&&|==|!=|\^|>>|<<)(?=(\w|\s|\*|\(|{|(-(\w|\(|\*))))", line):
                log_error("Missing white space before operator/comparator", "line %i" % (line_number + 1), "Add a space before the operator/comparator", line)
            if re.match(".*(?<=(\w|\)))\s*(=|<|>|<=|>=|\+|-|/|%|\+=|-=|/=|\*=|%=|\|\||&&|==|!=|\^|>>|<<)(?=(\w|\(|\*|{|(-(\w|\(|\*))))", line):
                log_error("Missing white space after operator/comparator", "line %i" % (line_number + 1), "Add a space after the operator/comparator", line)
        if "{" in lines[line_number - 1]:
            identation += 2
        if "}" in line:
            identation -= 2
        if re.match("^\s*((else if|if|while|for)(\s+|\()|else\s*)", lines[line_number - 1]):
            identation += 2
        else:
            i = 2
            while re.match("^\s*((else if|if|while|for)(\s+|\()|else\s*)", lines[line_number - i]) and not "{" in lines[line_number - i] and not "{" in lines[line_number - i + 1]:
                i += 1;
                identation -= 2
        if "}" in lines[line_number - 1]:
            identation -= 2
        if identation < 0:
            identation = 0
        if line.strip() is not "":
            spaces = len(line) - len(line.lstrip())
            if not spaces is identation:
                log_error("Illegal identation (expected %i spaces)" % identation, "line %i" % (line_number + 1), "Fix your identation with C-c C-q or use Tab", line)
                identation = spaces
        else:
            if line_number > 0 and lines[line_number - 1].strip() is "":
                log_error("Illegal empty line", "line %i" % (line_number + 1), "Remove this empty line")
        line_number += 1
        
def check_method(lines, starting_line):
    if not lines[starting_line].endswith("{\n"):
        log_error("Illegal function syntax", "line %i" % starting_line, "This line should only contain the opening bracket", lines[starting_line])
    if starting_line > 1 and lines[starting_line - 2].strip() is not "":
        log_error("Missing empty line", "line %i" % starting_line - 1, "There should be an empty line before the start of your function", lines[starting_line - 1])
    brackets_to_close = 1
    initializing_vars = True
    line_index = starting_line
    lines_count = 0
    alignement = re.search("^((unsigned|signed|static)?\s+)?(\w+)(\*+)?\s+(?=\w|\*)", lines[line_index - 1]).end()
    if alignement % 8 is not 0:
        log_error("Illegal function name alignement", "line %i" % (starting_line), "Use Alt-i to align your function name properly", lines[starting_line - 1])
    while not brackets_to_close is 0:
        line_index += 1
        lines_count += 1
        line = lines[line_index]
        if "{" in line:
            if line.strip() is not "{":
                log_error("Illegal bracket postition", "line %i" % (line_index + 1), "Brackets should be on their own lines", line)
            brackets_to_close += 1
        elif "}" in line:
            if line.strip() is not "}":
                log_error("Illegal bracket postition", "line %i" % (line_index + 1), "Brackets should be on their own lines", line)
            brackets_to_close -= 1
        if re.match("^(\s+\w+)?\s*\w+\*?\s+\*?\w+\s*=", line):
            if initializing_vars:
                log_error("Illegal variable initialization", "line %i" % (line_index + 1), "Initialize this variable in a separate line from it's declaration", line)
            else:
                log_error("Illegal variable declaration", "line %i" % (line_index + 1), "Declare this variable before executing commands in this function", line)
        if initializing_vars:
            if line.strip() == "":
                initializing_vars = False
            elif not re.match("^(\s+\w+)?\s*\w+\*?\s+\*?\w+(\[.*\])?;", line):
                initializing_vars = False
                if not lines_count == 1:
                    log_error("Missing empty line", "line %i" % (line_index + 1), "Add an empty line after you're done declaring your variables", line)
            elif re.search("^((unsigned|signed)?\s+)?(\w+)(\*+)?\s+(?=\w|\*)", line).end() != alignement:
                log_error("Illegal variable declaration alignement", "line %i" % (line_index + 1), "Use alt-i to correct your alignement", line)    
        else:
            if re.match("^(\s+\w+)?\s*\w+\*?\s+\*?\w+(\[.*\])?;", line) and not re.match("^\s+?return", line) and not "=" in line:
                log_error("Illegal variable declaration", "line %i" % (line_index + 1), "Declare this variable before executing commands in this method", line)
            elif line.strip() is "":
                log_error("Illegal empty line", "line %i" % (line_index + 1), "Remove this empty line", line)
            elif re.match("^\s+return(\s*|;|\()", line):
                if re.match("^\s*return\(", line):
                    log_error("Missing whitespace", "line %i" % (line_index + 1), "Add an empty space in between \"return\" and \"(\"", line)
                if re.match("^\s*return\s+\w", line):
                    log_error("Missing surrounding parenthesis", "line %i" % (line_index + 1), "Add parenthesis before and after your value", line)
            elif re.match("^\s*(else if|if|while)\(", line):
                log_error("Missing whitespace", "line %i" % (line_index + 1), "Add a white space between your flow control keyword and it's following parenthesis", line)
            elif re.match("^\s*(for|switch)\s*\(", line):
                log_error("Illegal C keyword", "line %i" % (line_index + 1), "Remove the incorrect keywords (for, switch, ...)", line);
    if line_index + 1 < len(lines) and not lines[line_index + 1].strip() is "":
        log_error("Missing empty line", "line %i" % (line_index + 1), "There should be an empty line after the end of your function", lines[line_index])        
    if lines_count - 1 > 25:
        log_error("Illegal number of lines in function (%i > 25)" % (lines_count - 1), "line %i" % (line_index - lines_count % 25), "Reduce number of lines, try using less variables for example")
    return line_index - starting_line
        
def check_header(lines):
    def log_header_error(line=1):
        log_error("Missing or invalid header", "line %s" % (line + 1), "Remove existing header and use C-c C-h in emacs to generate a new one")
    if len(lines) < 9:
        log_header_error()
    header_lines = lines[:9]
    if not header_lines[0].startswith("/*"):
        log_header_error(0)
    for l in range(0, 7):
        line = header_lines[l+1]
        if not line.startswith("**"):
            log_header_error(l + 1)
    if not header_lines[8].startswith("*/"):
        log_header_error(8)

def main():
    args = sys.argv
    if len(args) is 1:
        log("Fatal: You must specify a file to analyse")
        return
    global error_count
    error_count = 0
    log("\n/!\\ DISCLAIMER /!\\", colors.warning)
    log("Compile your files before using this utility")
    log("This utility isn't official and is only here to help you make less mistakes, DO NOT use it as a way to ensure your code is correct")
    log("USING THIS ON PROJECT SOURCE FILES IS CONSIDERED CHEATING, USE AT YOUR OWN RISK, I AM IN NO WAY RESPONSIBLE FOR YOUR USAGE OF THIS SCRIPT\n", colors.bold)
    f = open_source_file(args[1])
    if not f:
        return
    scan_file(f)
    log("Done checking %s" % args[1])
    if error_count > 0:
        log("There is a grand total of " + colors.error + "%i" % error_count + " error(s)" + colors.clear + " in your file")
    else:
        log("No error has been detected, however this script might not find everything so be carefull", colors.good)
    
if __name__ == "__main__":
    main()
