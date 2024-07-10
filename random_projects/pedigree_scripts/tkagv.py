#!/usr/bin/env python3
import sys
import pedigree
import agv

def tkmain(p, a):
    import tkinter
    root = tkinter.Tk()
    root.title("Schilduil - Kinship")

    frame = tkinter.Frame(root, padx=2, pady=2)
    frame.pack(fill=tkinter.BOTH, expand=tkinter.YES, side=tkinter.LEFT)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    xsb = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
    xsb.grid(row=1, column=0, sticky=tkinter.E+tkinter.W)

    ysb = tkinter.Scrollbar(frame)
    ysb.grid(row=0, column=1, sticky=tkinter.N+tkinter.S)

    canvas = tkinter.Canvas(frame, xscrollcommand=xsb.set, yscrollcommand=ysb.set, width=600, height=400)
    canvas.grid(row=0, column=0, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

    ysb.config(command=canvas.yview)
    xsb.config(command=canvas.xview)

    bl = tkinter.Canvas(frame, bg='#FF0000', width=10, height=10)
    bl.grid(row=1, column=1, sticky=tkinter.S+tkinter.E)

    list = p.getIds()
    padding = 0
    sf = tkinter.Frame(canvas)
    for row in range(len(list) + 1):
        for col in range(len(list) + 1):
            if row == 0:
                if col == 0:
                    th = tkinter.Label(sf, text="AGV")
                    th.grid(row=row, column=col, padx=padding, pady=padding)
                else:
                    th = tkinter.Label(sf, text=list[col - 1])
                    th.grid(row=row, column=col, padx=padding, pady=padding)
            elif col == 0:
                th = tkinter.Label(sf, text=list[row -1])
                th.grid(row=row, column=col, padx=padding, pady=padding)
            else:
                agv = a.getPcagv(list[col - 1], list[row - 1])
                #n = tkinter.DoubleVar()
                #n.set(agv)
                if col == row:
                    tc = tkinter.Entry(sf, width=10, relief=tkinter.FLAT, borderwidth=2, bg='#000000', fg='#FFFFFF') # , textvariable=n
                else:
                    bg="#FF%02xFF" % (int((1-agv)*255))
                    tc = tkinter.Entry(sf, width=10, relief=tkinter.FLAT, borderwidth=2, bg=bg) # , textvariable=n
                tc.insert(0, "%.4f" % (agv))
                tc.grid(row=row, column=col, padx=padding, pady=padding)
    # First pack, then add the frame to the canvas so it scrolls
    # Also do update() so the width & height are correct
    sf.pack()
    sf.update()
    canvas.create_window((0,0), window=sf, anchor=tkinter.N+tkinter.W)
    #print("subframe=(%s,%s)" % (sf.winfo_width(), sf.winfo_height()))
    #print("scrollregion=(%s,%s,%s,%s)" % canvas.bbox(tkinter.ALL))
    canvas.config(scrollregion=canvas.bbox(tkinter.ALL)) # Does not seem to do anything
    root.mainloop()

if __name__ == '__main__':
    a = agv.PcagvMatrix()
    p = pedigree.testPedigree()
    if len(sys.argv) > 1:
        p = pedigree.FilteredPedigree()
        p.importFile(sys.argv[1], instruction=a.parseline)
        if len(p.getIds()) == 0:
            p.show(p.getAllIds())
    a.processPedigree(p)
    tkmain(p, a)

