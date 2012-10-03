#!/usr/bin/env python2 
# The data files are newline-separated JSON objects representing each part,
#   like this:
# {"part-id":"a123","footprint":"dip6",description":"Digital IMU","quantity":4}

# Supported commands are:
#   add <full JSON object>
#   remove <match pattern>
#   change <match pattern> <modification>
#   list [match pattern] [sort specification]

# Match patterns are partial JSON objects. All three of the following match the
#   above-specified part:
#     {"part-id":"a123"}
#     {"footprint":"dip6"}
#     {"part-id":"a123", "footprint":"dip6"}
#   The empty match pattern, {}, matches everything.

# Modifications are basically identical to match patterns. The following
#   command would change the description of the above-specified part to "This
#   is a digital IMU with I2C".
#     change {"part-id":"a123"} {"description":"This is a digital IMU with I2C"}

# Sort specifications are JSON lists of field names, which order the output
#   preferentially. If, for example, you want to rank by quantity and then by
#   part number, this sort specification would do it for you:
#     ["quantity", "part-id"]

import json
import argparse
import tempfile
import shutil
import os
import sys

def validate(part):
  for key in ["part-id", "footprint", "description", "quantity"]:
    if not (key in part):
      raise ValueError

  return True

def validatePattern(pattern):
  for key in pattern.iterkeys():
    if not key in ["part-id", "footprint", "description", "quantity"]:
      raise ValueError

  return True

def match(pattern, part):
  for key, val in pattern.iteritems():
    if part[key] != pattern[key]:
      return False
  
  return True

def parts(name):
  """ Iterate over the file provided by the 'name' argument, and return
  the objects that the JSON parser gets out of them."""

  try:
    database = open(name, 'r')
  except IOError:
    database = []

  for line in database:
    try:
      record = json.loads(line)
      if not validate(record):
        raise ValueError
      yield record
    except ValueError:
      print >> sys.stderr, "Invalid record: " + line

def writeout(iterator, filename):
  """Writes the values yielded by the 'iterator' argument to the file
  specified by the 'filename' argument, in JSON format."""

  buf = tempfile.NamedTemporaryFile('a', delete=False)

  for record in iterator:
    buf.write(json.dumps(record) + "\n")

  buf.flush()
  shutil.move(buf.name, filename)

  buf.close()
  

def add(partDict, filename):
  def addIter(part):
    updated = False
    for record in parts(filename):
      if record["part-id"] == part["part-id"]:
        print >> sys.stderr, "Warning: Part exists. Adding to the total, but you may have meant to 'update'"
        record["quantity"] += part["quantity"]
        updated = True

      yield record

    if not updated:
      yield part

  writeout(addIter(partDict), filename)


def remove(pattern, filename):
  if pattern == {}:
    print "That would delete everything. If you want a new inventory, make a new file."
    return

  removeIter = (record for record in parts(filename) if not match(pattern, record))
  writeout(removeIter, filename)


def replace(newfields, record):
  for key in newfields.iterkeys():
    record[key] = newfields[key]

  return record
  

def update(pattern, newfields, filename):
#  def updateIter(pattern, newfields):
#    for record in parts(filename):
#      if match(pattern, record):
#        yield replace(newfields, record)
#      else:
#        yield record
  updateIter = (replace(newfields, record) if match(pattern, record) else record for record in parts(filename))
  
  writeout(updateIter, filename)

def find(pattern, sort):
  def compare(left, right):
    for index in sort:
      if left[index] < right[index]:
        return -1
    for index in sort:
      if left[index] > right[index]:
        return 1
    return 0

  result = []
  for record in parts(filename):
    if match(pattern, record):
      result.append(record)
  result.sort(cmp=compare)
  return result


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Keep track of a bill of materials.")
  parser.add_argument('-f', dest='filename', default="inventory.json", 
    help="specifies the database file")

  filename = parser.parse_args().filename

  add({"part-id":"a123","footprint":"dip6","description":"A thing","quantity":4}, filename)
  update({"part-id":"a123"}, {"quantity":3, "footprint":"what"}, filename)
