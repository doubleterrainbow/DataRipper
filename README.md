
# Usage

You'll need 3 exports to extract data from the game.

1. All assets from Asset Studio
2. assets.xml from Asset Studio
2. Code from DnSpy

Once you have those 3 things, you can run the program and select the proper directories. The output directory can be any folder. A new folder with whatever you put in the Game Version textbox will be created and all txt files will be placed in there.

Then, you should be able to click Start and see things happening.

There is some error handling, but if you ever run into any unexpected error you can either try again or share your `debug.log` file (which is in the output folder you specified earlier).

## Asset Studio
Asset Studio can be found [here](https://github.com/Perfare/AssetStudio/releases).

To use it, grab the directory of the game found in SteamApps/common, and drag it into Asset Studio.

Then go to File > Export > All Assets. You'll want to keep track of where these files are, because you'll need them later This will take a _while_. 

You'll also need the XML file. Go to Export > Asset List to XML > All Assets. **Put this in the same folder as before**

If at any point Asset Studio asks to open a directory without any explanation, you're looking for the Managed folder inside the Sun Haven directory.

## DnSpy
DnSpy can be found [here](https://github.com/dnSpy/dnSpy)

Once dnSpy is open, go to File > Open and select `Sun Haven\Suh Haven_Data\Managed\SunHaven.Core.dll`

File > Export to Project

Pick any folder to export this, but keep the location in mind as you will need it later.

# Running
This project uses [poetry](https://python-poetry.org/docs/) to manage packages and run a virtual environment.

Installation instructions are on their docs, but here's a tldr:

Linux, macOS:
```
curl -sSL https://install.python-poetry.org | python3 -
```

Powershell:
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

To run:
```
poetry run python app.py
```

