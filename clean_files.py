import os
import re

def clean_python_file(filepath):
    """Remove comments and empty lines from a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        in_docstring = False
        docstring_char = None
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Handle docstrings
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2:
                    # Single line docstring, skip it
                    continue
                else:
                    # Multi-line docstring start
                    in_docstring = True
                    continue
            
            if in_docstring:
                if docstring_char in stripped:
                    in_docstring = False
                    docstring_char = None
                continue
            
            # Skip comments (but not inline comments that are part of code)
            if stripped.startswith('#'):
                continue
            
            # Keep the line, but remove inline comments carefully
            # Only remove comments that are clearly comments, not string literals
            comment_pos = line.find('#')
            if comment_pos > 0:
                # Check if # is inside a string
                before_hash = line[:comment_pos]
                single_quotes = before_hash.count("'") - before_hash.count("\\'")
                double_quotes = before_hash.count('"') - before_hash.count('\\"')
                
                # If quotes are balanced, # is likely a comment
                if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                    line = line[:comment_pos].rstrip() + '\n'
            
            cleaned_lines.append(line)
        
        # Write back the cleaned content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        print(f"Cleaned: {filepath}")
        return True
        
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")
        return False

# Process all Python files
def main():
    files_to_clean = [
        'main.py',
        'setup_demo.py', 
        'enhanced_tts.py',
        'dash.py',
        'test_tts.py',
        'config/config.py',
        'src/tts.py',
        'src/__init__.py',
        'config/__init__.py'
    ]
    
    processed = 0
    for filepath in files_to_clean:
        if os.path.exists(filepath):
            if clean_python_file(filepath):
                processed += 1
        else:
            print(f"File not found: {filepath}")
    
    print(f"\nProcessed {processed} files successfully!")

if __name__ == "__main__":
    main()