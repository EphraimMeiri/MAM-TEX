import collections
import json
import os

_MINIROW = collections.namedtuple('Minirow', 'D, CP, EP')
_SUBTYPE_FNS = {  # wte: Wikitext element (str or single-item dict)
    'tmpl': lambda wte: wte[0][0],
    'stmpl': lambda wte: wte.split('|')[0] if isinstance(wte, str) else wte,  # New format: structured template as string
    'custom_tag': lambda wte: wte,
    'unparseable': lambda wte: None,
}
_PSV_PSN_CATEGORIES = {
    '0': '0 (pre-chapter)',
    str('תתת'): '2 (post-chapter)'
}

# Configuration settings
using_ednotes = False  # Setting 1: With notes (True) / Without notes (False)
use_column_markers = True  # Setting 2: Format songs using column markers (True/False)
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

def _parse_stmpl(stmpl_str):
    """Parse a structured template string into a dict-like structure.

    Example: "מ:קמץ|ד=נׇעֳמִ֜י|ס=נָעֳמִ֜י" ->
             {'name': 'מ:קמץ', 'params': {'ד': 'נׇעֳמִ֜י', 'ס': 'נָעֳמִ֜י'}}
    """
    parts = stmpl_str.split('|')
    name = parts[0]
    params = {}
    for part in parts[1:]:
        if '=' in part:
            key, val = part.split('=', 1)
            params[key] = val
    return {'name': name, 'params': params}

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
def wtel_to_str(wtel,caller=""):  # returns a TEX string
    # there are 100+ templates. This should have a conversion from the template to a latex string for each one
    # some will require dealing with nested templates
    # Ignoring "custom_tag"s (for now)
    if isinstance(wtel, str):
        return wtel
    keys = tuple(wtel.keys())
    assert len(keys) == 1
    key = keys[0]

    # Handle stmpl (new format) by converting to simplified form
    if key == 'stmpl':
        parsed = _parse_stmpl(wtel['stmpl'])
        tmpl_name = parsed['name']
        params = parsed['params']

        # Handle specific stmpl templates based on template name
        if tmpl_name == "מ:קמץ":
            # For קמץ, return the 'ס' param (grammatical form)
            return params.get('ס', params.get('ד', ''))
        elif tmpl_name == "ר1":
            return "{\\hfill}"
        elif tmpl_name in ["ר2", "ר3"]:
            return r'\newline\hspace*{.5em}'
        elif tmpl_name == "ר0":
            return r'\hspace{1em}'
        elif tmpl_name in ["מ:לגרמיה", "מ:לגרמיה-2"]:
            return u"\u2009" + "| "
        elif tmpl_name == "מ:פסק":
            return " | "
        elif tmpl_name == "מ:מקף אפור":
            return " "
        elif tmpl_name in ["כו\"ק", "קו\"כ"]:
            # Get the last param which is usually the qere reading
            vals = list(params.values())
            if len(vals) >= 2:
                if caller == "":
                    text = "(" + vals[-2] + ")"
                    text += "\\kri{" + vals[-1] + "}"
                    return text
                else:
                    return "(" + vals[-2] + "){" + vals[-1] + "}"
            return vals[-1] if vals else ''
        elif tmpl_name == "קרי ולא כתיב":
            vals = list(params.values())
            if caller == "":
                text = "( )\\kri{קרי ולא כתיב: " + (vals[0] if vals else '') + "}"
                return text
            else:
                return "(){קרי ולא כתיב: " + (vals[0] if vals else '') + "}"
        elif tmpl_name == "כתיב ולא קרי":
            vals = list(params.values())
            if caller == "":
                text = "(" + (vals[0] if vals else '') + ")"
                text += "\\kri{כתיב ולא קרי}"
                return text
            else:
                return "(" + (vals[0] if vals else '') + "){כתיב ולא קרי}"
        elif tmpl_name == "מ:אות-ג":
            vals = list(params.values())
            letter = vals[0] if vals else ''
            if caller != "":
                return "{\\Large " + letter + "}"
            else:
                return "\\edtext{{\\Large " + letter + "}}\\kri{אות גדולה}}"
        elif tmpl_name == "מ:אות-ק":
            vals = list(params.values())
            letter = vals[0] if vals else ''
            if caller != "":
                return "\\small{" + letter + "}"
            else:
                return "\\edtext{\\small{" + letter + " }}{\\kri{אות קטנה}}"
        elif tmpl_name == "מ:אות מנוקדת":
            vals = list(params.values())
            if caller != "":
                return vals[0] if vals else ''
            text = (vals[0] if vals else '') + "}{"
            text += "\\kri{אות מנוקדת}"
            return text
        elif tmpl_name in ["גלגל", "גלגל-2"]:
            return "֪"
        elif tmpl_name == "מ:דחי":
            # Dagesh/hiriq - just return the corrected form (last param)
            vals = list(params.values())
            return vals[-1] if vals else ''
        elif tmpl_name == "מ:צינור":
            # Vertical pipe - return the corrected form
            vals = list(params.values())
            return vals[-1] if vals else ''
        # For unknown stmpl, return the last param value or first param or empty string
        vals = list(params.values())
        return vals[-1] if vals else ''

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
        # if(caller==""):
        # text=  "\\edtext{"
        text = ""
        text += "(" + wtel['tmpl'][1][0] + ")"
        text += "\\kri{"
        text += wtel_to_str(wtel['tmpl'][2][0],"קרי") + "}"
        return text
        # else:
        #     text = "(" + wtel['tmpl'][1][0] + ")"
        #     text += "\\kri{"+wtel_to_str(wtel['tmpl'][2][0],"קרי") + "}"
        #     return text
    elif (tmpl_subtype == 'קרי ולא כתיב'):
        if(caller==""):
            text = "( )\\kri{קרי ולא כתיב: "
            text += wtel['tmpl'][1][0] + "}"  # This prints in the form {[text]} for now.
            # subject for further consideration. wiki just uses [], but prints most קריאין with no indication
            return text
        else:
            text="(){קרי ולא כתיב: "+wtel['tmpl'][1][0]+ "}"
    elif (tmpl_subtype == 'כתיב ולא קרי'):
        if(caller==""):
            text = "(" + wtel['tmpl'][1][0] + ")"
            text += "\\kri{כתיב ולא קרי}"
            return text
        else:
            text= "("+wtel['tmpl'][1][0]+")"
            text+= "{כתיב ולא קרי}"
            return text
    elif (tmpl_subtype == 'קו"כ-אם'): #TODO: Might want to change
        if caller!="":
            text = ''
            text += wtel_to_str(wtel['tmpl'][1][0])
            return text
        return wtel_to_str(wtel['tmpl'][1][0])
        # text=  ""
        # text += wtel_to_str(wtel['tmpl'][1][0],"קרי") + "}{"
        # text += "\\kri{קרי: "
        # text += wtel_to_str(wtel['tmpl'][1][0],"קרי")
        # for note in wtel['tmpl'][2:]:
        #     text+=" | "+ note[0]
        # text+= "}"
        # return text
    elif (tmpl_subtype == "מ:אות מנוקדת"):
        if caller!="":
            return wtel['tmpl'][1][0]
            # print("אות מנוקדת in recursive call!")
            # assert False
        text=  ""
        text += wtel['tmpl'][1][0] + "}{"
        text += "\\kri{אות מנוקדת: "
        for note in wtel['tmpl'][2:]:
            text+= "  |  "+wtel_to_str(note[0],"אות")
        text += "}"
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
            output = wtel_to_str(ent,"lemma")
            if output:
                lemma += output
            else:
                print("No output for lemma",ent)
            # lemma += wtel_to_str(ent,"lemma")
        # lemma = wtel_to_str(wtel['tmpl'][1][0],"lemma")
        # Concatenation concerns are naught, not a relevant performance factor at this scale. I think.
        if using_ednotes:
            text = "\edtext{" + lemma + "}{"
            note_contents = ""
            if lemma == r'\newline\hspace*{.5em}' or lemma=="{\\hfill}" or lemma=="{\\hspace{1em}":
                note_contents+= "\\lemma{*}"
            elif "\\kri" in lemma:
                note_contents+= "\\lemma{כ{.5em}ק*}"
            note_contents += "\\vart{"
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
        else:
            return lemma


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
        return r'֢'
    elif (tmpl_subtype == "ססס") or (tmpl_subtype == "סס"):
        # TODO: This is not the way it is displayed on wikisource
        return "{ס}    "
    elif ((tmpl_subtype=="מ:ששש")):
        # TODO: This is not the way it is displayed on wikisource
        return "    " #TODO: replace spaces with correct tab character
    elif ((tmpl_subtype== "פפ")or (tmpl_subtype== "פפפ")):
        return "{פ}\n"
    elif (tmpl_subtype== "פסקא באמצע פסוק"):
        text = wtel_to_str(wtel['tmpl'][1][0],"פסקא")
        text += "\\kri{פסקא באמצע פסוק}"
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
    elif(tmpl_subtype== "ר0"):#TODO: For HTML I think it's best to maintian the tags as is
        return r'\hspace{1em}'
        # return "{\\hfill}"
    elif(tmpl_subtype=="ר1"):
        return "{\\hfill}"
    elif(tmpl_subtype== "ר2" or tmpl_subtype=="ר3"):
        return r'\newline\hspace*{.5em}'
    elif(tmpl_subtype=='נוסח') and (caller!=""):
            return wtel_to_str(wtel['tmpl'][1][0],"נוסח")
    elif(tmpl_subtype=='פרשה-מרכז'):
        text=wtel['tmpl'][1][0][6:]
        return text
    elif(('custom_tag' in wtel) and (wtel['custom_tag'][-9:]=='צורת השיר')): #TODO: No documentation. Need to play with versification and tabular
        return " "
    else:
        print("Unknown template:", wtel)
        return ""  # Return empty string instead of None

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

