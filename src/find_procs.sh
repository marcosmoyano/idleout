ps ax -o tty,user,pid,ppid,command | grep "^pts/1" | egrep -v "grep"
