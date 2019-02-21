# BracketsTransform

## Introduction

This is a package for SublimeText3 to transform brackets.
It contains three type of operations:
  1. Transform the parentheses that contain the cursor's position.
  2. Remove the pair of parentheses that contain the cursor and are closest to the cursor, and then select the contents of the parentheses.
  3. Select a pair of parentheses and their contents as a whole for your convenience.
All the three commands support the simultaneous operation of multiple cursors.

## Custom Key bindings
Go `Preferences>Package` Settings find this package's settings, select Key bindings.
```json
[
  { "keys": ["ctrl+alt+9"], "command": "brackets_transform", "args": {"tobe": "("}},
  { "keys": ["ctrl+alt+["], "command": "brackets_transform", "args": {"tobe": "["}},
  { "keys": ["ctrl+alt+b"], "command": "brackets_transform", "args": {"tobe": "{"}},
  { "keys": ["ctrl+alt+."], "command": "brackets_take_off" },
  { "keys": ["ctrl+alt+,"], "command": "brackets_selector"},
]
```

If you are using OSX, please refer to the JSON code above to add your own shortcuts.

## Issue
Go [here](https://github.com/absop/BracketsTransform/issues) to post your issue.