# Inventory #

This is a simple program to keep track of an inventory database.
It reads commands from stdin, and updates a database file specified
on the command line.

### Features ###

Extra credit features implemented:

* Sort on quantity works numerically.
* Remove works with a pattern that can be applied to any field
  (or multiple fields)

In addition, multiple values can be updated with only one command (with the
same pattern-matching syntax as works with delete),
and the output can be sorted down to the minutest detail (you can specify
an arbitrary number of fields to sort by, in preferential order).

### Data storage design ###

The database files are composed of JSON objects, separated by newlines:

    {"part-id":"a123","footprint":"dip6","description":"Digital IMU","quantity":4}
    {"part-id":"a124","footprint":"dip6","description":"Digital IMU","quantity":4}

### Protocol design ###

Most communication is done in JSON. To add a part, you must specify all
fields in a JSON object, similar to what appears in the database file.
Additional fields will be stored, for the sake of forward-compatibility,
but queries against unspecified fields (for example, a "cost" field) will
return an error.

The following commands are supported:

    add <full JSON object>
    remove <match pattern>
    change ,match pattern> <modification>
    list [match pattern] [sort specification]


Match patterns are partial JSON objects. All three of the following match the
above-specified part:

    {"part-id":"a123"}
    {"footprint":"dip6"}
    {"part-id":"a123", "footprint":"dip6"}

The empty match pattern, {}, matches everything.

Modifications are basically identical to match patterns. The following
command would change the description of the above-specified part to "This
is a digital IMU with I2C".

     change {"part-id":"a123"} {"description":"This is a digital IMU with I2C"}

Sort specifications are JSON lists of field names, which order the output
preferentially. If, for example, you want to rank by quantity and then by
part number, this sort specification would do it for you:

     ["quantity", "part-id"]

Lists are returned as whitespace-separated fields for readability. They
are separated by `%%\n`s.

Successful requests with no return value will return an `OK\n`.

Warning conditions are prefixed with the string "Warning:", and Errors are
prefixed with the string "Error:".

