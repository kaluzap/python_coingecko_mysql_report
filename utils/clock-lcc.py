import requests
import argparse
import time


def main(delta, loop):
    
    while True:
        try:
            x = requests.get('https://chainz.cryptoid.info/lcc/api.dws?q=getblockcount')
            block_num = int(x.text)
            print(f'Block number: {block_num}')
            print(f'LCC time: {float(block_num)/1152.0:.3f}\n')
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
