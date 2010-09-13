
scratch:
	javac Scratch.java && echo build success && java -cp . Scratch

clj:
	clojure reorganize.clj

.PHONEY: scratch clj
