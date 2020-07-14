import requests
import argparse
import time
from datetime import datetime


def get_block_number():
    try:
        x = requests.get('https://chainz.cryptoid.info/lcc/api.dws?q=getblockcount')
        block_num = int(x.text)
    except:
        return 0
    return block_num

    
def main(delta, loop):
    last_block = -1
    while True:
        try:
            block_num = get_block_number()
            if block_num == last_block:
                continue
            print(f'Block number: {block_num}')
            print(f'Date time: {datetime.now().isoformat()[0:19].replace("T", " ")}')
            print(f'LCC time: {float(block_num)/1152.0:.3f}\n')
            last_block = block_num
        except:
            pass
        if not loop:
            break
        time.sleep(delta) 

        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=f"LCC clock",
        epilog=f"Example: python3 clock-lcc.py --loop --delta seconds",
    )

    parser.add_argument(
        "--delta",
        "-d",
        required=False,
        default = 300,
        help=f'specify the delta time (300 sec by default).',
    )
    
    parser.add_argument(
        "--loop",
        "-l",
        action="store_true",
        default=False,
        help=f"Runs the script in a loop.",
    )

    args = parser.parse_args()
    main(int(args.delta), args.loop)
