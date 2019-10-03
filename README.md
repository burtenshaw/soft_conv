# teen_conv

### Preprocessing 

To build an anonymous json file run:

Define the source of messages with `--data` and the type of platform with `--platfiorm`.

Data should be structured: 

```
--- #DATA_DIR#/
    --- school_name/
        --- instant_messagin_text_file.txt
        --- instant_messagin_text_file.txt
        --- instant_messagin_text_file.txt
        --- instant_messagin_text_file.txt
        --- instant_messagin_text_file.txt
    --- school_name/
    --- school_name/
    --- school_name/
    --- school_name/

```
**Whatsapp**
```python3 annon_schools_data.py --data #DATA_DIR# --type wa```

**Facebook**
```python3 annon_schools_data.py --data #DATA_DIR# --type fb```

