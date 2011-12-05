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
    # tags used to control color of strings and select buffer
    TAG = re.compile("@@(\d+)?,?(\d+):", re.MULTILINE)
    def __init__(self, windows):
        StringIO.__init__(self)
        self.windows = windows
        self.pos = {}
        if NCURSES:
            for w in windows:
                self.pos[w] = [0, 0]

    def scroll(self, win, vt, hz=0):
        line, col = self.pos[win]

        hz_pos = col + hz
        if hz_pos < 0: 
            hz_pos = 0
        elif hz_pos >= 1000:
            hz_pos = 999

        vt_pos = line + vt
        if vt_pos < 0:
            vt_pos = 0
        elif vt_pos >= 1000:
            vt_pos = 1000 - 1

        if line != vt_pos or col != hz_pos:
            self.pos[win] = [vt_pos, hz_pos]
            self.refresh()

    def scroll_to(self, win, vt, hz=0):
        line, col = self.pos[win]

        hz_pos = hz
        if hz_pos < 0: 
            hz_pos = 0
        elif hz_pos >= 1000:
            hz_pos = 999

        vt_pos = vt
        if vt_pos < 0:
            vt_pos = 0
        elif vt_pos >= 1000:
            vt_pos = 1000 - 1

        if line != vt_pos or col != hz_pos:
            self.pos[win] = [vt_pos, hz_pos]
            self.refresh()

    def refresh(self):
        for windex, (win, dim) in self.windows.iteritems():
            h, w, sy, sx = dim
            line, col = self.pos[windex]
            if h is not None: 
                win.touchwin()
                win.noutrefresh(line, col, sy+1, sx+1, sy+h-2, sx+w-2)
            else: 
                win.noutrefresh()
        curses.doupdate()

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

    def resize_screen(self, s, frame):

        import sys,fcntl,termios,struct 
        data = fcntl.ioctl(self.stdout.fileno(), termios.TIOCGWINSZ, '1234') 
        h, w = struct.unpack('hh', data) 

        win = self.windows
        #main = curses.initscr()
        #h, w = main.getmaxyx()
        #win[0] = (main, (None, None, 0, 0))
        #curses.resizeterm(h, w)

        win[0][0].resize(h, w)
        win[0][0].clear()
        info_win, error_win, debug_win = setup_layout(h, w)
        win[1][1] = info_win
        win[2][1] = error_win
        win[3][1] = debug_win
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
     
    WIN[1] = [curses.newpad(5000, 1000), info_win]
    WIN[2] = [curses.newpad(5000, 1000), error_win]
    WIN[3] = [curses.newpad(5000, 1000), debug_win]
     

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
        cbuff = 1
        while 1: 
            mwin = screen.windows[0][0]
            key = mwin.getch()
            mwin.addstr(0, 0, "%s (%s) (%s)" %(key, screen.pos, screen.windows) + " "*50)
            mwin.refresh()
            if key == 113: 
                break
            if key == 9: 
                cbuff += 1
                if cbuff>3: 
                    cbuff = 1
            elif key == curses.KEY_UP:
                screen.scroll(cbuff, -1)
            elif key == curses.KEY_DOWN:
                screen.scroll(cbuff, 1)
            elif key == curses.KEY_LEFT:
                screen.scroll(cbuff, 0, -1)
            elif key == curses.KEY_RIGHT:
                screen.scroll(cbuff, 0, 1)
            elif key == curses.KEY_NPAGE:
                screen.scroll(cbuff, 10)
            elif key == curses.KEY_PPAGE:
                screen.scroll(cbuff, -10)
            elif key == curses.KEY_END:
                screen.scroll_to(cbuff, 999, 0)
            elif key == curses.KEY_HOME:
                screen.scroll_to(cbuff, 0, 0)
            elif key == curses.KEY_RESIZE:
                screen.resize_screen(None, None)
            else:
                pass
            #screen.refresh()

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
    header = 4
    
    start_x = 0
    start_y = header
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
        info_win = [h, w1, start_y, start_x]
        error_win = [h1, w2, start_y, w1]
        debug_win = [h2, w2, h1, w1]
    else:
        #  ___
        # |___|
        # |___|
        # |___|
        h2a = h2/2 + h2%2 
        h2b = h2/2
        info_win = [h1, w, start_y, start_x]
        error_win = [h2a, w, h1, start_x]
        debug_win = [h2b, w, h1+h2a, start_x]
   
    return info_win, error_win, debug_win

