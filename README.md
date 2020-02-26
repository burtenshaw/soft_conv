# Teen_conv

## Workflow

- `preprocess.py`
- `build.py`
- `annon.py`
- `validate.py`

## Preprocessing 

To build an anonymous json file run:

```python preprocessing```

```
  -h, --help           show this help message and exit
  --debug              get more info and examples from data errors
  --data DATA          directory of instant messaging conversations
  --platform PLATFORM  type of instant messages: 'fb' / 'wa'
  --out_dir OUT_DIR    directory of instant messaging conversations
```

Define the source of messages with `--data` and the type of platform with `--platfiorm`.

Data should be structured: 

```
--- #DATA_DIR#/
    --- school_name/
        --- instant_messaging_text_file.txt
        --- instant_messaging_text_file.txt
        --- instant_messaging_text_file.txt
        --- instant_messaging_text_file.txt
        --- instant_messaging_text_file.txt
    --- school_name/
    --- school_name/
    --- school_name/
    --- school_name/

```
**Whatsapp**
```python3 annon_schools_data.py --data #DATA_DIR# --platform wa```

**Facebook**
```python3 annon_schools_data.py --data #DATA_DIR# --platform fb```

## Build
```
python3 build.py
```

```
  -h, --help            show this help message and exit
  --data DATA           directory of preprocessed json
  --append APPEND       directory of previously build dataset
  --out_dir OUT_DIR     directory of instant messaging conversations
  --version VERSION     filename addition for versions
  --alpha ALPHA         alpha data file
  --key KEY             FOREIGN KEY : json file with dictionary of alpha
                        usernames to chatter_ids for legacy matching
  --whatsapp WHATSAPP   medium specific build
  --facebook FACEBOOK   medium specific build
  --user_matching USER_MATCHING
                        perform validated matching on user names with alpha
                        chatter id
  --manual_annotation MANUAL_ANNOTATION
                        write manual annotation csv where user_matching fails
                        or queries alpha assumptions
  --combine COMBINE     combine IM mediums into one dataframe

```

## Annon

```
python3 annon.py
```
```
positional arguments:
  local_users          remove names from message text, of the users within a
                       conversation
  exterior_users       aggresively remove any name from message text
  locations            remove names from messages of the users within a
                       conversation
  contact_info         remove names from messages of the users within a
                       conversation

optional arguments:
  -h, --help           show this help message and exit
  --data DATA          directory of csv files produced by build.py
  --out_dir OUT_DIR    directory of instant messaging conversations
  --users USERS        a json list of all users
  --gementes GEMENTES  up to date list of all councils within Flanders
  --streets STREETS    up to date list of all actual streets within Flanders

```

## Validate Data Structure

```
python3 validate.py
```
```
  --line_csv LINE_CSV  path to any beta line_csv
  --out_csv OUT_CSV    path to output validation csv for annotation
  --size SIZE          number of samples per error type
```
