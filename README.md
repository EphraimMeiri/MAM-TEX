# MAM-TEX
 
This Git repository uses the parsed version of [MAM (Miqra According to the Masorah)](https://en.wikisource.org/wiki/User:Dovi/Miqra_according_to_the_Masorah) prepared by bdenckla.

There are two python scripts: to_TEX which can convert one of the json files to a .tex file that can be compiled to pdf. The script converts each of the MAM templates to an appropriate TEX layout (full inplementation still in development). A major goal is adding all documentation as notes to the main text. These are added as 'critical notes' using the reledmac package. Note that compiling to TEX will require installing all the involved TEX packages. Also note that reledmac requries a 3-pass compliation. 

to_html creates a html file of the nusach notes on each verse in each json file.

Some example tex, html, and pdf files are in the 'out' directory.