def count_lines(text):
    newline = r'\newline\hspace*{.5em}'
    return text.count(newline) + text.count("\\par")


import re
perek_pattern = r'\\pstart\[\\subsection\*\{\\textcolor\{red\}\{פרק\s([א-ת]{1,3})\}\}\]'
passuk_pattern = r'\{\\loc\{ ([א-ת]{1,3})\}~\}‏'
newline = r'\newline\hspace*{.5em}'
space = r'{\hfill}'
s_space = "\\hspace{1em}"
spaces = [newline, space, s_space]
all_whitespace = r'(\\newline\\hspace\*\{\.5em\})|(\{\\hfill\})|(\\hspace\{1em\})'
def emet_postprocess(full_text,non_header_perakim=None,bi_header_perakim=None):
    mod2 = []
    perakim = re.split(perek_pattern, full_text)
    mod2.append(perakim[0])
    perakim = perakim[1:]
    for pi in range(len(perakim))[::2]:
        perek = perakim[pi]
        pesukim = re.split(passuk_pattern, perakim[pi + 1])[1:]
        mod2.append('\\pstart[\\subsection*{\\textcolor{red}{פרק ' + perek + '}}]')
        for vi in range(1, len(pesukim))[::2]:
            passuk = pesukim[vi - 1]
            v_text = pesukim[vi]
            patterns = re.split(all_whitespace, v_text)
            if patterns:
                text = [s for s in patterns if s]
                patterns = [(p, i) for i, p in enumerate(text) if p in spaces]
                if passuk == "א" and perek not in non_header_perakim:
                    for i, p in enumerate(patterns):
                        if i == len(patterns)-1 and len(patterns)%2==1:
                            print(f"Leaving {p[0]} @ {perek}:{passuk}")
                        elif i % 2 == 0:
                            text[p[1]] = newline
                        else:
                            text[p[1]] = space
                else:
                    for i, p in enumerate(patterns):
                        if i == len(patterns)-1 and len(patterns)%2==0:
                            print(f"Leaving {p[0]} @ {perek}:{passuk}")
                        elif i % 2 == 1:
                            text[p[1]] = newline
                        else:
                            text[p[1]] = space
                mod2.append('\n{\\loc{ ' + passuk + '}~}‏' + "".join(text))
            else:
                mod2.append('\n{\\loc{ ' + passuk + '}~}‏' + v_text)
    modified_text = "".join(mod2)
    return modified_text
