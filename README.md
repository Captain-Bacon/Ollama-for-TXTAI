If anyone at anypoint ever sees this, well....

a) You must be bored
b) You probably don't want to go any further


This is my first public repo, and if it hadn't been such a pain in the butt then I wouldn't have put it up, but perhaps I can help someone spend a little less time on this than I did.

1st - this is not a package, nor will it ever be.  This is just a few files.
2nd - I probably won't (can't?!) answer questions.  I'm a code muppet.
3rd - this is a HACK.  It's hideous, hideous code.


If you really REALLY want to try it out then:
clone the gh repo for txt ai
install ollama

in the root folder of the txtai repo run
'''pip install -e .'''
this will install the repo from your local machine, the '-e' allows the files to be editable rather than static taken at the point of the build/install.  Now when you make changes to the files then it will take those and use them rather than a PyPi version.


Inside the repo you'll find a folder called src/piplines/llm or similar.
the ollama.py, generation.py and llm.py in this repo replace these files.  If you don't back them up or know how to revert then you shouldn't be doing this.  Fair warning.

T'other script is a basic gradio app.  I thought that would be easy.  IT ISN'T!  UI's SUCK.  Which is annoying 'cos I really really need some ;-(

So, proceed at your own peril.  But, FWIW, it seems to be working great for me.
