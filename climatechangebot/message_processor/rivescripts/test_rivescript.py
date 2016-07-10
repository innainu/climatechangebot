#!/usr/bin/python

from rivescript import RiveScript

rs = RiveScript()
rs.load_directory(".")
rs.sort_replies()

print """This is a bare minimal example for how to write your own RiveScript bot!

For a more full-fledged example, try running: `l`
This will run the built-in Interactive Mode of the RiveScript library. It has
some more advanced features like supporting JSON for communication with the
bot. See `python rivescript --help` for more info.

Type /quit when you're done to exit this example.
"""

while True:
    msg = raw_input("You> ")
    if msg == '/quit':
        quit()
    reply = rs.reply("localuser", msg)
    print "Bot>", reply