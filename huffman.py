import heapq
from collections import defaultdict

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    freq = defaultdict(int)
    for ch in text:
        freq[ch] += 1

    heap = [HuffmanNode(ch, f) for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left, merged.right = left, right
        heapq.heappush(heap, merged)

    return heap[0]

def build_codes(node, current="", codes={}):
    if node is None:
        return
    if node.char is not None:
        codes[node.char] = current
    build_codes(node.left, current + "0", codes)
    build_codes(node.right, current + "1", codes)
    return codes

def huffman_decode(encoded_text, huffman_codes):
    # Reverse the mapping: code -> character
    reverse_mapping = {code: char for char, code in huffman_codes.items()}
    
    decoded_text = ""
    current_code = ""
    
    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_mapping:
            decoded_text += reverse_mapping[current_code]
            current_code = ""
    
    return decoded_text


def compress(text):
    root = build_huffman_tree(text)
    codes = build_codes(root)
    encoded = ''.join(codes[ch] for ch in text)
    return encoded, root, codes

def decompress(encoded, root):
    result, node = "", root
    for bit in encoded:
        node = node.left if bit == "0" else node.right
        if node.char:
            result += node.char
            node = root
    return result
