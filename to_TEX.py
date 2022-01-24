import collections
import json
import os

_MINIROW = collections.namedtuple('Minirow', 'D, CP, EP')
_SUBTYPE_FNS = {  # wte: Wikitext element (str or single-item dict)
    'tmpl': lambda wte: wte[0][0],
    'custom_tag': lambda wte: wte,
    'unparseable': lambda wte: None,
}
_PSV_PSN_CATEGORIES = {
    '0': '0 (pre-chapter)',
    str('תתת'): '2 (post-chapter)'
}


def _openw(path, **kwargs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w', encoding='utf-8', **kwargs)


def _category(psv_psn):
    return _PSV_PSN_CATEGORIES.get(psv_psn) or '1 (normal verse)'


def _subtype(key, wtel):
    fn = _SUBTYPE_FNS[key]
    return fn(wtel[key])
def _rsubtype(wtel):
    if isinstance(wtel, str):
        return str
    keys = tuple(wtel.keys())
    assert len(keys) == 1
    key = keys[0]
    return _subtype(key, wtel)


def print_nusah_tmpl(r, wtel, psv_psn, column_letter):
    if (column_letter != 'E'):
        return
    assert isinstance(wtel, dict)
    keys = tuple(wtel.keys())
    assert len(keys) == 1
    key = keys[0]

    for arg in wtel['tmpl'][1:]:
        print(arg);
    print("\n");
    return
"""
def html_wtel_to_str(wtel):  # returns a TEX string
    # there are 100+ templates. This should have a conversion from the template to a latex string for each one
    # some will require dealing with nested templates
    # Ignoring "custom_tag"s (for now)
    if isinstance(wtel, str):
        return wtel
    elif isinstance(wtel,list) and len(wtel)==1:
        return wtel[0]
    keys = tuple(wtel.keys())
    assert len(keys) == 1
    key = keys[0]
    tmpl_subtype = _subtype(key, wtel)
    if ((tmpl_subtype == 'כו"ק')or (tmpl_subtype == 'קו"כ')
            or (tmpl_subtype== 'מ:כו"ק כתיב מילה חדה וקרי תרתין מילין')
            or (tmpl_subtype== 'מ:קו"כ כתיב מילה חדה וקרי תרתין מילין')
            or (tmpl_subtype== 'מ:כו"ק כתיב מילה חדה וקרי תרתין מילין בין שני מקפים')
            or (tmpl_subtype == 'מ:כו"ק בין שני מקפים')
            or (tmpl_subtype=='מ:כו"ק של שתי מילים בהערה אחת')
            or (tmpl_subtype=='מ:כו"ק כתיב תרתין מילין וקרי מילה חדה')
            or (tmpl_subtype=='מ:קו"כ קרי שונה מהכתיב בשתי מילים')
            or (tmpl_subtype=='מ:כו"ק קרי שונה מהכתיב בשתי מילים')):
        text=  ""
        text += "(" + wtel['tmpl'][1][0] + "){"
        text += "קרי: "
        text += wtel_to_str(wtel['tmpl'][2][0]) + "}"
        return text
    elif (tmpl_subtype == 'קרי ולא כתיב'):
        text = "( ){קרי ולא כתיב: "
        text += wtel['tmpl'][1][0] + "}"  # This prints in the form {[text]} for now.
        # subject for further consideration. wiki just uses [], but prints most קריאין with no indication
        return text
    elif (tmpl_subtype == 'כתיב ולא קרי'):
        text = "(" + wtel['tmpl'][1][0] + "){"
        text += "{כתיב ולא קרי}"
        return text
    elif (tmpl_subtype == 'קו"כ-אם'): #TODO: Might want to change
        text = wtel['tmpl'][1][0] + "{"
        text += '{קו"כ-אם:'
        text += wtel_to_str(wtel['tmpl'][1][0])
        for note in wtel['tmpl'][2:]:
            text+=" | "+ note[0]
        text+= "}"
        return text
    elif (tmpl_subtype == "מ:אות מנוקדת"):
        text = wtel['tmpl'][1][0]
        text += "{אות מנוקדת."
        for note in wtel['tmpl'][2:]:
            text+= "  |  "+wtel_to_str(note[0])
        text += "}"
        return text
    elif (tmpl_subtype == "מ:אות-ק"):
        text = "{אות-ק,"+wtel['tmpl'][1][0] +"}"
        return text
    elif (_subtype(key, wtel) == "מ:אות-ג"):
        text = "{\\Large "+wtel['tmpl'][1][0] +"}"
        return text
    elif ((tmpl_subtype == "ססס")
        or (tmpl_subtype == "סס")):
        # TODO: This is not the way it is displayed on wikisource
        return "{ס}"
    elif (tmpl_subtype== "פפ"):
        return "{פ}"
    elif (tmpl_subtype== "פסקא באמצע פסוק"):
        text = wtel_to_str(wtel['tmpl'][1][0])
        text += "{{פסקא באמצע פסוק}}"
        return text
    elif(tmpl_subtype=="ר0"):#TODO: For HTML I think it's best to maintian the tags as is
        return "{ר0}"
    elif(tmpl_subtype=="ר1"):
        return "{ר1}"
    elif(tmpl_subtype=="ר2"):
        return "{ר2}"
    elif(tmpl_subtype=="ר3"):
        return "{ר3}"
    elif(tmpl_subtype=='נוסח'):
        return "{הערה בתוך הערה}"+get_nussach_note(wtel)
    else:
        print(wtel)
        return
"""
def wtel_to_str(wtel,caller=""):  # returns a TEX string
    # there are 100+ templates. This should have a conversion from the template to a latex string for each one
    # some will require dealing with nested templates
    # Ignoring "custom_tag"s (for now)
    if isinstance(wtel, str):
        return wtel
    keys = tuple(wtel.keys())
    assert len(keys) == 1
    key = keys[0]
    tmpl_subtype = _subtype(key, wtel)
    if ((tmpl_subtype == 'כו"ק')or (tmpl_subtype == 'קו"כ')
            or (tmpl_subtype== 'מ:כו"ק כתיב מילה חדה וקרי תרתין מילין')
            or (tmpl_subtype== 'מ:קו"כ כתיב מילה חדה וקרי תרתין מילין')
            or (tmpl_subtype== 'מ:כו"ק כתיב מילה חדה וקרי תרתין מילין בין שני מקפים')
            or (tmpl_subtype == 'מ:כו"ק בין שני מקפים')
            or (tmpl_subtype=='מ:כו"ק של שתי מילים בהערה אחת')
            or (tmpl_subtype=='מ:כו"ק כתיב תרתין מילין וקרי מילה חדה')
            or (tmpl_subtype=='מ:קו"כ קרי שונה מהכתיב בשתי מילים')
            or (tmpl_subtype=='מ:כו"ק קרי שונה מהכתיב בשתי מילים')):
        if(caller==""):
            text=  "\\edtext{"
            text += "(" + wtel['tmpl'][1][0] + ")}{"
            text += "\\kri{קרי: "
            text += wtel_to_str(wtel['tmpl'][2][0],"קרי") + "}}"
            return text
        else:
            text = "(כתיב:" + wtel['tmpl'][1][0] + ")"
            text += "{קרי: "+wtel_to_str(wtel['tmpl'][2][0],"קרי") + "}"
            return text
    elif (tmpl_subtype == 'קרי ולא כתיב'):
        if(caller==""):
            text = "\\edtext{( )}{\\kri{קרי ולא כתיב: "
            text += wtel['tmpl'][1][0] + "}}"  # This prints in the form {[text]} for now.
            # subject for further consideration. wiki just uses [], but prints most קריאין with no indication
            return text
        else:
            text="(){קרי ולא כתיב: "+wtel['tmpl'][1][0]+ "}"
    elif (tmpl_subtype == 'כתיב ולא קרי'):
        if(caller==""):
            text = "\\edtext{(" + wtel['tmpl'][1][0] + ")}{"
            text += "\\kri{כתיב ולא קרי}}"
            return text
        else:
            text= "("+wtel['tmpl'][1][0]+")"
            text+= "{כתיב ולא קרי}"
            return text
    elif (tmpl_subtype == 'קו"כ-אם'): #TODO: Might want to change
        if caller!="":
            text = '{קו"כ-אם, '
            text += wtel_to_str(wtel['tmpl'][1][0])+"}"
            return text
        text=  "\\edtext{"
        text += wtel_to_str(wtel['tmpl'][1][0],"קרי") + "}{"
        text += "\\kri{קרי: "
        text += wtel_to_str(wtel['tmpl'][1][0],"קרי")
        for note in wtel['tmpl'][2:]:
            text+=" | "+ note[0]
        text+= "}}"
        return text
    elif (tmpl_subtype == "מ:אות מנוקדת"):
        if caller!="":
            return wtel['tmpl'][1][0]
            # print("אות מנוקדת in recursive call!")
            # assert False
        text=  "\\edtext{"
        text += wtel['tmpl'][1][0] + "}{"
        text += "\\kri{אות מנוקדת: "
        for note in wtel['tmpl'][2:]:
            text+= "  |  "+wtel_to_str(note[0],"אות")
        text += "}}"
        return text
    elif (tmpl_subtype == "מ:אות-ק"):
        if caller!="":
            text = "\\small{" + wtel['tmpl'][1][0] + "}"
            return text
        else:
            text = "\\edtext{\\small{"
            text += wtel['tmpl'][1][0] + "} }{"
            text += "\\kri{אות קטנה}}"
            return text
    elif (tmpl_subtype == "מ:אות-ג"):
        if(caller!=""):
            text = "{\\Large " + wtel['tmpl'][1][0] + "}"
            return text
        else:
            text = "\\edtext{"
            text += "{\\Large " + wtel['tmpl'][1][0] + "}}"
            text += "\\kri{אות גדולה}}"
            return text
    elif (tmpl_subtype=="מ:אות תלויה"):
        text='\\textsuperscript{'+wtel['tmpl'][1][0]+'}'
        return text



    elif (tmpl_subtype == "נוסח") and (caller==""):
        lemma=""
        for ent in wtel['tmpl'][1]:
            lemma+= wtel_to_str(ent,"lemma")
        # lemma = wtel_to_str(wtel['tmpl'][1][0],"lemma")
        # Concatenation concerns are naught, not a relevant performance factor at this scale. I think.
        text = "\edtext{" + lemma + "}{"
        note_contents = "\\vart{"
        notfirst = False
        for arg in wtel['tmpl'][2:]:
            if (notfirst):
                note_contents += " | "
            else:
                notfirst = True
            if isinstance(arg, str):
                note_contents += arg
            else:
                for arg_wtel in arg:
                    note_contents += wtel_to_str(arg_wtel,"נוסח")
        text += note_contents + "}}\u200F"
        return text


    elif (tmpl_subtype == "מ:קמץ"):
        return wtel['tmpl'][1][0][2:]
        # We go for the grammatical forms here
    elif (tmpl_subtype == "מ:לגרמיה"):
        return u"\u2009" + "| "
    elif (tmpl_subtype == "מ:פסק"):
        return " | "
    elif (tmpl_subtype == "ירח בן יומו"):
        return "֪"
    elif (tmpl_subtype == "מ:נו\"ן הפוכה"):
        # TODO: The template contains a long note, partly academic,
        # partly noting that the glyph is font dependent.
        # This should be added eventually
        return "׆"
    elif(tmpl_subtype== "שני טעמים באות אחת"):
        text= wtel['tmpl'][1][0] + wtel['tmpl'][2][0]
        return text
    elif(tmpl_subtype== "מ:גרשיים ותלישא גדולה"):
        return "֞֠"
    elif(tmpl_subtype=="מ:טעם ומתג באות אחת"):
        return "͏ֽ"
    elif(tmpl_subtype=='אתנח הפוך'):
        return  "֢"
    elif (tmpl_subtype == "ססס") or (tmpl_subtype == "סס"):
        # TODO: This is not the way it is displayed on wikisource
        return "{ס}    "
    elif ((tmpl_subtype=="מ:ששש")):
        # TODO: This is not the way it is displayed on wikisource
        return "    " #TODO: replace spaces with correct tab character
    elif ((tmpl_subtype== "פפ")or (tmpl_subtype== "פפפ")):
        return "{פ}\n"
    elif (tmpl_subtype== "פסקא באמצע פסוק"):
        text = "\\edtext{"
        text += wtel_to_str(wtel['tmpl'][1][0],"פסקא")
        text += "}{\\kri{פסקא באמצע פסוק}"
        for note in wtel['tmpl'][2:]:
            text+= note[0]
        text+= "}\u200F"
        return text
    elif(tmpl_subtype=='מ:ירושלם'):
        #u"\u0008"+
        if(len(wtel['tmpl'])<3):
            text = "ל" + wtel['tmpl'][1][0]
        else:
            text= "ל"+wtel['tmpl'][1][0] +wtel['tmpl'][2][0]
        text+= "\u034Fִם"
        return text
    elif(tmpl_subtype=='מ:ירושלמה'):
        text= wtel['tmpl'][1][0] +wtel['tmpl'][2][0]
        text+= "\u034Fִ"
        return text
    elif (tmpl_subtype== "מ:הערה"):
        text= "*\\ledsidenote{"+wtel['tmpl'][1][0]+"}"
        return text
    elif(tmpl_subtype=="גלגל"):
        return "֪"
    elif(tmpl_subtype=='מ:מקף אפור'):
        return " " #TODO: Here we break with miqra's decision to add a makaf where it should be there by virtue of morphology
    elif(tmpl_subtype=="ר0"):#TODO: For HTML I think it's best to maintian the tags as is
        return "&"
    elif(tmpl_subtype=="ר1"):
        return "{ר1}"
    elif(tmpl_subtype=="ר2"):
        return "{ר2}"
    elif(tmpl_subtype=="ר3"):
        return "{ר3}"
    elif(tmpl_subtype=='נוסח') and (caller!=""):
            keys = tuple(wtel.keys())
            key = keys[0]
            if (_subtype(key, wtel) != "נוסח"):
                return ""
            lemma = "<b>" + wtel_to_str(wtel['tmpl'][1][0],"נוסח")+ "</b>- "
            note_contents = ""
            notfirst=False
            for arg in wtel['tmpl'][2:]:
                if(notfirst):
                    note_contents += " | "
                else:
                    notfirst=True
                if isinstance(arg, str) or isinstance(arg, dict):
                    note_contents += " ## " + wtel_to_str(arg,"נוסח")
                else:
                    for arg_wtel in arg:
                        if (type(arg_wtel) == str):
                            note_contents += arg_wtel
                        else:
                            note_contents += wtel_to_str(arg_wtel)

            return "{הערה בתוך הערה}"+lemma+note_contents
    elif(tmpl_subtype=='פרשה-מרכז'):
        text=wtel['tmpl'][1][0][6:]
        return text
    elif((wtel.has_key('custom_tag'))and(wtel['custom_tag'][-9:]=='צורת השיר')): #TODO: No documentation. Need to play with versification and tabular
        return " "
    else:
        print(wtel)
        return

def gimatria(heb):
    MISPAR_HECHRACHI = { # From here: https://github.com/avi-perl/Hebrew/blob/master/hebrew/gematria.py
        "א": 1,    "ב": 2,    "ג": 3,    "ד": 4,    "ה": 5,
        "ו": 6,    "ז": 7,    "ח": 8,    "ט": 9,    "י": 10,
        "כ": 20,   "ך": 20,   "ל": 30,   "מ": 40,   "ם": 40,
        "נ": 50,   "ן": 50,   "ס": 60,   "ע": 70,   "פ": 80,
        "ף": 80,   "צ": 90,   "ץ": 90,   "ק": 100,  "ר": 200,
        "ש": 300,  "ת": 400,
    }
    val =0
    assert type(heb)==str
    for char in heb:
        val+= MISPAR_HECHRACHI[char]
    output= str(val)
    return output

def old_loc_to_line(loc_str):
    if(len(loc_str)<1):
        return ""
    if(loc_str[2:6]=='נוסח'): # TODO: find a way to hand nussach notes here
        loc_str= loc_str[7:]
    if(type(loc_str)==list):
        return ""
    # use replace in case the passuk is the last param and doesn't get caught with the braces. Not neccisary for the opening braces.
    strs= loc_str.replace("}","",3).split('|')
    assert len(strs[2]) >0
    assert len(strs[3]) >0
    assert len(strs[2])<4
    assert len(strs[3])<3
    return (gimatria(strs[2]))+"."+ (gimatria(strs[3]))

def loc_to_line(strs):
    if(len(strs)<4):
        return ""
    assert len(strs[2][0]) >0
    assert len(strs[3][0]) >0
    assert len(strs[2][0])<4
    assert len(strs[3][0])<3
    return (gimatria(strs[2][0]))+"."+ (gimatria(strs[3][0]))
def get_full_loc(cp):
    if(cp[0]['tmpl'][0][0]=='נוסח'):
        locs= cp[0]['tmpl'][1][0]['tmpl']
    else:
        locs=cp[0]['tmpl']
    return locs[1][0] +" "+locs[2][0]+" "+locs[3][0]
def output_to_tex(sec_name):
    text = """\documentclass{article}
    \\renewcommand{\\baselinestretch}{1.25}
    \\usepackage{polyglossia}
    \\usepackage[series={A,B},noend,noeledsec,nofamiliar]{reledmac} 
    \\setdefaultlanguage[numerals=arabic]{hebrew}
    \\newfontfamily\hebrewfont[Script=Hebrew]{SBL Hebrew}
    \\newcommand{\\vart}[1]{\Bfootnote{#1}}	% Macro to make adding notes a bit quicker.
    \\newcommand{\\kri}[1]{\Afootnote{#1}}	% Macro to make adding notes a bit quicker.
    \\newcommand{\loc}[1]{\\textsuperscript{\locf{#1}}}
    \\newfontfamily\locf[Script=Hebrew]{Aharoni}
    \\firstlinenum{1}
    \\linenumincrement{2}
    \\lineation{page}
    \\Xhangindent[B]{1em}
    \\begin{document}
    \\beginnumbering
    """
    #sec_name = 'Ruth'
    inpath = f'mam-json/MAM-{sec_name}.json'
    with open(inpath, encoding='utf-8') as fpi:
        sec = json.load(fpi)
    # chapent: chaptered entity (book or sub-book)
    first_flag= False
    for chapent in sec['body']:
        if first_flag:
            text+='\n\pend'
        else:
            first_flag=True
        text += '\n\pstart[\subsection*{' + (chapent['book_name']) + "}]\n"
        for num, chapter in chapent['chapters'].items():
            text += "\n\\ledsidenote{{\loc{"+ num +" פרק" +"}}}" #Need to flip order bec the sidienote seems to use a LTR space
            for pseudoverse in chapter.items():
                psv_psn, psv_contents = pseudoverse
                if ((psv_psn != '0') and (psv_psn != 'תתת')):
                    #text += "\\setline{" + gimatria(psv_psn) + "}\\startlock\n"
                    text += "\n{\\loc{ " + psv_psn + "}~}\u200F"
                minirow = _MINIROW(*psv_contents)
                if(not (len(minirow.CP)>0)):
                    continue
                print(get_full_loc(minirow.CP))
                if loc_to_line(minirow.D) == '13.3':
                    print("incoming!")
                skipping=False
                for wikitext_el in minirow.EP:
                    # The following mess is required to get around python not playing nicely with concatenating the nikkud for ירושלם.
                    #TODO: add for ירושלמה.
                    # The proper solution would just be to modify the base json to remove the ל and the מ, but that's for later.
                    if skipping:
                        skipping=False
                        continue
                    if(_rsubtype(wikitext_el)=="מ:ירושלם"):
                        text= text[:-2]
                        skipping=True
                    output =wtel_to_str(wikitext_el)
                    if(type(output) is None):
                        print("ERR!")
                    text += output + " "
    text += '''
    \\pend 
    \\endnumbering
    \\end{document}
                '''
    #TEX reserved chars require escaping.
    text= text.replace('&','\\&')
    text= text.replace('_', '\\_')
    # Changes for apparatus
    text= text.replace('א(ס)','א\\textsubscript{ס}')
    text= text.replace('א(ק)','א\\textsubscript{ק}')
    text= text.replace('ש1','ש\\textsubscript{1}')
    text= text.replace('ב1','ב\\textsubscript{1}')
    text= text.replace('ל1','ל\\textsubscript{1}')
    text= text.replace('ל2','ל\\textsubscript{2}')

    outpath = f'out/MAM-{sec_name}-tex.tex'
    with _openw(outpath) as fpo:
        fpo.write(text)


def main():
    #    output_to_tex('Ruth')
    output_to_tex('SifEm')


if __name__ == "__main__":
    main()


