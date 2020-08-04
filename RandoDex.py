import tkinter as tk
from tkinter import filedialog as tk
from math import *
import json, os
from PIL import Image, ImageTk
from functools import partial

def indexconvert(ind):
    return ("00" + str(ind))[-3:]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Application(tk.Frame):
    pokebutton = []
    isFileLoaded = False
    selected = None
    routelist = []
    pokelist = []
    
    def __init__(self, master=None):
        super().__init__(master)
        self.loadjson()
        self.master = master
        self.master.title("RandoDex")
        self.ico = self.GetIconImage()
        self.master.iconphoto(True, self.ico)
        self.includeSwarms = tk.BooleanVar()
        self.gamename = tk.StringVar()
        self.pack()
        self.AskGame()

    def create_widgets(self):
        #creates all of the items in the program
        #holds the file selection part of the program
        self.fileselectionframe = tk.Frame(self)
        self.fileselectionframe.pack(side="top")
        #creates file selection text bar
        self.filename = tk.StringVar()
        self.filetextinput = tk.Entry(self.fileselectionframe, width=100, state="readonly", textvariable=self.filename)
        self.filetextinput.pack(side="left")
        #creates file selection button
        self.filebuttoninput = tk.Button(self.fileselectionframe, text="Browse", command=self.fileBrowser)
        self.filebuttoninput.pack(side="left")
        #creates file load button
        self.fileloadbutton = tk.Button(self.fileselectionframe, text="Load", command=self.fileLoader)
        self.fileloadbutton.pack(side="left")
        #holds the pokemon selection buttons and their scrollbar
        self.masterpokeframe = tk.Frame(width=838)
        self.masterpokeframe.pack(side="left")
        #holds the frame for pokemon selection buttons so that its scrollable
        self.pokeboxesframe = tk.Canvas(self.masterpokeframe)
        self.pokeboxesframe.config(yscrollincrement=50)
        self.pokeboxesframe.pack(side="left")
        #holds the pokemon selection buttons
        self.smallframe = tk.Frame(width=838)
        #creates pokemon selection buttons
        for i in range(0, self.gameinfo.get("dexsize")):
            self.pokebutton.append(tk.Button(self.smallframe, anchor='s'))
            pokeimage = self.GetPokeImage(i+1, "SMALL")
            self.pokebutton[i]["image"] = pokeimage
            self.pokebutton[i].image = pokeimage
            self.pokebutton[i].config(width=50, height=50, command=partial(self.selectpoke, i))
            self.pokebutton[i].grid(column=i%15, row=floor(i/15))
        self.pokeboxesframe.create_window(0, 0, anchor='nw', window=self.smallframe)
        #creates pokemon selection buttons scrollbar
        self.pokeboxscroll = tk.Scrollbar(self.masterpokeframe, command=self.pokeboxesframe.yview)
        self.pokeboxesframe.config(yscrollcommand=self.pokeboxscroll.set, height=10000, width=836, scrollregion=self.gameinfo.get("scrollregion"))
        self.pokeboxscroll.pack(side="left", fill="y")
        #holds the bigger pokemon image box and map image box
        self.pokeinfoframe = tk.Frame()
        self.pokeinfoframe.pack(side="right")
        #creates bigger pokemon image box
        self.pokepic = tk.Label(self.pokeinfoframe, height=350, width=350, relief="groove")
        pokeimage = self.GetPokeImage(0, "BIG")
        self.pokepic["image"] = pokeimage
        self.pokepic.image = pokeimage
        self.pokepic.pack()
        #creates map image box
        self.mappic = tk.Canvas(self.pokeinfoframe, relief="groove")
        self.mappic.config(height=self.gameinfo.get("mapcanvasheight"))
        self.mappic.config(width=self.gameinfo.get("mapcanvaswidth"))
        mapimg = self.GetMap()
        self.mappic.create_image((0, 0), image=mapimg, anchor="nw", tags="mapimg")
        self.mappic.image = mapimg
        self.mappic.pack()
        #used for testing self.mapdict
        #for i in self.mapdict.get(self.gamename).values():
        #    for j in i:
        #        self.mappic.create_rectangle(j, fill="red", outline="red", tags="rect")

    def GetPokeImage(self, dexnum, size):
        #receives the dex number and returns the image of a pokemon
        temp = {}
        if size == "SMALL":
            dexnum = indexconvert(dexnum)
            tempget = self.pokedict.get(dexnum, "notfound")
            if tempget != "notfound":
                temp = tempget.get("slug", "notfound")
            if temp != "notfound":
                pokename = temp.get("eng", "notfound")
            if pokename == "notfound":
                img = Image.open(resource_path("data/icons/unknown-gen5.png"))
                img = img.resize((90, 90), Image.ANTIALIAS)
            else:
                img = Image.open(resource_path("data/icons/" + pokename + ".png"))
                img = img.resize((90, 90), Image.ANTIALIAS)
        elif size == "BIG" and dexnum == 0:
            img = Image.open(resource_path("data/0.png"))
            img = img.resize((350, 350), Image.ANTIALIAS)
        elif size == "BIG":
            img = Image.open(resource_path(self.gameinfo.get("spritelocation") + str(dexnum) + ".png"))
            img = img.resize(self.gameinfo.get("spriteresize"), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def loadjson(self):
        #loads the .json that holds info for each pokemon
        with open(resource_path("data/pokemon.json"), encoding="utf8") as file:
            self.pokedict = json.load(file)
        with open(resource_path("data/locations.json"), encoding="utf8") as file:
            self.mapdict = json.load(file)
        with open(resource_path("data/gameinfo.json"), encoding="utf8") as file:
            self.gameinfo = json.load(file)

    def selectpoke(self, ind):
        #actions performed whenever a pokemon is selected as long as a file is loaded
        if not self.isFileLoaded:
            return
        #removes location visuals of previous pokemon
        for i in self.mappic.find_withtag("rect"):
            self.mappic.delete(i)
        #change big pokemon image to the selected pokemon
        pokeimage = self.GetPokeImage(ind+1, "BIG")
        self.pokepic["image"] = pokeimage
        self.pokepic.image = pokeimage
        #return previous selection button to normal
        if self.selected is not None:
            self.pokebutton[self.selected].config(relief="raised")    
        #change selected pokemon index and perform selection functions on it
        self.selected = ind
        self.pokebutton[ind].config(relief="sunken")
        #show new selection's location visuals on map
        temp = self.mapdict.get(self.gamename)
        for i in self.pokelist[ind][1:]:
            for j in temp.get(i):
                self.mappic.create_rectangle(j, fill="red", outline="red", tags="rect")
                
    def fileBrowser(self):
        #opens file dialog to select file
        self.filename.set(tk.askopenfilename(filetypes=[("Randomizer log files", "*.log")]))

    def fileLoader(self):
        #loads data from selected file
        #does nothing if no file has been browsed
        if self.filename is None:
            return                                                                      #add error message here
        #changes isFileLoaded flag and processes the data from the file
        self.isFileLoaded = True
        self.ParseFile()
        self.MakePokeList()

    def GetIconImage(self):
        #returns icon for program
        img = Image.open(resource_path("data/egg-manaphy.png"))
        img = img.crop(box=(26, 35, 41, 51))
        img = img.resize((500, 500), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def ParseFile(self):
        with open(self.filename.get(), 'r', encoding="utf-8") as file:
            doublelist = ["Rod", "Radio", "Smash"] #used when removing extraneous info
            setnum = 0 #used when removing extraneous info
            routelist = [] #the main list every route and pokemon is saved in
            locationnames = [] #the name of every location used to determine validity of user input
            hyphenpoke = ["Ho-Oh", "Porygon-Z"] #Stores names of pokemon with hyphens in their names
            swarms = ["Swarms", "Radio"] #encounters not to be included if includeSwarms is False
            line = file.readline()
            #skips every line until the encounter log
            while line != "--Wild Pokemon--\n":
                line = file.readline()
            #reads every line and edits it as its read and adds it to the route list
            while line != "\n":
                line = file.readline()
                setnum += 1
                hasEdit = False #used to flag if the type of catch was already removed due to being two words long
                hasBeenAdded = False #used when checking if a location is already in routelist
                tempstr = "" #used when concatenating location names after reading them from the file
                templist = [] #used to hold info before being added to routelist
                skipFlag = False 
                #skips swarm encounters if includeSwarms is set to False
                if not self.includeSwarms.get():
                    for i in swarms:
                        if i in line:
                            skipFlag = True
                if skipFlag:
                    continue
                #removes first few characters depending on the set number
                if setnum < 10:
                    tempstring = line[9:]
                elif setnum < 100:
                    tempstring = line[10:]
                elif setnum < 1000:
                    tempstring = line[11:]
                thesplit = tempstring.split()
                #finds where the list splits between locations and pokemon
                if len(tempstring) > 5:
                    index = thesplit.index('-')
                else:
                    break
                #deletes the type of catch and appearance rate
                for i in doublelist:
                    if i in thesplit:
                        del thesplit[index-3:index]
                        hasEdit = True
                if not hasEdit:
                    del thesplit[index-2:index]
                #readjusts split index
                if len(tempstring) > 5:
                    index = thesplit.index('-')
                else:
                    break
                #adds the location name to the templist and locationnames
                for i in thesplit:
                    if i != '-':
                        tempstr += i + ' '
                    else:
                        break
                templist.append(tempstr[:-1])
                if tempstr[:-1] not in locationnames:
                    locationnames.append(tempstr[:-1])
                #adds pokemon to templist
                for i in thesplit[index+1:]:
                    if (not i.startswith('Lv')) and (('-' not in i) or (i in hyphenpoke)):
                        templist.append(i)
                #edits templist to account for certain pokemon
                for i in templist:
                    ind = templist.index(i)
                    if "’" in i:
                        i = i.replace("’", "'")
                        templist[ind] = i.replace("’", "'")
                    if i == "Jr.":
                        if not templist[ind-1].endswith("Jr."):
                            templist[ind-1] += " Jr."
                        del i
                    elif i == "Mr.":
                        templist[ind] += " Mime"
                        del templist[ind+1]
                    elif i == "Farfetch'D":
                        templist[ind] = i.replace("D", "d")
                #adds the templist to the routelist if the area hasn't been added yet or appends if it has
                if routelist == []:
                    routelist.append(templist)
                    hasBeenAdded = True
                    index = 0
                elif templist[0] == routelist[-1][0]:
                    hasBeenAdded = True
                    index = -1
                elif templist[0] != routelist[-1][0]:
                    for i in routelist:
                        if i[0] == templist[0]:
                            hasBeenAdded = True
                            index = routelist.index(i)
                            break
                if not hasBeenAdded:
                    routelist.append(templist)
                else:
                    for i in templist[1:]:
                        routelist[index].append(i)
        #checks for and removes duplicate pokemon from routelist
        for i in routelist:
            tempset = []
            for j in i:
                if j not in tempset:
                    tempset.append(j)
            self.routelist.append(tempset)

    def MakePokeList(self):
        for i in range(1, 494):
            ind = indexconvert(i)
            temp = self.pokedict.get(ind)
            temp = temp.get("name")
            self.pokelist.append([temp.get("eng")])
        for i in self.pokelist:
            for j in self.routelist:
                if i[0] in j:
                    i.append(j[0])

    def GetMap(self):
        img = Image.open(resource_path("data/maps/" + self.gamename + ".png"))
        img = img.resize(self.gameinfo.get("mapsize"), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def AskGame(self):
        #Creates window that asks user which game they are playing
        self.gamename.set("None")
        self.firstframe = tk.Frame(self)
        self.firstframe.pack()
        for i, j in self.gameinfo.get("gamemenu"):
            b = tk.Radiobutton(self.firstframe, text=i, value=j, variable=self.gamename)
            b.pack(side="top", anchor="w")
        #Button to confirm selection
        b = tk.Button(self.firstframe, text="Select Game", command=self.SelectGame)
        b.pack(side="bottom")
        #Button to select whether to include difficult pokemon to acquire
        b = tk.Checkbutton(self.firstframe, text="Include Swarm/Radio Pokemon", variable=self.includeSwarms)
        b.pack(side="right")

    def SelectGame(self):
        #Deletes game selection window, opens application
        if self.gamename.get() == "None":
            b = tk.Toplevel(self)
            msg = tk.Label(b, text="Please select a game first")
            msg.pack()
            goback = tk.Button(b, text="Return", command=b.destroy)
            goback.pack()
            return
        elif self.gamename.get().startswith("notready"):
            b = tk.Toplevel(self)
            msg = tk.Label(b, text="Sorry, that hasn't been developed yet")
            msg.pack()
            return
        self.firstframe.destroy()
        self.gamename = self.gamename.get()
        self.gameinfo = self.gameinfo.get(self.gamename)
        self.master.geometry("1500x1000")
        self.create_widgets()
        self.pack()

root = tk.Tk()
app = Application(master=root)
app.mainloop()