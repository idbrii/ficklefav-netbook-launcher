
scratch:
	javac Scratch.java && echo build success && java -cp . Scratch

clj:
	clojure reorganize.clj

README.html:	README.rst
	rst2html README.rst > README.html

.PHONEY: scratch clj
