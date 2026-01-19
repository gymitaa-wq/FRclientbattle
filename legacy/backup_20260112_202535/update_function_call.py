"""Update extract_final_products call to pass callModel"""

with open('run_streamlined_simulation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update the function call to pass callModel
old_call = '''    # Extract final products if accepted
    final_products = extract_final_products(
        final_iteration['proposal'],
        final_iteration['accepted']
    )'''

new_call = '''    # Extract final products if accepted (using LLM, not regex!)
    final_products = extract_final_products(
        final_iteration['proposal'],
        final_iteration['accepted'],
        callModel=callModel
    )'''

content = content.replace(old_call, new_call)

with open('run_streamlined_simulation.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated function call to pass callModel")
print("LLM-based extraction is now fully integrated!")
