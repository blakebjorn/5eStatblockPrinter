import sys
reload(sys)
sys.setdefaultencoding("UTF8")
import re
import os
import time
import hashlib
import webbrowser
from functools import partial

try:
    import yaml
    import jinja2
    from unidecode import unidecode
    from PySide import QtGui, QtCore, QtWebKit
except ImportError:
    import pip
    proc = raw_input("Modules need to be installed to continue. Download and Install:\n"+"\n".join(("PyYaml","Jinja2","Unidecode","PySide","\n(Y/N)?")))
    if proc.upper() in ("YES","Y"):
        pip.main(['install','-r','requirements.txt'])
        import yaml
        import jinja2
        from unidecode import unidecode
        from PySide import QtGui, QtCore, QtWebKit
    else:
        print "Closing in 5 Seconds."
        time.sleep(5)
        sys.exit()


def compile_ui_files():
    """
    Stores a list of all the .ui files in the current directory.
    If the UI changes since last startup, re-compile with pyside-uic before importing.
    """

    if os.path.isfile("uiHashDigests.yml"):
        with open("uiHashDigests.yml",'rb') as file_:
            uiDigests = yaml.load(file_)
    else:
        uiDigests = {}

    for fileName in (x for x in os.listdir(os.curdir) if x.endswith(".ui")):
        with open(fileName, 'rb') as file_:
            digest = hashlib.md5(file_.read()).hexdigest()
            print digest
        if fileName in uiDigests.keys() and digest == uiDigests[fileName]:
            continue
        else:
            print "Reloading UI"
            command = "pyside-uic "+fileName+" -o "+os.path.splitext(fileName)[0]+".py"
            print command
            os.system(command)
            uiDigests[fileName] = digest
            with open("uiHashDigests.yml", 'wb') as file_:
                yaml.safe_dump(uiDigests,file_)
            time.sleep(0.5)
if "--dev" in sys.argv:
    compile_ui_files()

import mainWindow

