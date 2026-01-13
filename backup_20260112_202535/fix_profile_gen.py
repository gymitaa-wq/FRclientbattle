"""Fix all nested f-string issues in profile_generator.py"""

with open('profile_generator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix line 182 (email 43)
for i, line in enumerate(lines):
    if 'Email 43 (Client to Self - After Reddit)' in line and "{'Oh no.'" in line:
        # Replace with pre-computed values
        lines[i-1] = '    reddit_sentiment = "overpriced and commission-driven" if skepticism > 6 else "mixed reviews - some good, some bad"\n'
        lines[i] = '    reddit_reaction = \\'Oh no.\\' if skepticism > 6 else \\'Interesting.\\'\n'
        lines.insert(i+1, '    reddit_conclusion = "Now I\\'m really skeptical." if skepticism > 6 else "Need to be careful."\n')
        lines.insert(i+2, '    emails.append(f"Email 43 (Client to Self - After Reddit):\\\\n{reddit_reaction} Reddit says advisors are {reddit_sentiment}. {reddit_conclusion}")\n')
        break

# Find and fix line with "I don't know" (email 46)
for i, line in enumerate(lines):
    if 'Email 46' in line and "{'I don\\'t know.'" in line:
        lines.insert(i, '    email46_reaction = "I don\\'t know." if skepticism > 6 else "This is confusing."\n')
        lines[i+1] = '    emails.append(f"Email 46 (Client to {\\'Spouse\\' if has_spouse else \\'Self\\'}):\\\\n{email46_reaction} The advisor made it sound good, but the internet says it\\'s a bad deal.")\n'
        break

# Write fixed version
with open('profile_generator.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ Fixed all nested f-string issues in profile_generator.py")
