import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat import SymptomExtractor


if __name__ == '__main__':
    image_bytes = open("/home/cgbc/code/nlpchat/test.png", "rb").read()
    extractor = SymptomExtractor()
    result = extractor.chat_top("ct中的人有什么不良症状吗", image_bytes)
    print(result)