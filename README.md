# 5eStatblockPrinter
Print statblocks from the basic rules in pretty formats. 
Python 2 compatible only, due to move from QtWebKit to QtWebEngine in PyQt5 and questionable QPrinter functionality at the time being.

# Installation
Download the DM rules (web format) from the WOTC site and save the html page as "DM_Rules.html" in the program directory
> python D&DPrinter.py 

User will be prompted to install requirements.txt on startup if they aren't present.

# Usage
DM rulebook will be crawled on application startup and monster stat blocks will be extracted. All monsters will be listed in the left pane. Right/double click on a monster to add it to the current active list. Active list can be previewed in the center pane, or saved to PDF for printing.

[[https://github.com/blakebjorn/5eStatblockPrinter/blob/master/Examples/Preview.png|alt=octocat]]

