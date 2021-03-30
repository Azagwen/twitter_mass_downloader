## Twitter mass Downloader.

This is a simple app of which sole purpose is to download images from Twitter for strictly personal, non-commercial use.

It takes a list of Twitter status URLs as an input and outputs as many image files in PNG format as the input tweets have as their contents.
___
## How to use

To use the files in this repository as-is, you need to create a Python Virtual environment and to edit `template_tokens.json` with your own Twitter app Tokens.
___
## Json Input

This app takes an input in the form of `input.json`, this input file is formated to allow for sub-folder creation as easily as possible. It is currently formated as follows : 
```
{
    "sub_folder__00": "url"
    "sub_folder__01": "url"
    "sub_folder__03": "url"
    "another_sub_folder": "url"
    "__none__": "url"
    "": "url"
}
```

#### Further explanations:

Here the keys are used as sub-folder names, note that anything after the double "_" will be ignored, as it is used to distinct "indexes" to avoid keys overriding each others.

The keys `"__none__"` and `""` will be considered as "no sub-folder specified", creating the images in the `output/` folder itself, to put multiple images in a null sub-folder, `"__none__"` will accepts indexes, so it can be used as shown below to download multiple files in the root of `output/`: 

```
"__none__00": "...", 
"__none__01": "...", 
"__none__02": "..."
```