class MainWindow(QtGui.QMainWindow, mainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle("Statblock Printer")
        self.reportHTML = ""

        ## Load monster manual
        if not os.path.isfile("DM_Rules.html"):
            QtGui.QMessageBox.warning(self,'Error',"""No rules file is present. Save the DM rules site HTML in this directory as "DM_Rules.html" and restart the program.""")
            webbrowser.open("http://dnd.wizards.com/products/tabletop/dm-basic-rules")
        with open("DM_Rules.html",'r') as file_:
            monsterList = re.findall("""<dt id=".*?"><span>.*?</dd>""", file_.read().split("<span>List of Monsters</span>")[-1], re.DOTALL)

        self.monsterDict = {}
        self.monsterTreeParent = QtGui.QTreeWidgetItem(["Monsters"])
        for monster in monsterList:
            monsterName = re.search("(<span>)(.*?)(</span>)", monster).group(2).strip()
            type = re.search("""(<p class="type">)(.*?)(</p>)""", monster, re.DOTALL).group(2).strip()
            ac = re.search("""(<strong>Armor Class</strong>)(.*?)(</p>)""", monster, re.DOTALL).group(2).strip()
            hp = re.search("""(<strong>Hit Points</strong>)(.*?)(</p>)""", monster, re.DOTALL).group(2).strip()
            speed = re.search("""(<strong>Speed</strong>)(.*?)(</p>)""", monster, re.DOTALL).group(2).strip()

            statTable = re.search("""(<tbody>.*?<tr>.*?<td>)(.*?)(</td>.*?<td>)(.*?)(</td>.*?<td>)(.*?)(</td>.*?<td>)(.*?)(</td>.*?<td>)(.*?)(</td>.*?<td>)(.*?)(</td>)""", monster, re.DOTALL)
            STR = statTable.group(2).strip()
            DEX = statTable.group(4).strip()
            CON = statTable.group(6).strip()
            INT = statTable.group(8).strip()
            WIS = statTable.group(10).strip()
            CHA = statTable.group(12).strip()

            damResistances = re.search("""(<strong>Damage Resistances</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            damImmunities = re.search("""(<strong>Damage Immunities</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            conditionImmunities = re.search("""(<strong>Condition Immunities</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            savingThrows = re.search("""(<strong>Saving Throws</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            skills = re.search("""(<strong>Skills</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            senses = re.search("""(<strong>Senses</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            languages = re.search("""(<strong>Languages</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            challenge = re.search("""(<strong>Challenge</strong>)(.*?)(</p>)""", monster, re.DOTALL)
            actionBlock = re.search("""<h5>Actions</h5>.*?(<p class|</div>|<h5>Legendary Actions)""", monster, re.DOTALL)
            legendaryActionBlock = re.search("""<h5>Legendary Actions</h5>.*?(<p class|</div>)""", monster, re.DOTALL)

            specialTraitList = [x[1] for x in re.findall("""(<p class="special_trait">)(.*?)(</p>)""", monster, re.DOTALL) if len(x)==3]
            actionList = [x[1] for x in re.findall("""(<p>)(.*?)(</p>)""", actionBlock.group(0) if actionBlock is not None else "", re.DOTALL) if len(x) == 3]
            legendaryActionList = [x[1] for x in re.findall("""(<p>)(.*?)(</p>)""", legendaryActionBlock.group(0) if legendaryActionBlock is not None else "", re.DOTALL) if len(x) == 3]
            lore = re.search("""(<p class="lore">)(.*?)(</p>)""", monster, re.DOTALL)


            self.monsterDict[monsterName] = {
                "monsterName":monsterName,
                "monsterType":type,
                "armorClass":ac,
                "hitPoints":hp,
                "speed":speed,
                "STR":STR,
                "DEX": DEX,
                "CON": CON,
                "INT": INT,
                "WIS": WIS,
                "CHA": CHA,
                "damageResistances":damResistances.group(2).strip() if damResistances is not None else "",
                "damageImmunities": damImmunities.group(2).strip() if damImmunities is not None else "",
                "conditionImmunities": conditionImmunities.group(2).strip() if conditionImmunities is not None else "",
                "savingThrows": savingThrows.group(2).strip() if savingThrows is not None else "",
                "skills": skills.group(2).strip() if skills is not None else "",
                "senses": senses.group(2).strip() if senses is not None else "",
                "languages": (languages.group(2).strip() if languages.group(2).strip() != '\xe2\x80\x94' else "") if languages is not None else "",
                "challenge": challenge.group(2).strip() if challenge is not None else "",
                "specialTraits" : specialTraitList,
                "actions": actionList,
                "legendaryActions":legendaryActionList,
                "lore" : lore
            }

            monsterTreeItem = QtGui.QTreeWidgetItem([monsterName])
            self.monsterTreeParent.addChild(monsterTreeItem)

        self.ruleBookTreeWidget.addTopLevelItem(self.monsterTreeParent)

        self.ruleBookTreeWidget.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self.ruleBookTreeWidget.itemSelectionChanged.connect(self.preview_rule_selection)

        self.ruleBookTreeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ruleBookTreeWidget.customContextMenuRequested.connect(self.prepare_rule_menu)

        self.webView = QtWebKit.QWebView()
        self.settings = self.webView.settings()
        self.settings.setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True)

        self.rightFrameLayout.insertWidget(0, self.webView)
        self.jinjaTemplate = jinja2.Environment(loader=jinja2.FileSystemLoader(os.curdir)).get_template("wideTemplate.html")
        self.reportTemplate = jinja2.Environment(loader=jinja2.FileSystemLoader(os.curdir)).get_template("reportTemplate.html")

        self.previewPushButton.clicked.connect(self.create_html_view)
        self.savePushButton.clicked.connect(self.save_html_view)
        self.show()

    def create_html_view(self):
        # build list of lists of items to include.
        self.reportTemplate = jinja2.Environment(loader=jinja2.FileSystemLoader(os.curdir)).get_template("reportTemplate.html")

        outputList = []
        for topLevelIndex in range(self.selectedItemsTreeWidget.topLevelItemCount()):
            topLevelItem = self.selectedItemsTreeWidget.topLevelItem(topLevelIndex)
            for childIndex in range(topLevelItem.childCount()):
                outputList.append(self.build_monster_dict(topLevelItem.child(childIndex).text(0)))


        print outputList
        self.reportHTML = self.reportTemplate.render(outputList=outputList)
        try:
            self.webView.setHtml(self.reportHTML)
        except:
            raise

    def save_html_view(self):
        self.create_html_view()
        if self.reportHTML:
            with open("Current Report.html",'w') as file_:
                file_.write(self.reportHTML)

            printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            printer.setOutputFileName("CurrentReport.pdf")
            self.webView.print_(printer)

    def prepare_rule_menu(self, pos):
        items = self.ruleBookTreeWidget.selectedItems()
        print (item.text(0) for item in items)
        menu = QtGui.QMenu()
        action = QtGui.QAction("Add", menu)
        action.triggered.connect(partial(self.pin_item, [(item.parent().text(0), item.text(0)) for item in items]))
        menu.addAction(action)
        menu.exec_(self.ruleBookTreeWidget.mapToGlobal(pos))

    def pin_item(self, inputList):
        for inputTuple in inputList:
            # Creates top level tree widget if it doesn't exist yet
            for topLevelIndex in range(self.selectedItemsTreeWidget.topLevelItemCount()):
                if inputTuple[0] in self.selectedItemsTreeWidget.topLevelItem(topLevelIndex).text(0):
                    currentParent = self.selectedItemsTreeWidget.topLevelItem(topLevelIndex)
                    break
            else:
                currentParent = QtGui.QTreeWidgetItem([inputTuple[0]])
                self.selectedItemsTreeWidget.addTopLevelItem(currentParent)

            for childIndex in range(currentParent.childCount()):
                if inputTuple[1] in currentParent.child(childIndex).text(0):
                    self.statusBar().showMessage("Already added.",2000)
                    break
            else:
                childItem = QtGui.QTreeWidgetItem([inputTuple[1]])
                currentParent.addChild(childItem)

    def build_monster_dict(self,name):
        d = self.monsterDict[name]
        for key in d.keys():
            if isinstance(d[key], list):
                for i in range(len(d[key])):
                    try:
                        d[key][i] = unidecode(unicode(d[key][i]))
                    except:
                        d[key][i] = unicode(d[key][i]).decode('latin1')
            else:
                try:
                    d[key] = unidecode(unicode(d[key]))
                except:
                    d[key] = unicode(d[key]).decode('latin1')
        return d

    def preview_rule_selection(self):
        selection = self.ruleBookTreeWidget.selectedItems()
        d = self.build_monster_dict(selection[0].text(0))
        try:
            self.webView.setHtml(self.jinjaTemplate.render(d))
        except:
            print d
            raise


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())

