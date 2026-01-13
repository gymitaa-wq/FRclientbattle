"""Fix decision parsing bug in streamlined_simulation.py"""

with open('streamlined_simulation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace the buggy decision parsing logic
for i, line in enumerate(lines):
    if 'accepted = "ACCEPT" in decision_text.upper() and decision_text.upper().index("ACCEPT") < 100' in line:
        # Replace with better logic
        lines[i] = '    # Parse decision - look for explicit DECISION: ACCEPT or DECISION: REJECT\n'
        lines.insert(i+1, '    decision_upper = decision_text.upper()\n')
        lines.insert(i+2, '    \n')
        lines.insert(i+3, '    # Look for "DECISION: ACCEPT" or "DECISION: REJECT" pattern\n')
        lines.insert(i+4, '    decision_match = re.search(r\'DECISION[:\\s]*(\\w+)\', decision_upper)\n')
        lines.insert(i+5, '    \n')
        lines.insert(i+6, '    if decision_match:\n')
        lines.insert(i+7, '        decision_word = decision_match.group(1)\n')
        lines.insert(i+8, '        accepted = decision_word.startswith(\'ACCEPT\')\n')
        lines.insert(i+9, '    else:\n')
        lines.insert(i+10, '        # Fallback: check if ACCEPT appears before REJECT\n')
        lines.insert(i+11, '        accept_pos = decision_upper.find(\'ACCEPT\')\n')
        lines.insert(i+12, '        reject_pos = decision_upper.find(\'REJECT\')\n')
        lines.insert(i+13, '        \n')
        lines.insert(i+14, '        if accept_pos >= 0 and reject_pos >= 0:\n')
        lines.insert(i+15, '            accepted = accept_pos < reject_pos\n')
        lines.insert(i+16, '        elif accept_pos >= 0:\n')
        lines.insert(i+17, '            accepted = True\n')
        lines.insert(i+18, '        else:\n')
        lines.insert(i+19, '            accepted = False\n')
        break

with open('streamlined_simulation.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed decision parsing bug!")
print("Now correctly identifies DECISION: ACCEPT vs DECISION: REJECT")
print("Streamlit will auto-reload")
