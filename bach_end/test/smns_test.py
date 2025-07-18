import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from chat import upload_image

if __name__ == '__main__':
    image_path = "/home/cgbc/code/nlpchat/test.png"
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    url = upload_image(image_bytes)
    print(url)
    
