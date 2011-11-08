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

def newwin(nlines, ncols, begin_y, begin_x):
    border = curses.newwin(nlines, ncols, begin_y, begin_x)
    border.border()
    
    #win = curses.newwin(nlines-2, ncols-2, begin_y+1, begin_x+1)
    pad = curses.newwin(1000, 1000)
    print pad
    return pad, border

class Screen(StringIO):
    # TAG USED TO CHANGE COLOR OF STRINGS AND SELECT WINDOW
    TAG = re.compile("@@(\d+)?,?(\d+):", re.MULTILINE)
    def __init__(self, windows):
        StringIO.__init__(self)
        self.windows = windows
        self.pos = {}
        for w in windows:
            self.pos[w] = [0, 0]

        if NCURSES:
            # Resize window signal
            signal(SIGWINCH, self.sigwinch_handler) 

    def scroll(self, win, alpha):
        try:
            line, col = self.pos[win]
        except:
            raise Exception(self.pos)

        pos = line + alpha
        if pos < 0:
            pos = 0
        elif pos >= 1000:
            pos = 1000 - 1

        if line != pos:
            self.pos[win][0] = pos
            self.refresh()


    def refresh(self):
        for windex, (win, dim) in self.windows.iteritems():
            h, w, sy, sx = dim
            line, col = self.pos[windex]
            if h is not None: 
                win.refresh(line, col, sy, sx, sy+h-1, sx+w-1)
            else: 
                win.refresh()
            #w.noutrefresh()
            #w.doupdate()

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
            win, dim = self.windows[int(windex)]
            try:
                win.addstr(text[start:next_stop], face)
            except curses.error: 
                win.addstr("???")
            start = next_start
            stop = next_stop
            cindex = next_cindex
            if next_windex is not None:
                windex = next_windex
        self.refresh()

    def sigwinch_handler(self, s, frame):
        curses.endwin()
        win = self.windows
        main = curses.initscr()
        h, w = main.getmaxyx()
        win[0] = (main, (None, None, 0, 0))

        curses.resizeterm(h, w)

        info_win, error_win, debug_win = setup_layout(h, w)
        win[0][0].addstr(str([h, w, "--", info_win, error_win, debug_win])+" "*50)
        win[0][0].refresh()
        win[1].resize(info_win[0], info_win[1])
        win[1].mvwin(info_win[2], info_win[3])
        
        win[2].resize(error_win[0], error_win[1])
        win[2].mvwin(error_win[2], error_win[3])

        win[3].resize(debug_win[0], debug_win[1])
        win[3].mvwin(debug_win[2], debug_win[3])

        
        self.refresh()


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

    WIN = {}
    main = main_scr
    h, w = main.getmaxyx()
    WIN[0] = (main, (None, None, 0, 0))

    # Creates layout
    info_win, error_win, debug_win = setup_layout(h, w)
     
    WIN[1] = (curses.newpad(1000, 1000), info_win)
    WIN[2] = (curses.newpad(1000, 1000), error_win)   
    WIN[3] = (curses.newpad(1000, 1000), debug_win)

   
    

    #WIN[1], WIN[11] = newwin(h-1, w/2, 1,1)
    #WIN[2], WIN[12] = newwin(h-dbg_h-1, (w/2)-1, 1, (w/2)+2)
    #WIN[3], WIN[13] = newwin(dbg_h-1, (w/2)-1, h-dbg_h+1, (w/2)+2)

    for w, dim in WIN.itervalues():
        #w = WIN[i]
        w.keypad(1)
        w.idlok(True)
        w.scrollok(True)
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
            mwin = screen.windows[0][0]
            key = mwin.getch()
            mwin.addstr(0, 0, "%s (%s)" %(key, screen.pos) + " "*50)
            mwin.refresh()
            if key == 113: 
                break
            elif key == curses.KEY_UP:
                screen.scroll(1, -1)
            elif key == curses.KEY_DOWN:
                screen.scroll(1, 1)
            elif key == curses.KEY_NPAGE:
                screen.scroll(1, 10)
            elif key == curses.KEY_PPAGE:
                screen.scroll(1, -10)
            elif key == curses.KEY_END:
                C.goto_end()
            elif key == curses.KEY_HOME:
                C.goto_start()
            else:
                screen.refresh()


        #while 1: 
        #    if ln >= len(chars):
        #        ln = 0
        #    #screen.windows[0].addstr(0,0, chars[ln])
        #    #screen.windows[0].refresh()
        #    time.sleep(0.2)
        #    ln += 1
    else:
        func(args)

def setup_layout(h, w):
    # Creates layout

    start_x = 2
    start_y = 2
    h -= start_y
    w -= start_x

    h1 = h/2 + h%2
    h2 = h/2 
    if w > 160:
        #  _______
        # |   |___|
        # |___|___|
        w1 = w/2 + w%2
        w2 = w/2 
        info_win = (h, w1, start_y, start_x)
        error_win = (h1, w2, start_y, w1)
        debug_win = (h2, w2, h1, w1)
    else:
        #  ___
        # |___|
        # |___|
        # |___|
        h2a = h2/2 + h2%2 
        h2b = h2/2
        info_win = (h1, w, start_y, start_x)
        error_win = (h2a, w, h1, start_x)
        debug_win = (h2b, w, h2a, start_x)
   
    return info_win, error_win, debug_win
