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



def wtel_to_str(wtel):  # returns a TEX string
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
        text = "{אות-ג,"+wtel['tmpl'][1][0] +"}"
        return text
    elif (_subtype(key, wtel) == "מ:קמץ"):
        return wtel['tmpl'][1][0][2:]
        # We go for the grammatical forms here
    elif (_subtype(key, wtel) == "מ:לגרמיה"):
        return "\u2008" + "| "
    elif (_subtype(key, wtel) == "מ:פסק"):
        return " | "
    elif (tmpl_subtype == "ירח בן יומו"):
        return "֪"
    elif(tmpl_subtype=='מ:גרש ותלישא גדולה'):
        return "֜‍֠"
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
    elif (tmpl_subtype == "ססס"):
        # TODO: This is not the way it is displayed on wikisource
        return "{ס}    "
    elif (tmpl_subtype == "סס"):
        # TODO: This is not the way it is displayed on wikisource
        return "{ס}    " #TODO: replace spaces with correct tab character
    elif (tmpl_subtype== "פפ"):
        return "{פ}<br>"
    elif (tmpl_subtype== "פסקא באמצע פסוק"):
        text = wtel_to_str(wtel['tmpl'][1][0])
        text += "{{פסקא באמצע פסוק}}"
        return text
    elif(tmpl_subtype=='מ:ירושלם'):
        text= wtel['tmpl'][1][0] +wtel['tmpl'][2][0]
        text+= "&#847;ִם"
        return text
    elif(tmpl_subtype=="גלגל"):
        return "֪"
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
    for char in heb:
        val+= MISPAR_HECHRACHI[char]
    output= str(val)
    return output

def loc_to_line(strs):
    if(len(strs)<4):
        return ""
    if(strs[0][0]=='נוסח'):
        strs=strs[1][0]['tmpl']
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
def get_nussach_note(wtel):
    if isinstance(wtel, str):
        return ""
    keys = tuple(wtel.keys())
    key = keys[0]
    if (_subtype(key, wtel) != "נוסח"):
        return ""
    lemma = "<b>"+wtel_to_str(wtel['tmpl'][1][0])
    text = lemma + "</b>- "
    note_contents = ""
    for arg in wtel['tmpl'][2:]:
        if isinstance(arg, str) or isinstance(arg, dict):
            note_contents += " ## "+wtel_to_str(arg)
        else:
             for arg_wtel in arg:
                if(type(arg_wtel)==str):
                    note_contents+=arg_wtel
                else:
                    note_contents += wtel_to_str(arg_wtel)
        note_contents+= " | "

    text += note_contents +" \n"
    return text

def get_nussachs(sec_name):
    text="""<html dir="rtl">
<head>
  <meta charset="UTF-8">
</head>
    """
    inpath = f'miqra-json/MAM-{sec_name} modified.json'
    with open(inpath, encoding='utf-8') as fpi:
        sec = json.load(fpi)
    # chapent: chaptered entity (book or sub-book)
    for chapent in sec['body']:
        #text += '<br><br>' + (sec['body'][0]['book_name']) + "<br>"
        for num, chapter in chapent['chapters'].items():
            #text += "<br>פרק " + num + "<br>"
            for pseudoverse in chapter.items():
                psv_psn, psv_contents = pseudoverse
                #text += "<br>פסוק " + psv_psn + "<br>"
                minirow = _MINIROW(*psv_contents)
                if(not (len(minirow.CP)>0)):
                    continue

                # if(chapent['book_name']=='ספר תרי עשר'):
                #     print("Stop")
                if(minirow.CP[0]['tmpl'][0][0]=='נוסח'):
                    print("נוסח בסדר!")
                    text+= "\n"+get_full_loc(minirow.CP)+"\n"
                    text+= minirow.CP[0]['tmpl'][2][0]
                    for note in minirow.CP[0]['tmpl'][3:]:
                        text+= " | "+note[0]
                    # if(len(minirow.CP[0]['tmpl'])>3):
                    #     print("Stop!")
                    #     print(minirow.CP[0]['tmpl'])
                    text +="\n"
                    # print(minirow.CP[0]['tmpl'])

                fulloc=get_full_loc(minirow.CP)
                # if(fulloc=="ישעיהו כז יא"):
                #     print(fulloc)
                print(fulloc)
                # print(chapent['book_name']+" " + loc_to_line(minirow.CP[0]['tmpl'])+" "+str(type(minirow.CP[0]['tmpl'][1][0])))
                #print(loc_to_line(minirow.D))
                for wikitext_el in minirow.EP:
                    output= get_nussach_note(wikitext_el)
                    if(output!= ""):
                        # text +=  '\n' + (chapent['book_name']) + " פרק "+ num + " פסוק "+psv_psn +"\n"
                        text += '\n' + get_full_loc(minirow.CP) + "\n"
                        text += output
    outpath = f'out/MAM-{sec_name}-הערות נוסח.html'
    import re
    br = re.compile(r"(\r\n|\r|\n)")  # Supports CRLF, LF, CR
    text = br.sub(r"<br />\n", text)  # \n for JavaScript
    with _openw(outpath) as fpo:
        fpo.write(text)


def main():
    # #    output_to_tex('Ruth')
    get_nussachs('Torah')  #Done
    get_nussachs('NevRish')   #Done
    get_nussachs('NevAch')   #Done
    get_nussachs('SifEm')
    get_nussachs('ChamMeg') #Done
    get_nussachs('KetAch')   #Done
if __name__ == "__main__":
    main()


