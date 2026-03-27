import math
import sys
import json

def main(**kwargs):
    start_x = kwargs.get('start_x', 0)
    start_y = kwargs.get('start_y', 0)
    end_x = kwargs.get('end_x', 0)
    end_y = kwargs.get('end_y', 0)
    
    dx = math.fabs(end_x - start_x)
    dy = math.fabs(end_y - start_y)
    
    if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
        print("YES")
    else:
        print("NO")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
        main(**params)