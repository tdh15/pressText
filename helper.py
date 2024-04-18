# helper.py

import re

def validate_preference_input(user_input: str):
    # Set of allowed characters
    allowed_chars = {'1', '2', '3', '4'}
    
    # Check if each character in the input is allowed
    if all(char in allowed_chars for char in user_input):
        # Return a sorted list of unique digits
        return sorted(set(user_input))
    else:
        return False
    
# Convert cleaned preference input to a preference array
# ['1', '2'] -> [1, 1, 0, 0]
def convert_to_preference_array(selected_digits: list):
    # Initialize preference array with all zeros
    preference_array = [0, 0, 0, 0]
    
    # Set the corresponding index to 1 for each selected digit
    for digit in selected_digits:
        preference_array[int(digit) - 1] = 1
    
    return preference_array
    
# Find the first sentence of the article.
# This works by skipping over live news bulletins and the location of the reporting,
# if either of those are provided.
def find_first_sentence(content: str):
    paragraphs = content.split('\n\n')  # Split content into paragraphs
    
    # Find the first paragraph that does not start with "Follow live AP coverage"
    first_paragraph = next((p for p in paragraphs if not p.startswith("Follow live AP coverage")), None)
    
    if first_paragraph:
        ap_em_dash_index = first_paragraph.find('(AP) —')
        
        if ap_em_dash_index != -1:
            # Return everything after the (AP) em dash
            first_sentence = first_paragraph[ap_em_dash_index + 6:].strip()
        else:
            # Return the whole paragrap
            first_sentence = first_paragraph.strip()
    else:
        first_sentence = ""  # No suitable paragraph found
    
    return first_sentence

# Split text into sentences (for deliverability of raptor responses)
def split_into_sentences(text: str):
    # Split text into sentences (. ? !)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
    # Remove empty strings
    sentences = [s for s in sentences if s]
    
    return sentences