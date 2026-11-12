# hand-checked against beat-by-beat contact sheets of the film (one entry per beat, 16 beats per verse)
_T={'c':COLOR,'s':SIL,'=':STRIPE,'.':DOT,'O':BIG,'p':POLKA,'-':0}
_V=["- - - - - - - - c c c c c c c -",
    "s s s s s s s s - - - c c c c c",
    "c c c c c c cs cs s s s s s s s s",
    "s cs cs cs s s cs c - - c cs c cs cs cs",
    "s s s s s s s s s s s s - - - -",
    "s s - - - s s s s s = s s s = s",
    "s = = = = = c - - = = s s s = =",
    "= s = = =s s s s= s = = = c c = c",
    "c = c c c = - - - s s = s = = =",
    "= - = = = = = = = - - = = = O= =",
    "= O - - = = = = . . = . - - - O",
    "= O O = = = O O. O. O. O. O. . . . .",
    ". . . . . =. O O. . O O O - - O O.",
    "O O. O. O. = = . = . = . . . . . .",
    "- - - . . s - - s . . s . . . .",
    ". . s . O. s s O O. c - - O O p O.",
    "s O. s . . p p p p p p p O cO cO O",
    "O O O c c c O c - - - - . . . s",
    "s . s s - c c c c c c c - - - -"]
for _v,_row in enumerate(_V):
    _e=_row.split(); assert len(_e)==16,(_v,len(_e))
    for _i,_x in enumerate(_e):
        mb[_v*16+_i]=sum(_T[ch] for ch in _x)
