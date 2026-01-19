"""Fix the import re issue properly"""

with open('streamlined_simulation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the mangled line 237
old_line = "    # Parse decision - look for explicit DECISION: ACCEPT or DECISION: REJECT\\r\\n    import re\\r\\n    decision_upper = decision_text.upper()"
new_lines = """    # Parse decision - look for explicit DECISION: ACCEPT or DECISION: REJECT
    import re
    decision_upper = decision_text.upper()"""

content = content.replace(old_line, new_lines)

# Also remove the duplicate "import re" on line 258
lines = content.split('\n')
new_lines_list = []
seen_import_re_in_function = False

for i, line in enumerate(lines):
    # Skip duplicate import re after we've seen one in the decision parsing section
    if 'import re' in line and i > 230 and i < 270:
        if seen_import_re_in_function:
            continue  # Skip duplicate
        else:
            seen_import_re_in_function = True
    new_lines_list.append(line)

content = '\n'.join(new_lines_list)

with open('streamlined_simulation.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed import re issue!")
print("Removed escaped characters and duplicate imports")