def psalms_postprocess(full_text):
    non_header_perakim = "א ב י לג מג עא צא צג צד צה צו צז צט קד קה קז קיד קטו קטז קיז קיח קיט קלו קלז".split()
    bi_header_perakim = "ג ה ו ח ט יב כב  קל".split
    modified_text= emet_postprocess(full_text,non_header_perakim,bi_header_perakim)
    mod3 = []
    perakim = re.split(perek_pattern, modified_text)
    mod3.append(perakim[0])
    perakim = perakim[1:]
    for pi in range(len(perakim))[::2]:
        mod3.append('\\pstart[\\subsection*{\\textcolor{red}{פרק ' + perakim[pi] + '}}]\\label{פרק '+perakim[pi]+'}')
        if len(perakim) > (pi + 2):
            count = count_lines(perakim[pi + 1])
            next_count = count_lines(perakim[pi + 3])
            if (pi ==0 or "\\ledpb" in perakim[pi - 1]) and ((count + next_count < 25)or(count>27 and (count-27)+next_count<25)):
                print("Joining "+perakim[pi] + " and " + perakim[pi + 2])
                perakim[pi + 1] = perakim[pi + 1].replace("\\ledpb", "")
        mod3.append(perakim[pi + 1])
    return "".join(mod3)
def job_postprocessing(full_text):
    non_header_perakim = "ב ה ז י יג יד יז כד ל לא לג לז לט מא".split()
    modified_text= emet_postprocess(full_text,non_header_perakim)
    mod3 = []
    perakim = re.split(perek_pattern, modified_text)
    mod3.append(perakim[0])
    perakim = perakim[1:]
    print(perakim[0],perakim[1],perakim[2],perakim[3])
    print(perakim[1].count("\\par"),perakim[3].count("\\par"))
    perakim[1] = perakim[1].replace("\\par"," ").replace("\n\n","\n")
    perakim[3] = perakim[3].replace("\\par"," ").replace("\n\n","\n")
    print(perakim[1].count("\\par"),perakim[3].count("\\par"))
    ending = perakim[-1].split("{\\loc{ ז}~}")
    story = "\\vspace{5mm}\\par" + "{\\loc{ ז}~}" + ending[1].replace("\\par"," ").replace("\n\n","\n")
    ending[1] = story
    perakim[-1] = "".join(ending)
    for pi in range(len(perakim))[::2]:
        perek = perakim[pi]
        mod3.append('\\pstart[\\subsection*{\\textcolor{red}{פרק ' + perek + '}}]')
        if pi+2<len(perakim) and perakim[pi+2] in non_header_perakim:
            print("Non-header perek: " + perek)
            perakim[pi + 1] = perakim[pi + 1].replace("\\ledpb","")
        mod3.append(perakim[pi + 1])
    return "".join(mod3)

