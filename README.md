## Twitter mass Downloader.

This is a simple app of which sole purpose is to download images from Twitter for strictly personal, non-commercial use.

It takes a list of Twitter status URLs as an input and outputs as many image files in PNG format as the input tweets have as their contents.
___
## How to use

To use the files in this repository as-is, you need to create a Python Virtual environment and to edit `template_tokens.json` with your own Twitter app Tokens.
___
## Json Input

This app takes an input in the form of `input.json`, this input file is formated to allow for sub-folder creation as easily as possible. It is currently formated as follows : 
```json
{
    "sub_folder/00": "url",
    "sub_folder/01": "url",
    "sub_folder/03": "url",
    "sub_folder/a": "url",
    "sub_folder/b": "url",
    "sub_folder/z": "url",
    "another_sub_folder": "url",
    "__none__": "url",
    "": "url"
}
```

#### Further explanations:

Here the json keys are used as sub-folder names, **note that anything after `/` will be ignored, as it is used to distinct "indexes" to avoid keys overriding each others.**

The keys `"__none__"` and `""` will be considered as "no sub-folder specified", creating the images in the `output/` folder itself, to put multiple images in a null sub-folder, `"__none__"` will accepts indexes, so it can be used as shown below to download multiple files in the root of `output/`: 

```json
"__none__00": "...", 
"__none__01": "...", 
"__none__02": "..."
```

#### The Folder list:

the Folder list is a special key that can be added to `input.json`, it goes as follow :

```json
"folder_list": {
  "fo1": "my_first_folder",
  "fo2": "my_second_folder",
  "fo3": "my_third_folder"
}
```

The first key in each element is used as a "shortcut name" for the full name, this is meant to make it easier to keep track of long sub-folder names, and also as a way for the user to save the folders they used previously if they want to re-use them.

The Folder list keys are used as follows :

```json
{
  "fo1": "url...",
  "fo2": "url...",
  "fo3": "url...",
  
  "folder_list": {
    "fo1": "my_first_folder",
    "fo2": "my_second_folder",
    "fo3": "my_third_folder"
  }
}
```

Each of the 3 URLs above will go to the folder specified before them using the shortcuts. If the name specified isn't found in the list, it will be used as the folder's name to create a unique folder without referring to the list.