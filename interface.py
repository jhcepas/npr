import sys
import re
from StringIO import StringIO
from signal import signal, SIGWINCH
from collections import deque

from logger import get_main_log

try:
    import curses
except ImportError: 
    NCURSES = False
else:
    NCURSES = True

class Screen(StringIO):
    # TAG USED TO CHANGE COLOR OF STRINGS AND SELECT WINDOW
    TAG = re.compile("@@(\d+)?,?(\d+):", re.MULTILINE)
    def __init__(self, windows):
        StringIO.__init__(self)
        self.windows = windows
        if NCURSES:
            # Resize window signal
            signal(SIGWINCH, self.sigwinch_handler) 

    def write(self, text):
        if NCURSES: 
            self.write_curses(text)
        else:
            self.write_normal(text)
    def write_normal(self, text):
        text = re.sub(self.TAG, "", text)
        self.stdout.write(text)

    def write_curses(self, text):
        formatstr = deque()
        for m in re.finditer(self.TAG, text):
            x1, x2  = m.span()
            cindex = int(m.groups()[1])
            windex = m.groups()[0]
            formatstr.append([x1, x2, cindex, windex])
        if not formatstr:
            formatstr.append([None, 0, 1, 1])

        if formatstr[0][1] == 0:
            stop, start, cindex, windex = formatstr.popleft()
            if windex is None:
                windex = 1
        else:
            stop, start, cindex, windex = None, 0, 1, 1

        while start is not None:
            if formatstr:
                next_stop, next_start, next_cindex, next_windex = formatstr.popleft()
            else:
                next_stop, next_start, next_cindex, next_windex = None, None, cindex, windex

            face = curses.color_pair(cindex)
            try:
                self.windows[int(windex)].addstr(text[start:next_stop], face)
            except curses.error: 
                self.windows[int(windex)].addstr("???")
            start = next_start
            stop = next_stop
            cindex = next_cindex
            if next_windex is not None:
                windex = next_windex
        for w in self.windows.values():
            w.refresh()

    def sigwinch_handler(self, n, frame):
        self.windows[0] = curses.initscr()
        h, w = self.windows[0].getmaxyx()
        curses.resizeterm(h, w)
        for w in self.windows.values():
            w.refresh()

def init_curses(main_scr):
    if not NCURSES or not main_scr:
        # curses disabled, no multi windows
        return None

    # Colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_WHITE)

    # Creates layout
    dbg_h = 40
    WIN = {}
    WIN[0] = main_scr
    h, w = WIN[0].getmaxyx()
    
    WIN[1] = curses.newwin(h-1, w/2, 1,1)
    WIN[2] = curses.newwin(h-dbg_h-1, (w/2)-1, 1, (w/2)+2)
    WIN[3] = curses.newwin(dbg_h-1, (w/2)-1, h-dbg_h+1, (w/2)+2)


    for i in xrange(1, len(WIN)):
        w = WIN[i]
        w.keypad(1)
        w.idlok(True)
        w.scrollok(True)
        w.border()
        w.refresh()
    return WIN

def app_wrapper(func, args):
    global NCURSES

    if args.disable_interface:
        NCURSES = False

    if NCURSES:
        curses.wrapper(main, func, args)
    else:
        main(None, func, args)

def main(main_screen, func, args):
    """ Init logging and Screen. Then call main function """

    # Do I use ncurses or basic terminal interface? 
    screen = Screen(init_curses(main_screen))

    # prints are handled by my Screen object
    screen.stdout = sys.stdout
    sys.stdout = screen

    # Start logger, pointing to the selected screen
    log = get_main_log(screen)

    # Call main function as lower thread
    if NCURSES:
        import threading
        import time
        t = threading.Thread(target=func, args=[args])
        t.daemon = True
        t.start()
        ln = 0           
        chars = "\\|/-\\|/-"
        while 1: 
            if ln >= len(chars):
                ln = 0
            screen.windows[0].addstr(0,0, chars[ln])
            screen.windows[0].refresh()
            time.sleep(0.2)
            ln += 1
    else:
        func(args)

