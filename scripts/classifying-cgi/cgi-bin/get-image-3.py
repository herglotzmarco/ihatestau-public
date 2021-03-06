#!/usr/bin/env python3.6

import cgi
import cgitb; cgitb.enable()
import sys
import os
import os.path
import shutil
import random
import urllib.parse
import sqlite3
from datetime import datetime

import config

print('Content-Type: text/html; charset=UTF-8')
print('Cache-Control: no-cache')
print()

print('''<title>iHateStau Camera Classification</title>''')


db = sqlite3.connect(config.dbfile)
db.row_factory = sqlite3.Row

imgs = db.execute(
''' select SHOTS.FILE_A, SHOTS.FILE_B, SHOTS.MAP_VAL,
        POINTS.MASK_A, POINTS.MASK_B, POINTS.POINT_ID,
        POINTS.CAMERA_A, POINTS.CAMERA_B, SHOTS.SHOT_ID,
        POINTS.DESCRIPTION, SHOTS.TIMESTAMP, SHOTS.HUMAN_EVAL
    from SHOTS
    join POINTS on SHOTS.POINT_ID = POINTS.POINT_ID
    where (FILE_A is not null or FILE_B is not null)
        and SHOTS.HUMAN_EVAL is null
        and (SHOTS.MAP_VAL = ? or SHOTS.MAP_VAL = ?)
    order by RANDOM()
    limit 100
    ''', (0xff0000, 0xffe500))


print('<h1>Classify Images: Random Probable Jams</h1>')
print('<form action=classify-image-2.py method=POST name=classify_form>')

i = 0
for img in imgs:
    print('<table cellspacing=10 style="background-color: #{:06x}">'.format(img['MAP_VAL']))
    print('<tr><td>')
    print('<a href="{}/{}">'.format(config.cameraurl, img['FILE_A']))
    print('<div style="position:relative; width:320px; height:240px; background-color:black">')
    print('<img with=320 height=240 style="position:absolute; top:0; left:0;" src="{1}/{0}">'.format(img['FILE_A'], config.cameraurl))
    print('<img with=320 height=240 style="position:absolute; top:0; left:0; opacity:0.8" src="{1}/{0}">'.format(img['MASK_A'], config.maskurl))
    print('</div></a>')
    print('<td>')
    print('<a href="{}/{}">'.format(config.cameraurl, img['FILE_B']))
    print('<div style="position:relative; width:320px; height:240px; background-color:black">')
    print('<img with=320 height=240 style="position:absolute; top:0; left:0" src="{1}/{0}">'.format(img['FILE_B'], config.cameraurl))
    print('<img with=320 height=240 style="position:absolute; top:0; left:0; opacity:0.8" src="{1}/{0}">'.format(img['MASK_B'], config.maskurl))
    print('</div></a>')
    print('<td style="background-color: white; color: black;">')

    print('<input type=hidden name=shotid_{} value="{}">'.format(i, img['SHOT_ID']))

    def checked_if_eval(val):
        if img['HUMAN_EVAL'] == val:
            return ' checked="checked"'
        else:
            return ''

    print('<label><input type=radio name=human_eval_{} value=nil {}>Not Set</label>'.format(i, checked_if_eval(None)))
    print('<label><input type=radio name=human_eval_{} value=fluid {}>Fluid</label>'.format(i, checked_if_eval('fluid')))
    print('<label><input type=radio name=human_eval_{} value=jam {}>Jam</label>'.format(i, checked_if_eval('jam')))
    print('<label><input type=radio name=human_eval_{} value=unsure {}>Unsure</label>'.format(i, checked_if_eval('unsure')))

    print('</table>')

    i = i + 1

print('<input type=hidden name=redirect_to value="{}">'.format(cgi.escape('get-image-3.py')))
print('<input type=hidden name=pic_count value={}>'.format(i))
print('<input type=submit>')
print('</form>')

print('''<script>
document.forms.classify_form.addEventListener('change', function(e) {
    var name = e.target.name;
    console.log('onchange! ' + name)
    console.log(e)
    if (name.startsWith('human_eval_')) {
        var num = parseInt(name.match(/\d+$/)[0]);
        console.log('num = ' + num);

        for (i = num-1; i >= 0; --i) {
            if (document.forms.classify_form['human_eval_'+i].value != 'nil') {
                console.log('break at i=' + i + ' value=' + document.forms.classify_form['human_eval_'+i].value);
                break;
            }

            document.forms.classify_form['human_eval_'+i].value = document.forms.classify_form[name].value;
        }
    }
}, false);
</script>''')