def output_to_tex(sec_name):
    text = """\\documentclass[12pt]{article}
    \\renewcommand{\\baselinestretch}{1.25}
    \\usepackage[
        paperwidth= 5.5in,
        paperheight= 8.5in,
%        paperwidth=4.25in,
%        paperheight=6.875in,
        top=0.5in,
        bottom= .75in
        ]{geometry}
    \\usepackage{titlesec}
    \\usepackage{polyglossia}
    \\usepackage{xcolor}

    \\usepackage[series={A,B},noend,noeledsec,nofamiliar]{reledmac} 
    \\setdefaultlanguage[numerals=arabic]{hebrew}
    \\newfontfamily\hebrewfont[Script=Hebrew]{Taamey D}
    \\newcommand{\\vart}[1]{\\Bfootnote{#1}}	% Macro to make adding notes a bit quicker.
    \\newcommand{\\kri}[1]{\\ledsidenote{\\small{#1}}}	% Macro to make adding notes a bit quicker.
    \\newcommand{\\loc}[1]{\\textsuperscript{\locf{#1}}}
    %\\Xarrangement[B]{paragraph}
    

    \\ledpbsetting{after}
    \\usepackage{ragged2e}
    \\newcommand{\\rightText}[1]{\\RaggedLeft#1}
    \\newcommand{\\leftText}[1]{\\RaggedRight#1}
    \\titleformat{\\section}[hang]{\\normalfont\\Large\\bfseries}{\\thesection}{1em}{}
    \\titlespacing*{\\section}{0pt}{0pt}{0pt}
    \\titlespacing*{\\subsection}{0pt}{-\\parskip}{0pt}
    \\Xnotefontsize[B]{\\tiny}
    	
    \\newfontfamily\\locf[Script=Hebrew]{Aharoni}
    \\firstlinenum{2000}
    \\linenumincrement{2000}    
    \\lineation{page}
    \\Xhangindent[B]{1em}
    \\begin{document}
    \\setlength{\\parindent}{0pt}    
    \\beginnumbering
    """
    # Book name mapping from common names to new format filenames
    BOOK_MAP = {
        'Genesis': 'A1-Genesis',
        'Exodus': 'A2-Exodus',
        'Leviticus': 'A3-Levit',
        'Numbers': 'A4-Numbers',
        'Deuteronomy': 'A5-Deuter',
        'Joshua': 'B1-Joshua',
        'Judges': 'B2-Judges',
        'Samuel': 'BA-Samuel',
        'Kings': 'BC-Kings',
        'Isaiah': 'C1-Isaiah',
        'Jeremiah': 'C2-Jeremiah',
        'Ezekiel': 'C3-Ezekiel',
        'The-12': 'CA-The-12-Minor-Prophets',
        'Psalms': 'D1-Psalms',
        'Proverbs': 'D2-Proverbs',
        'Job': 'D3-Job',
        'Song': 'E1-Song of Songs',
        'Ruth': 'E2-Ruth',
        'Lamentations': 'E3-Lamentations',
        'Ecclesiastes': 'E4-Ecclesiastes',
        'Esther': 'E5-Esther',
        'Daniel': 'F1-Daniel',
        'Ezra': 'FA-Ezra-Nexemiah',
        'Chronicles': 'FC-Chronicles',
    }

    # Try to find the MAM-parsed data in multiple locations
    mam_data_paths = [
        '/tmp/MAM-parsed/plain',
        '/Users/ephraimmeiri/gitEtc/MAM-parsed/plain',
        './MAM-parsed/plain',
    ]

    mam_data_dir = None
    for path in mam_data_paths:
        if os.path.exists(path):
            mam_data_dir = path
            break

    if mam_data_dir is None:
        raise FileNotFoundError("Could not find MAM-parsed data. Please clone https://github.com/bdenckla/MAM-parsed")

    # Get the correct filename
    file_name = BOOK_MAP.get(sec_name, sec_name)
    inpath = os.path.join(mam_data_dir, f'{file_name}.json')
    with open(inpath, encoding='utf-8') as fpi:
        sec = json.load(fpi)
    # chapent: chaptered entity (book or sub-book)
    first_flag= False
    for book in sec['book39s']: # Chnage for new (plain) format
        if first_flag:
            text+='\n\pend'
        else:
            first_flag=True
        text += '\n\subsection*{' + (book['book24_name']) + "}\n"
        if(sec_name=="Psalms"):
            text+= """\\pstart[]על פי נוסח מקרא ע׳׳פ המסורה \\newline 
                        בעיצוב ב׳ טורי
                        \\newline
                        \\newline ספר א {\\hfill} \\textcolor{red}{פרק א}{\\hspace{1em}} עמוד \\pageref{פרק א}
                        \\newline {\\small {\\locf{חתימה:}} ‏בָּ֘ר֤וּךְ יְהֹוָ֨ה | אֱלֹ֘הֵ֤י יִשְׂרָאֵ֗ל מֵֽ֭הָעוֹלָם וְעַ֥ד הָעוֹלָ֗ם אָ֘מֵ֥ן | וְאָמֵֽן׃}
                        \\newline
                        \\newline ספר ב {\\hfill} \\textcolor{red}{פרק מב}{\\hspace{1em}} עמוד \\pageref{פרק מב}
                        \\newline {\\small {\\locf{חתימה:}}
‏בָּר֤וּךְ | יְהֹוָ֣ה אֱ֭לֹהִים אֱלֹהֵ֣י יִשְׂרָאֵ֑ל עֹשֵׂ֖ה נִפְלָא֣וֹת לְבַדּֽוֹ׃                        \\newline
‏וּבָר֤וּךְ | שֵׁ֥ם כְּבוֹד֗וֹ לְע֫וֹלָ֥ם וְיִמָּלֵ֣א כְ֭בוֹדוֹ אֶת־כֹּ֥ל הָאָ֗רֶץ אָ֘מֵ֥ן | וְאָמֵֽן׃                        \\newline
                         ‏כׇּלּ֥וּ תְפִלּ֑וֹת דָּ֝וִ֗ד בֶּן־יִשָֽׁי׃}
                        \\newline
                        \\newline ספר ג {\\hfill} \\textcolor{red}{פרק עג}{\\hspace{1em}} עמוד \\pageref{פרק עג}
                        \\newline {\\small {\\locf{חתימה:}} ‏בָּר֖וּךְ יְהֹוָ֥ה לְעוֹלָ֗ם אָ֘מֵ֥ן | וְאָמֵֽן׃}
                        \\newline
                        \\newline ספר ד {\\hfill} \\textcolor{red}{פרק צ}{\\hspace{1em}} עמוד \\pageref{פרק צ}
                        \\newline {\\small {\\locf{חתימה:}} ‏בָּ֤רֽוּךְ יְהֹוָ֨ה אֱלֹהֵ֪י יִשְׂרָאֵ֡ל מִן־הָ֤עוֹלָ֨ם | וְעַ֬ד הָעוֹלָ֗ם וְאָמַ֖ר כׇּל־הָעָ֥ם אָמֵ֗ן הַֽלְלוּ־יָֽהּ׃}
                        \\newline
                        \\newline ספר ה {\\hfill} \\textcolor{red}{פרק קז}{\\hspace{1em}} עמוד \\pageref{פרק קז}
                        
                        \\pend\\ledpb"""
        else:
            text+= "\\pstart"
        for num, chapter in book['chapters'].items():
            if(sec_name in ["Psalms","Job","Proverbs"]):
                # Add perek as header on new page
                text += "\n\\pstart[\\subsection*{\\textcolor{red}{"+"פרק " + num + "}}]"
            else:
                text += "\n\\ledsidenote{{\loc{"+ num +" פרק" +"}}}" #Need to flip order bec the sidienote seems to use a LTR space
            for pseudoverse in chapter.items():
                psv_psn, psv_contents = pseudoverse
                if ((psv_psn != '0') and (psv_psn != 'תתת')):
                    #text += "\\setline{" + gimatria(psv_psn) + "}\\startlock\n"
                    text += "\n{\\loc{ " + psv_psn + "}~}\u200F"
                minirow = _MINIROW(*psv_contents)
                if(not (len(minirow.CP)>0)):
                    continue
                # print(get_full_loc(minirow.CP))
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
                    output = wtel_to_str(wikitext_el)
                    if output is None:
                        print(f"ERR! None output for: {wikitext_el}")
                        output = ""  # Use empty string if None
                    if(_rsubtype(wikitext_el)=="אתנח הפוך"):
                        text += output
                    else:
                        text += output
                if(sec_name in ["Psalms","Job","Proverbs"]):
                    text += "\\par"
            if(sec_name in ["Psalms","Job","Proverbs"]):
                text += "\\pend\n\\ledpb"
    if(sec_name not in ["Psalms","Job","Proverbs"]):
        text+= "\\pend"
    text += '''
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

    # Apply column marker post-processing if enabled
    if use_column_markers:
        if sec_name == "Psalms":
            text = psalms_postprocess(text)
        elif sec_name == "Job":
            text = job_postprocessing(text)
    # Generate filename based on settings
    suffix = ""
    if not using_ednotes:
        suffix += "_noNotes"
    if not use_column_markers:
        suffix += "_noColumns"
    outpath = f'out/MAM-{sec_name}{suffix}.tex'
    with _openw(outpath) as fpo:
        fpo.write(text)
    return outpath

import subprocess
def tex_to_pdf(tex_file):
    # Get the directory and filename
    dir_path = os.path.dirname(tex_file)
    file_name = os.path.splitext(os.path.basename(tex_file))[0]

    # Change to the directory containing the .tex file
    original_dir = os.getcwd()
    os.chdir(dir_path)

    # Run pdflatex four times
    for _ in range(5):
        # subprocess.run(['xelatex', '-interaction=nonstopmode', file_name + '.tex'])
        subprocess.run(['xelatex', '-interaction=nonstopmode', file_name + '.tex'])
    subprocess.run(['xelatex', '-interaction=nonstopmode', file_name + '.tex'])

    # Change back to the original directory
    os.chdir(original_dir)

    # Return the path to the generated PDF
    return os.path.join(dir_path, file_name + '.pdf')

def main():
    """Main function to generate TEX files with different settings."""
    global using_ednotes, use_column_markers

    # Test with a small book first (Ruth)
    test_books = ['Ruth', 'Psalms']

    for book in test_books:
        print(f"\n{'='*60}")
        print(f"Processing {book}")
        print(f"{'='*60}")

        # Generate with notes and column markers
        print(f"\nGenerating {book} with notes and column markers...")
        using_ednotes = True
        use_column_markers = True
        try:
            tex_file = output_to_tex(book)
            print(f"Generated: {tex_file}")
        except Exception as e:
            print(f"Error generating with notes: {e}")
            import traceback
            traceback.print_exc()

        # Generate without notes
        print(f"\nGenerating {book} without notes...")
        using_ednotes = False
        use_column_markers = True
        try:
            tex_file = output_to_tex(book)
            print(f"Generated: {tex_file}")
        except Exception as e:
            print(f"Error generating without notes: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()


