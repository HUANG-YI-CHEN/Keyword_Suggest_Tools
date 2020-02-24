# Google/Bing/Youtub/Yahoo Keyword Suggest

input `keyword`, and ouput is browser autocomplete.
* input : `'smartphone'`
* ouput : `['smartphone', 'smartphone market share', 'smartphone deals', 'smartphone 2019', 'smartphone comparison', 'smartphone中文', 'smartphone link', 'smartphone addiction', 'smartphone tycoon', 'smartphone icon', 'smartphone 中文', 'smartphone projector 2.0']`

# Getting Started
## Installation Environment
* Microsoft Windows`+`

## System Requirements
* Python `3+`

## Mounting Kit  
* pip freeze > requirements.txt (Output installed packages in requirements)
```
pip install -r requirements.txt
```

## Execute Program
```
python main.py
```
or

```
python main.py 1 0 1000
```
## Constructor
* keyword = '', <type 'str'>, input keyword.
* proxy_switch = False, <type 'boolean'>, input True or False.
* dicts = {}, <type 'dict'>, get suggest response.
* json = '', <type 'str'>, get suggest response JSON string.
* tokens = [], <type 'list'>, get suggest token lists.

## Fuction
* get(), no input. Return suggest response ( type <dict> ).
* format_JSON(mode), mode: input 'all', 'google', 'bing', 'youtube', or 'yahoo'. Return JSON String <type 'str'>.
* get_tokens(dict), dict: input dicts['all'], dicts['google'], dicts['bing'], dicts['youtube'], or dicts['yahoo']. Return token lists <type 'list'>.
* generator(self), no input. Render response
* set_proxy_switch(params), params: True or False. Set Proxy, which turn on or off.

## Example
```
keyword = [u'蔡英文',u'馬英九',u'柯文哲']
for i in range(0,3,1):
    a = time.time()
    response = suggest(keyword[i])
    for i in response.dicts:
        print(i,response.dicts[i])
    # for i in response.tokens:
    #     print(i)
    print("spend time:",time.time()-a)
```

## Configuration File
Establish configuration file(`config.ini`), which is placed under this project directory
* `config.ini` is following :
    *   [database]
        *   hostname=localhost
        *   username=
        *   password=
        *   database=

    *   [mode]
        *   Run=3
        *   0=Parser
        *   1=Google Search & Parser
        *   2=Bing Search & Parser
        *   3=Yahoo Search & Parser
        *   4=Google/Bing/Youtube/Yahoo Search & Parser
        *   switch=4

    *   [control]
        *   domainkeyword=智慧型手機
        *   counter=1
        *   divisor=1
        *   remainder=0

## Subsequent Settlement
To be continued ......