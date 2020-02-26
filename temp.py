from wexpect import spawn
import re
import wexpect

spawn_args = {
    "echo": False
    #"encoding": "utf-8",
    #"codec_errors": "replace"
}

INIT_COMMAND = '<call val="Init"> <option val="none"/> </call>'

REPLY_PATTERNS = [
    re.compile(r'\<{0}.*?\>.+?\<\/{0}\>'.format(t), re.DOTALL)
    for t in [
        "feedback",
        "value",
        "message" # older versions of coqtop wont wrap 'message' inside 'feedback'
    ]
]

#c = spawn("{} -main-channel stdfds {}".format("coqidetop", ""), **spawn_args)
#c.send("Check True. Quit.\n")
#c.expect(wexpect.wexpect_util.EOF)
#print(c.before)

child = spawn('cmd.exe')
child.expect('>')
child.sendline('ls')
child.expect('>')
print(child.before)
child.sendline('exit')
