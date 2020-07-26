import sys
import requests
import argparse
import time
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, QTime, Qt


last_block = 0

class AppDemo(QWidget):

    def __init__(self, delta_time):
        super().__init__()
        self.resize(250, 150)
        layout = QVBoxLayout()
        fnt = QFont('Open Sans', 60, QFont.Bold)
        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setFont(fnt)
        layout.addWidget(self.lbl)
        self.setLayout(layout)
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(delta_time*1000) # update every delta_time seconds
        self.showTime()

 
    def showTime(self):
        global last_block
        currentTime = QTime.currentTime()
        block_num = get_block_number()
        if block_num == -1:
            return
        if block_num == last_block:
            return
        displayTxt = f'Block number: {block_num}\n'
        displayTxt += f"Date time: {currentTime.toString('hh:mm:ss')}\n"
        displayTxt += f'LCC time: {float(block_num)/1152.0:.6f}\n'
        
        date = float(block_num)/1152.0
        hora = int((date%1)*24.0)
        
        total_seconds = int((date%1)*86400)
        
        
        minutes = int((total_seconds - hora*3600)/60)
        seconds = total_seconds - hora*3600 - minutes*60
        displayTxt += f'LCC time: {hora:02.0f}:{minutes:02.0f}:{seconds:02.0f}\n'
        self.lbl.setText(displayTxt)
        last_block = block_num

 
def get_block_number():
    try:
        x = requests.get('https://chainz.cryptoid.info/lcc/api.dws?q=getblockcount')
        block_num = int(x.text)
    except:
        return -1
    return block_num


def main(delta, loop):
    delta_time = delta
    app = QApplication(sys.argv)
    demo = AppDemo(delta)
    demo.show()
    app.exit(app.exec_())
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=f"LCC clock",
        epilog=f"Example: python3 qt_clock-lcc.py --loop --delta seconds",
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
